import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/spec-prep-workbench.py'
spec = importlib.util.spec_from_file_location('workbench', SCRIPT)
workbench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(workbench)


class PortableWorkbench(unittest.TestCase):
    def test_relative_bundle_survives_copy_and_preserves_custom_settings(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'original'; intake = root / 'intake'; build = root / 'build'
            intake.mkdir(parents=True); build.mkdir()
            (intake / 'brief.md').write_text('# Report export\n')
            manifest = {'schemaVersion': 1, 'projectId': 'report', 'title': 'Report',
                        'summary': 'Export reports', 'nextOperation': 'specification-preparation',
                        'lifecycle': 'staged', 'assignment': 'assigned',
                        'sources': [{'path': 'brief.md', 'format': 'md', 'role': 'evidence'}],
                        'readOrder': ['brief.md'], 'issues': [], 'relatedProjects': [], 'externalResources': []}
            (intake / 'project-intake.json').write_text(json.dumps(manifest))
            (build / 'intent.md').write_text('# Intent\nExport reports.\n')
            workbench.write_workbench(intake, build_root=build)
            doc = json.loads((intake / 'workbench.json').read_text())
            self.assertEqual(doc['buildRoot'], '../build')
            doc['customSetting'] = {'operator': 'preserve'}
            (intake / 'workbench.json').write_text(json.dumps(doc))
            destination = Path(temp) / 'relocated'
            shutil.copytree(root, destination)
            copied = json.loads((destination/'intake/workbench.json').read_text())
            self.assertEqual(workbench.validate_workbench(destination/'intake', copied), [])
            workbench.write_workbench(destination/'intake', build_root=destination/'build')
            final = json.loads((destination/'intake/workbench.json').read_text())
            self.assertEqual(final['customSetting'], {'operator': 'preserve'})


if __name__ == '__main__':
    unittest.main()
