import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import build
import build_publication
import check_publication

class PublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory=tempfile.TemporaryDirectory()
        cls.out=Path(cls.directory.name)/'site'
        cls.result=build_publication.materialise(cls.out)

    @classmethod
    def tearDownClass(cls):cls.directory.cleanup()

    def test_each_bundle_has_a_distinct_source_linked_worked_example(self):
        descriptors=set();questions=set()
        for name in ('core','domain','control'):
            data=json.loads((self.out/'walkthrough'/f'{name}-evidence.json').read_bytes())
            case=data['case'];descriptors.add(case['descriptor']);questions.add(case['title'])
            self.assertTrue(case['answer']);self.assertGreaterEqual(len(case['negative_controls']),3)
            self.assertGreaterEqual(len(data['records']),6)
            self.assertEqual(data['descriptor_sha256'],build.digest((self.out/case['descriptor']).read_bytes()))
            page=(self.out/'walkthrough'/f'{name}.html').read_text()
            self.assertIn('Open this bundle and record in OKF Explorer',page)
            self.assertIn('What the evidence does not establish',page)
            self.assertIn(f'{name}-mobile.svg',page)
            for record in data['records']:
                self.assertEqual(record['source_sha256'],build.digest((self.out/record['source_path']).read_bytes()))
        self.assertEqual(len(descriptors),3);self.assertEqual(len(questions),3)

    def test_manifest_covers_the_exact_publication(self):
        manifest=json.loads((self.out/'checksums.json').read_bytes())['files']
        actual={p.relative_to(self.out).as_posix() for p in self.out.rglob('*') if p.is_file()}
        self.assertEqual(set(manifest)|{'checksums.json'},actual)
        for name,row in manifest.items():
            raw=(self.out/name).read_bytes()
            self.assertEqual(row,{'sha256':build.digest(raw),'bytes':len(raw)})

    def test_control_keeps_its_version_and_empty_encoded_relationships(self):
        control=json.loads((self.out/'baseline/okf-bundle.json').read_bytes())
        self.assertEqual(control['okf_version'],'0.2')
        self.assertEqual(control['corpora']['ey-rehearsal']['relationships'],[])
        current=json.loads((self.out/'bundle/okf-bundle.json').read_bytes())
        self.assertEqual(current['okf_version'],'0.3')
        self.assertEqual(len(current['corpora']['ey-rehearsal']['relationships']),23)
        compatibility=json.loads((self.out/'baseline/control-explorer.json').read_bytes())
        for key in ('bundle_id','version','snapshot','historical_source'):compatibility.pop(key)
        self.assertEqual(compatibility,control)

    def test_published_source_and_content_licence_are_preserved(self):
        self.assertEqual((self.out/'bundle/LICENSE-CONTENT.md').read_bytes(),(build.ROOT/'LICENSE.md').read_bytes())
        self.assertIn('historical-control',json.loads((self.out/'okf.publication.json').read_bytes())['logical_bundles'][2]['id'])
        self.assertIn('CC BY-NC 4.0',(self.out/'llms.txt').read_text())

    def test_promoter_rejects_a_different_source_revision(self):
        self.assertEqual(check_publication.check(self.out)['status'],'passed')
        with self.assertRaises(ValueError):check_publication.check(self.out,'0'*40)

    def test_promoter_rejects_changed_public_bytes(self):
        import shutil
        with tempfile.TemporaryDirectory() as directory:
            candidate=Path(directory)/'site';shutil.copytree(self.out,candidate)
            (candidate/'walkthrough/domain-evidence.json').write_text('{}\n')
            with self.assertRaises(ValueError):check_publication.check(candidate)

if __name__=='__main__':unittest.main()
