"""Delivery boundaries: compact inputs, native outputs, governance and reset safety."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), SCRIPTS / name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DeliveryFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.worker = load('spec-prep-delivery.py')
        self.launch = load('spec-prep-launch.py')
        self.doc = {'schemaVersion': 1, 'operation': 'input-handoff',
                    'implementationAuthorized': False, 'workstreams': []}
        self.add_stream('local')

    def write(self, path, text):
        dest = self.root / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text)
        return dest

    def add_stream(self, name):
        prefix = name + '/'
        for filename, text in {
            'inputs/intent.md': '# Intent\nExport complete reports.\n## Source disposition\nUSER-1: preserved.\n',
            'inputs/requirements.md': '# Requirements\nFR-001: MUST export complete reports.\n',
            'inputs/design.md': '# Design\nFR-001: deterministic report serializer.\n',
            '.specify/memory/constitution.md': '# Constitution\nEvidence precedes completion.\n',
            'AGENTS.md': 'Read .specify/memory/constitution.md and reset-handoff.md before changes.\nPreparation only; do not implement.\n',
            'reset-handoff.md': '# Handoff\nPreparation only; implementation not authorized.\nNext: specification preparation.\n',
            'README.md': '# Conversion\nRead inputs/requirements.md and inputs/intent.md for specify; read inputs/design.md, generated spec.md, intent and .specify/memory/constitution.md for plan. Then tasks and analyze. Stop before implementation.\n',
        }.items():
            self.write(prefix + filename, text)
        self.doc['workstreams'].append({
            'id': name, 'buildRoot': name, 'inputRoot': name + '/inputs',
            'inputs': {role: filename for role, filename in
                       [('requirements', 'requirements.md'), ('design', 'design.md'), ('intent', 'intent.md')]},
            'sourceMap': 'intent.md#source-disposition',
            'conversionGuide': 'README.md', 'nextOperation': 'specification-preparation',
            'governance': {'constitution': '.specify/memory/constitution.md',
                           'instructions': 'AGENTS.md', 'handoff': 'reset-handoff.md'},
        })

    def errors(self):
        return self.worker.validate(self.root, self.doc)

    def native(self):
        self.doc['operation'] = 'native-preparation'
        stream = self.doc['workstreams'][0]
        stream.update(featureRoot='specs/001-report', receipt='preparation.json',
                      nextOperation='await-implementation-authorization')
        self.write('local/reset-handoff.md', '# Handoff\nPreparation complete; implementation not authorized.\nNext: await explicit implementation authorization.\n')
        self.write('local/specs/001-report/intent.md', '# Intent\nExport complete reports.\n')
        artifacts = {}
        for role, path in [('spec', 'specs/001-report/spec.md'), ('plan', 'specs/001-report/plan.md'),
                           ('tasks', 'specs/001-report/tasks.md'), ('constitution', '.specify/memory/constitution.md'),
                           ('handoff', 'reset-handoff.md')]:
            target = self.root / 'local' / path
            if role in ('spec', 'plan', 'tasks'):
                target = self.write('local/' + path, '# ' + role + '\n' + ('- [ ] T001 Export report. Gate: exported record count matches the source.\n' if role == 'tasks' else 'Report contract.\n'))
            artifacts[role] = {'path': path, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}
        for path in ['inputs/intent.md', 'inputs/requirements.md', 'inputs/design.md',
                     'specs/001-report/intent.md', 'AGENTS.md', 'README.md']:
            artifacts[path] = {'path': path, 'sha256': hashlib.sha256((self.root/'local'/path).read_bytes()).hexdigest()}
        gates = {}
        for name in ['constitution', 'prerequisites', 'analysis', 'traceability']:
            evidence = 'evidence/' + name + '.md'
            self.write('local/' + evidence, '# Synthetic test fixture\nGate result for validator testing, not a real workflow claim.\n')
            gates[name] = {'status': 'passed', 'command': 'fixture-only', 'observedAt': '2026-10-26', 'evidence': evidence}
        receipt = {'schemaVersion': 1, 'lifecycle': 'specification-prepared', 'implementationAuthorized': False,
                   'skill': {'version': '2.5.1', 'sha256': hashlib.sha256((SCRIPTS.parent/'SKILL.md').read_bytes()).hexdigest()}, 'artifacts': artifacts, 'gates': gates}
        self.write('local/preparation.json', json.dumps(receipt))
        return receipt


class DeliveryBoundary(DeliveryFixture):
    def test_compact_trio_with_governance_and_two_workstreams(self):
        self.add_stream('platform')
        self.assertEqual(self.errors(), [])

    def test_fragmented_core_or_duplicate_authority_is_rejected(self):
        self.doc['workstreams'][0]['inputs']['design'] = 'hardware-profiles.md'
        self.assertTrue(self.errors())

    def test_missing_cli_does_not_make_standalone_a_native_pass(self):
        self.doc['operation'] = 'native-preparation'
        self.assertTrue(self.errors())
        self.doc['operation'] = 'input-handoff'
        self.assertEqual(self.errors(), [])

    def test_input_handoff_cannot_point_straight_to_implementation(self):
        self.doc['workstreams'][0]['nextOperation'] = 'implementation'
        self.assertTrue(self.errors())

    def test_constitution_pointer_is_required(self):
        self.write('local/AGENTS.md', 'Read reset-handoff.md. Preparation only; do not implement.\n')
        self.assertTrue(self.errors())

    def test_missing_source_disposition_heading_is_rejected(self):
        self.doc['workstreams'][0]['sourceMap'] = 'intent.md#missing-heading'
        self.assertTrue(self.errors())

    def test_optional_adapter_must_import_agents(self):
        self.doc['workstreams'][0]['governance']['adapter'] = 'CLAUDE.md'
        self.write('local/CLAUDE.md', '@AGENTS.md\n')
        self.assertEqual(self.errors(), [])
        self.write('local/CLAUDE.md', 'Unrelated instructions.\n')
        self.assertTrue(self.errors())

    def test_safe_native_output_and_receipt(self):
        self.native()
        self.assertEqual(self.errors(), [])

    def test_no_launch_or_checked_task_after_preparation(self):
        self.native()
        self.doc['implementationAuthorized'] = True
        self.assertTrue(self.errors())
        self.doc['implementationAuthorized'] = False
        self.write('local/specs/001-report/tasks.md', '- [x] T001 Implemented.\n')
        self.assertTrue(self.errors())

    def test_unconsented_implement_hook_is_rejected(self):
        self.write('local/.specify/extensions.yml', 'hooks:\n  after_tasks:\n    - command: speckit.implement\n')
        self.assertTrue(self.errors())

    def test_outside_or_symlinked_root_is_rejected(self):
        self.doc['workstreams'][0]['buildRoot'] = '../elsewhere'
        self.assertTrue(self.errors())

    def test_receipt_hash_and_evidence_are_required(self):
        self.native()
        self.write('local/evidence/analysis.md', '')
        self.assertTrue(self.errors())

    def test_incomplete_receipt_cannot_be_native_complete(self):
        receipt = self.native()
        receipt['lifecycle'] = 'specification-reviewed-incomplete'
        self.write('local/preparation.json', json.dumps(receipt))
        self.assertTrue(self.errors())

    def test_changed_consumed_input_invalidates_native_receipt(self):
        self.native()
        self.write('local/inputs/requirements.md', '# Requirements\nChanged behavior.\n')
        self.assertTrue(self.errors())

    def test_legacy_receipt_normalizes_without_mutation(self):
        receipt = self.native()
        legacy = dict(receipt)
        legacy['artifacts'] = list(receipt['artifacts'].values())
        legacy['gates'] = [dict(item, name=name) for name, item in receipt['gates'].items()]
        before = json.dumps(legacy)
        normalized = self.launch.normalize_receipt(legacy)
        self.assertEqual(normalized['artifacts']['spec'], receipt['artifacts']['spec'])
        self.assertEqual(before, json.dumps(legacy))

    def test_ambiguous_legacy_role_is_rejected(self):
        receipt = self.native()
        receipt['artifacts'] = list(receipt['artifacts'].values()) + [{'path': 'other/spec.md', 'sha256': 'a' * 64}]
        with self.assertRaises(ValueError):
            self.launch.normalize_receipt(receipt)


if __name__ == '__main__':
    unittest.main()
