import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'media_review.py'
SPEC = importlib.util.spec_from_file_location('media_review', SOURCE)
MEDIA = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MEDIA)


class MediaReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = self.root / 'review.json'
        self.output = self.root / 'review.v2'

    def build(self, data, zipped=True):
        self.manifest.write_text(json.dumps(data), encoding='utf-8')
        return MEDIA.build_review(self.manifest, self.output, zipped)

    def test_image_manifest_resolves_relative_files_and_keeps_distinct_names(self):
        for folder, content in [('a', b'first'), ('b', b'second')]:
            (self.root / folder).mkdir()
            (self.root / folder / 'image.png').write_bytes(content)
        result = self.build({'kind': 'image', 'title': 'A & B', 'items': [{'file': 'a/image.png'}, {'file': 'b/image.png'}]})
        page = Path(result['html']).read_text(encoding='utf-8')
        self.assertIn('A &amp; B', page)
        self.assertEqual(b'first', (self.output / 'assets/image-001.png').read_bytes())
        self.assertEqual(b'second', (self.output / 'assets/image-002.png').read_bytes())
        self.assertNotIn('{{STYLE}}', page)
        with zipfile.ZipFile(result['zip']) as archive:
            self.assertIn('index.html', archive.namelist())
            self.assertIn('assets/image-002.png', archive.namelist())
        self.assertEqual('review.v2.zip', Path(result['zip']).name)

    def test_video_and_process_files_are_copied_without_transcoding(self):
        for name, content in [('clip.mp4', b'original-video'), ('poster.jpg', b'poster'), ('workspace.png', b'whole-workspace')]:
            (self.root / name).write_bytes(content)
        result = self.build({'kind': 'video', 'items': [{'file': 'clip.mp4', 'poster': 'poster.jpg', 'spec': '18 s'}], 'process_images': [{'file': 'workspace.png', 'caption': 'Full view'}]})
        page = Path(result['html']).read_text(encoding='utf-8')
        self.assertIn('<video controls playsinline', page)
        self.assertIn('assets/poster-001.jpg', page)
        self.assertIn('assets/process-001.png', page)
        self.assertEqual(b'original-video', (self.output / 'assets/video-001.mp4').read_bytes())
        with zipfile.ZipFile(result['zip']) as archive:
            self.assertEqual(b'original-video', archive.read('assets/video-001.mp4'))

    def test_empty_video_template_has_no_fake_player(self):
        result = self.build({'kind': 'video', 'items': []})
        page = Path(result['html']).read_text(encoding='utf-8')
        self.assertNotIn('<video ', page)
        self.assertIn('items', page)

    def test_missing_source_reports_error(self):
        with self.assertRaises(FileNotFoundError):
            self.build({'kind': 'video', 'items': [{'file': 'missing.mp4'}]})

    def test_zip_does_not_include_unlisted_files_from_older_output(self):
        self.output.mkdir()
        (self.output / 'internal-notes.txt').write_text('Not for this review')
        result = self.build({'kind': 'image', 'items': []})
        with zipfile.ZipFile(result['zip']) as archive:
            self.assertNotIn('internal-notes.txt', archive.namelist())


if __name__ == '__main__':
    unittest.main()
