import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'

class ShellTools(unittest.TestCase):
    def test_alias_variables_work_and_conflicts_fail_before_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); repo = root / 'repo'; repo.mkdir()
            env = {k: v for k, v in os.environ.items() if not k.startswith(('SPECPREP_', 'SPEC_PREP_'))}
            env.update(SPEC_PREP_AUTHOR='Alias Owner', SPEC_PREP_MODEL='alias-model', SPEC_PREP_EVALS=str(root/'evals'))
            cp = subprocess.run(['bash', str(SCRIPTS/'spec-prep-scaffold.sh'), 'Alias Project', str(repo)], env=env, capture_output=True, text=True)
            self.assertEqual(cp.returncode, 0, cp.stderr)
            self.assertIn('Alias Owner', (repo/'docs/specs/alias-project/intent.md').read_text())
            other = root / 'other'; other.mkdir()
            env['SPECPREP_AUTHOR'] = 'Different Owner'
            cp = subprocess.run(['bash', str(SCRIPTS/'spec-prep-scaffold.sh'), 'Another Project', str(other)], env=env, capture_output=True, text=True)
            self.assertNotEqual(cp.returncode, 0)
            self.assertIn('conflicting', cp.stderr)
            self.assertEqual(list(other.iterdir()), [])

    def test_scaffold_uses_shell_safe_environment_and_preserves_instructions(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);repo=root/'repo';repo.mkdir();evals=root/'evals'
            (repo/'AGENTS.md').write_text('Existing operator instructions.\n')
            env=os.environ.copy();env.update(SPECPREP_AUTHOR='Test Owner',SPECPREP_MODEL='test-model',
                                            SPECPREP_EVALS=str(evals),SPECPREP_LAYOUT='docs')
            cp=subprocess.run(['bash',str(SCRIPTS/'spec-prep-scaffold.sh'),'Test Project',str(repo)],env=env,capture_output=True,text=True)
            self.assertEqual(cp.returncode,0,cp.stderr)
            text=(repo/'docs/specs/test-project/intent.md').read_text()
            self.assertIn('author: Test Owner',text);self.assertIn('model: test-model',text)
            self.assertTrue((evals/'evals.md').is_file())
            self.assertEqual((repo/'AGENTS.md').read_text(),'Existing operator instructions.\n')

    def test_scaffold_rejects_in_tree_evals_before_artifact_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            repo=Path(temp)
            env=os.environ.copy();env.update(SPECPREP_EVALS=str(repo/'evals'),SPECPREP_LAYOUT='docs')
            cp=subprocess.run(['bash',str(SCRIPTS/'spec-prep-scaffold.sh'),'Test Project',str(repo)],env=env,capture_output=True,text=True)
            self.assertNotEqual(cp.returncode,0)
            self.assertIn('outside the build root',cp.stderr)
            self.assertFalse((repo/'docs').exists());self.assertFalse((repo/'evals').exists())

    def test_revive_reads_flat_standing_without_frontmatter(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/'standing.md').write_text('# Standing\nNext: export the existing report.\n')
            (root/'ledger.md').write_text('## 0001 decision\nPreserve the original report.\n')
            cp=subprocess.run(['bash',str(SCRIPTS/'spec-prep-revive.sh'),str(root)],capture_output=True,text=True)
            self.assertEqual(cp.returncode,0,cp.stderr)
            self.assertIn('Next: export the existing report.',cp.stdout)

if __name__=='__main__':unittest.main()
