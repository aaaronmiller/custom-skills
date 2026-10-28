import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import os

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/spec-prep-validate.py'
loader = importlib.util.spec_from_file_location('validator', SCRIPT)
v = importlib.util.module_from_spec(loader)
loader.loader.exec_module(v)


class ValidatorRegressions(unittest.TestCase):
    def test_unbulleted_next_clause_is_not_absorbed(self):
        clauses = v.spec_clauses('**FR-001** [EVAL-001]: MUST count.\n**FR-002** [EVAL-002]: MUST export.\n')
        self.assertEqual(len(clauses), 2)
        self.assertNotIn('FR-002', clauses[0][1])

    def test_duplicate_ids_and_empty_specs_fail_without_padding_small_features(self):
        errors = []
        v.check_fidelity([('FR-001', 'MUST count.')], 'spec.md', errors)
        self.assertEqual(errors, [])
        v.check_fidelity([('FR-001', 'MUST count.'), ('FR-001', 'MUST export.')], 'spec.md', errors)
        self.assertTrue(any('duplicate' in error for error in errors))

    def test_eval_alias_conflict_and_explicit_missing_path(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'feature'; root.mkdir()
            (root.parent / 'evals.md').write_text('EVAL-001')
            with patch.dict(os.environ, {'SPECPREP_EVALS': temp, 'SPEC_PREP_EVALS': temp + '/other'}):
                with self.assertRaises(ValueError):
                    v.find_eval_manifest(root, None)
            with patch.dict(os.environ, {}, clear=True):
                (root.parent / 'feature-evals.md').write_text('EVAL-001')
                self.assertIsNone(v.find_eval_manifest(root, str(root / 'missing.md')))

    def test_eval_mentions_are_not_definitions_and_tables_are_compatible(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'build'; root.mkdir()
            manifest = Path(temp) / 'evals.md'
            clause = [('FR-001', 'FR-001 [EVAL-001] MUST count.')]
            manifest.write_text('A sentence that merely mentions EVAL-001.\n')
            errors = []; v.check_eval_resolution(clause, 'spec.md', root, errors, str(manifest))
            self.assertTrue(errors)
            manifest.write_text('| EVAL-001 | Count exactly one record. |\n')
            errors = []; v.check_eval_resolution(clause, 'spec.md', root, errors, str(manifest))
            self.assertEqual(errors, [])

    def test_no_git_build_boundary_and_explicit_root(self):
        with tempfile.TemporaryDirectory() as temp:
            build = Path(temp); (build / '.specify').mkdir()
            feature = build / 'specs/001-report'; feature.mkdir(parents=True)
            manifest = build / 'evals.md'; manifest.write_text('EVAL-001\n')
            errors = []
            v.check_eval_resolution([('FR-001', '[EVAL-001] MUST count.')], 'spec.md', feature, errors, str(manifest))
            self.assertTrue(any('inside' in error for error in errors))

    def test_help_is_success(self):
        result = subprocess.run([sys.executable, str(SCRIPT), '--help'], capture_output=True)
        self.assertEqual(result.returncode, 0)

    def test_native_story_ids_do_not_poison_harvest(self):
        found = v.harvest_tokens(['Use `US1` and `US12`, plus `React` and WebGPU.'], set())
        self.assertNotIn('us1', found)
        self.assertNotIn('us12', found)
        self.assertIn('react', v.tech_hits('React', v.TECH_TOKENS))
        self.assertIn('webgpu', [t.lower() for t in found])

    def test_wrapped_clause_is_checked(self):
        clauses = v.spec_clauses('- **FR-001** [EVAL-001]: The operator MUST receive\n  a user-friendly result.\n\n### Next\nA comment.\n')
        errors = []
        v.check_testability(clauses, 'spec.md', errors)
        self.assertTrue(any('user-friendly' in e for e in errors))
        self.assertNotIn('### Next', clauses[0][1])

    def test_continuity_accepts_declared_flat_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'project'; root.mkdir()
            (root / 'intent.md').write_text('# Intent\nThe operator can export a report.\n')
            spec = '# Contract\n' + '\n'.join(f'- **FR-{i:03d}** [EVAL-{i:03d}]: The system MUST return exactly {i} records.' for i in range(1, 9))
            (root / 'spec.md').write_text(spec)
            (root / 'plan.md').write_text('# Derived plan\n'+'\n'.join(f'FR-{i:03d}: counted export response.' for i in range(1,9)))
            (root / 'substrate.md').write_text('## Declared level\nS2. Agent drafts and human reviews.\n')
            for name in ('ledger.md','standing.md'):
                (root/name).write_text('The export contract has been prepared and verified; implementation has not started.\n')
            evals=Path(temp)/'evals.md';evals.write_text('\n'.join(f'EVAL-{i:03d}' for i in range(1,9)))
            result=subprocess.run([sys.executable,str(SCRIPT),str(root),'--evals',str(evals)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_divergent_continuity_aliases_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'ledger').mkdir()
            (root/'ledger.md').write_text('flat authority with substantial but conflicting current evidence')
            (root/'ledger/ledger.md').write_text('nested authority with different substantial evidence and next action')
            result=subprocess.run([sys.executable,str(SCRIPT),str(root)],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('disagree',result.stdout)

    def test_in_tree_eval_is_still_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);manifest=root/'evals.md';manifest.write_text('EVAL-001')
            errors=[]
            v.check_eval_resolution([('FR-001','- FR-001 [EVAL-001]: MUST count.')],'spec.md',root,errors,str(manifest))
            self.assertTrue(any('inside the repository' in e for e in errors))


if __name__ == '__main__':
    unittest.main()
