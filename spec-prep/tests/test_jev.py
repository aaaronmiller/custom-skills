import copy
import importlib.util
import json
import math
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/spec-prep-jev.py'
loader=importlib.util.spec_from_file_location('jev',SCRIPT)
j=importlib.util.module_from_spec(loader);loader.loader.exec_module(j)


class JevContract(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'skill';self.root.mkdir()
        (self.root/'SKILL.md').write_text('# Skill\nOnly prepare; do not implement.\n')
        self.packet={'schemaVersion':1,'sources':[{'id':'rule','path':'SKILL.md'}],
                     'checks':[{'id':'boundary','criterion':'Preparation stops before implementation.','sourceIds':['rule']}]}
        self.request,self.fps=j.build_request(self.root,'skill','governance',self.packet)
        self.response={'model':'jev-1.13','answers':{'boundary':{'type':'choice','choice':'supported',
                       'probabilities':{'supported':0.9,'needs_review':0.05,'abstain':0.05},'confidence':0.9}},
                       'usage':{'input_tokens':20,'output_tokens':5}}

    def test_supported_is_advice_with_no_gate_effect(self):
        result=j.interpret(self.request,self.response,0.8)
        self.assertEqual(result['status'],'advisory')
        self.assertEqual(result['gateEffect'],'none')
        self.assertTrue(result['requiresReviewer'])

    def test_low_confidence_and_abstention_require_review(self):
        response=copy.deepcopy(self.response);response['answers']['boundary']['confidence']=0.5
        self.assertEqual(j.interpret(self.request,response,0.8)['status'],'review_required')
        answer=response['answers']['boundary'];answer.update(choice='abstain',confidence=0.9,
                    probabilities={'supported':0.05,'needs_review':0.05,'abstain':0.9})
        self.assertEqual(j.interpret(self.request,response,0.8)['decisions']['boundary']['advice'],'abstained')

    def test_missing_foreign_and_wrong_type_answers_fail(self):
        for mutate in (lambda d:d['answers'].clear(),
                       lambda d:d['answers'].update(other=d['answers']['boundary']),
                       lambda d:d['answers']['boundary'].update(type='noul'),
                       lambda d:d['answers']['boundary'].update(choice='approve')):
            response=copy.deepcopy(self.response);mutate(response)
            with self.assertRaises(ValueError):j.interpret(self.request,response,0.8)

    def test_invalid_probability_distribution_fails(self):
        for value in (True,float('nan'),float('inf'),-0.1,1.1):
            response=copy.deepcopy(self.response);response['answers']['boundary']['confidence']=value
            with self.assertRaises(ValueError):j.interpret(self.request,response,0.8)
        response=copy.deepcopy(self.response)
        response['answers']['boundary']['probabilities']={'supported':0.1,'needs_review':0.8,'abstain':0.1}
        with self.assertRaises(ValueError):j.interpret(self.request,response,0.8)

    def test_outside_root_and_wrong_target_rejected(self):
        other=self.root.parent/'private.md';other.write_text('must not be sent')
        for path in ('../private.md',str(other)):
            packet=copy.deepcopy(self.packet);packet['sources'][0]['path']=path
            with self.assertRaises(ValueError):j.build_request(self.root,'skill','intake',packet)
        (self.root/'outside.md').symlink_to(other)
        packet=copy.deepcopy(self.packet);packet['sources'][0]['path']='outside.md'
        with self.assertRaises(ValueError):j.build_request(self.root,'skill','intake',packet)
        with self.assertRaises(ValueError):j.build_request(self.root.parent,'skill','intake',self.packet)

    def test_duplicate_ids_and_unknown_sources_rejected(self):
        packet=copy.deepcopy(self.packet);packet['checks'].append(packet['checks'][0].copy())
        with self.assertRaises(ValueError):j.build_request(self.root,'skill','intake',packet)
        packet=copy.deepcopy(self.packet);packet['checks'][0]['sourceIds']=['absent']
        with self.assertRaises(ValueError):j.build_request(self.root,'skill','intake',packet)

    def test_wire_contains_typed_questions_and_frozen_source(self):
        self.assertNotIn('messages',self.request)
        self.assertEqual(self.request['model'],'jev-1.13-free')
        self.assertEqual(self.request['questions']['boundary']['type'],'choice')
        self.assertIn('1: # Skill',self.request['state']['sources']['rule']['excerpt'])
        old=self.fps[str(self.root/'SKILL.md')]
        (self.root/'SKILL.md').write_text('# Changed\nNow launch.\n')
        _,fps=j.build_request(self.root,'skill','intake',self.packet)
        self.assertNotEqual(old,fps[str(self.root/'SKILL.md')])

    def test_preview_never_reads_credentials_or_calls_provider(self):
        packet=self.root.parent/'packet.json';packet.write_text(json.dumps(self.packet))
        args=['jev','--root',str(self.root),'--target','skill','--stage','tasks','--packet',str(packet)]
        with patch.object(sys,'argv',args),patch.object(j,'credential',side_effect=AssertionError('credential read')), \
             patch.object(j,'call_once',side_effect=AssertionError('network call')),patch('builtins.print'):
            self.assertEqual(j.main(),0)

    def test_provider_failure_is_single_call_sanitized(self):
        error=urllib.error.HTTPError(j.ENDPOINT,401,'secret must not appear',{},None)
        with patch.object(j,'credential',return_value='secret-key'),patch.object(j.urllib.request,'build_opener') as opener:
            opener.return_value.open.side_effect=error
            response,result=j.call_once(self.request,1)
            self.assertIsNone(response);self.assertEqual(result['status'],'unavailable')
            self.assertEqual(opener.return_value.open.call_count,1)
            self.assertNotIn('secret',json.dumps(result))

    def test_api_request_identifies_its_client(self):
        with patch.object(j,'credential',return_value='unit-test-key'),patch.object(j.urllib.request,'build_opener') as opener:
            opener.return_value.open.return_value.__enter__.return_value.read.return_value=json.dumps(self.response).encode()
            response,error=j.call_once(self.request,1)
            request=opener.return_value.open.call_args.args[0]
            self.assertTrue(request.get_header('User-agent','').startswith('spec-prep/'))
            self.assertEqual(request.get_header('Accept'),'application/json')
            self.assertIsNone(error)

    def test_cloudflare_error_is_classified_without_echoing_body(self):
        body=json.dumps({'error':{'error_code':1010,'error_name':'browser_signature_banned',
                                 'detail':'private-secret-body'}}).encode()
        error=urllib.error.HTTPError(j.ENDPOINT,403,'Forbidden',{},io.BytesIO(body))
        with patch.object(j,'credential',return_value='unit-test-key'),patch.object(j.urllib.request,'build_opener') as opener:
            opener.return_value.open.side_effect=error
            _,result=j.call_once(self.request,1)
            self.assertEqual(result['reason'],'client-signature-rejected')
            self.assertEqual(result['providerErrorCode'],1010)
            self.assertNotIn('private-secret-body',json.dumps(result))
            self.assertEqual(opener.return_value.open.call_count,1)

    def test_expired_key_error_is_distinct_from_edge_failure(self):
        body=json.dumps({'error':{'code':'api_key_expired','message':'private-secret-body'}}).encode()
        error=urllib.error.HTTPError(j.ENDPOINT,401,'Unauthorized',{},io.BytesIO(body))
        with patch.object(j,'credential',return_value='unit-test-key'),patch.object(j.urllib.request,'build_opener') as opener:
            opener.return_value.open.side_effect=error
            _,result=j.call_once(self.request,1)
            self.assertEqual(result['reason'],'credential-expired')
            self.assertNotIn('private-secret-body',json.dumps(result))

    def test_global_bucket_key_precedes_stale_auth_store(self):
        home=Path(self.temp.name)/'home';home.mkdir()
        (home/'.cuddle-bucket').write_text('export OPENCODE_API_KEY="unit-global-key"\n')
        auth=home/'.local/share/opencode';auth.mkdir(parents=True)
        (auth/'auth.json').write_text(json.dumps({'opencode':{'key':'unit-stale-key'}}))
        with patch.dict(os.environ,{},clear=True),patch.object(j.Path,'home',return_value=home):
            self.assertEqual(j.credential(),'unit-global-key')

    def test_explicit_environment_key_keeps_precedence(self):
        home=Path(self.temp.name)/'home';home.mkdir()
        (home/'.cuddle-bucket').write_text('OPENCODE_API_KEY=unit-file-key\n')
        with patch.dict(os.environ,{'OPENCODE_API_KEY':'unit-env-key'},clear=True),patch.object(j.Path,'home',return_value=home):
            self.assertEqual(j.credential(),'unit-env-key')

    def test_bucket_is_data_and_never_shell_execution(self):
        home=Path(self.temp.name)/'home';home.mkdir();marker=home/'executed'
        (home/'.cuddle-bucket').write_text('OPENCODE_API_KEY="$(touch '+str(marker)+')"\nOPENCODE_ZEN_API_KEY=unit-safe-key\n')
        with patch.dict(os.environ,{},clear=True),patch.object(j.Path,'home',return_value=home):
            self.assertEqual(j.credential(),'unit-safe-key')
        self.assertFalse(marker.exists())

    def test_duplicate_json_and_nonfinite_threshold_rejected(self):
        path=self.root.parent/'bad.json';path.write_text('{"x":1,"x":2}')
        with self.assertRaises(ValueError):j.read_json(path)
        with self.assertRaises(ValueError):j.interpret(self.request,self.response,float('nan'))

    def test_source_change_during_call_returns_stale(self):
        packet=self.root.parent/'packet.json';packet.write_text(json.dumps(self.packet))
        args=['jev','--root',str(self.root),'--target','skill','--stage','tasks','--packet',str(packet),'--allow-network']
        def changed(request, timeout):
            (self.root/'SKILL.md').write_text('# Changed after request\n')
            return self.response,None
        with patch.object(sys,'argv',args),patch.object(j,'call_once',side_effect=changed),patch('builtins.print') as output:
            self.assertEqual(j.main(),1)
            result=json.loads(output.call_args.args[0])
            self.assertEqual(result['status'],'stale')
            self.assertEqual(result['gateEffect'],'none')

    def test_output_collision_stops_before_network(self):
        packet=self.root.parent/'packet.json';packet.write_text(json.dumps(self.packet))
        existing=self.root.parent/'evidence.json';existing.write_text('operator work')
        args=['jev','--root',str(self.root),'--target','skill','--stage','output','--packet',str(packet),
              '--allow-network','--report-out',str(existing)]
        with patch.object(sys,'argv',args),patch.object(j,'call_once',side_effect=AssertionError('network')),patch('builtins.print'):
            self.assertEqual(j.main(),2)
        self.assertEqual(existing.read_text(),'operator work')

    def test_oversized_request_is_not_truncated(self):
        packet=copy.deepcopy(self.packet);packet['checks'][0]['criterion']='x'*j.MAX_BYTES
        with self.assertRaises(ValueError):j.build_request(self.root,'skill','intake',packet)


if __name__=='__main__':unittest.main()
