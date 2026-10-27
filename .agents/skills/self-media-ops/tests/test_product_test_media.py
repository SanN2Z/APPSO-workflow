from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / 'scripts/validate_content_package.py'
SPEC = importlib.util.spec_from_file_location('product_media_validator', SOURCE)
VALIDATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATOR
SPEC.loader.exec_module(VALIDATOR)
ROOT = Path(__file__).resolve().parents[4]


class ProductTestMediaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.package = Path(self.temp.name)
        (self.package / 'research').mkdir()
        (self.package / 'assets').mkdir()
        (self.package / 'research/task.json').write_text(
            '{"task_id":"test-task","prompt":"A short scene","status":"success"}',
            encoding='utf-8',
        )
        (self.package / 'research/cost.csv').write_text('case,credits\nscene,100\n')
        (self.package / 'research/plot.py').write_text('# Cost chart renderer\n')
        self.native = self.asset('assets/frame.png', 'source_original', 'ai_generated')
        self.native.update(
            source_original_kind='product_test_output', original_pixels_preserved=True,
            generator='Target official CLI', model='Target model',
            generated_on='2026-10-27', input_assets=[],
            generation_record='research/task.json',
        )
        self.chart = self.asset('assets/cost.png', 'infographic', 'data_visualization')
        self.chart.update(data_source='research/cost.csv', render_script='research/plot.py')

    @staticmethod
    def asset(file, route, source_type):
        return dict(
            file=file, used_in_draft=True, visual_route=route, source_type=source_type,
            source='Actual task or recorded data', creator_or_rightsholder='Test owner',
            obtained_on='2026-10-27', modifications='Original output or chart',
            rights_status='project_owned', allowed_platforms=['wechat'],
            attribution='AI generated or author chart, as applicable',
        )

    def validate(self, assets=None, adapter='generic'):
        return VALIDATOR.validate_manifest_assets(
            self.package, assets if assets is not None else [self.native, self.chart],
            3, 'ready', 'wechat', {'assets/frame.png', 'assets/cost.png'}, adapter, None,
        )[0]

    def test_native_output_and_data_chart_are_two_valid_routes(self):
        self.assertEqual([], self.validate())

    def test_native_output_requires_its_actual_generation_record(self):
        (self.package / 'research/task.json').unlink()
        self.assertTrue(any('generation_record' in issue for issue in self.validate()))

    def test_native_output_keeps_ai_model_provenance(self):
        del self.native['model']
        self.assertTrue(any('model' in issue for issue in self.validate()))

    def test_official_original_still_rejects_ai_redraw(self):
        self.native.update(source_original_kind='official_original', source_url='https://example.com/image')
        self.assertTrue(any('cannot be AI-generated or redrawn' in issue for issue in self.validate()))

    def test_native_input_rights_remain_required(self):
        reference = self.asset('assets/input.png', None, 'user_attachment')
        reference.update(used_in_draft=False, rights_status='pending')
        self.native['input_assets'] = ['assets/input.png']
        self.assertTrue(any('not cleared for derivative use' in issue for issue in self.validate([self.native, self.chart, reference])))

    def test_native_release_rights_and_platform_remain_required(self):
        self.native.update(rights_status='pending', allowed_platforms=['x'])
        errors = self.validate()
        self.assertTrue(any('not release-cleared' in issue for issue in errors))
        self.assertTrue(any('does not allow platform wechat' in issue for issue in errors))

    def test_single_native_route_does_not_bypass_visual_diversity(self):
        self.assertTrue(any('at least two distinct visual_route' in issue for issue in self.validate([self.native])))

    def test_data_chart_needs_data_and_renderer(self):
        self.chart.update(data_source='research/missing.csv', render_script='../plot.py')
        errors = self.validate()
        self.assertTrue(any('data_source' in issue for issue in errors))
        self.assertTrue(any('render_script' in issue for issue in errors))

    def test_ai_picture_cannot_be_called_a_data_chart(self):
        self.chart['ai_generated'] = True
        self.assertTrue(any('not AI-generated' in issue for issue in self.validate()))

    def test_appsso_data_chart_keeps_registered_logo_requirement(self):
        self.assertTrue(any('registered APPSO Logo' in issue for issue in self.validate(adapter='appsso')))
        logo_path = 'APPSO-数字资产/01-栏目与品牌/品牌视觉/原始资料/APPSO Logo 红底白字.png'
        (self.package / 'assets/logo.png').write_bytes((ROOT / logo_path).read_bytes())
        logo = self.asset('assets/logo.png', None, 'brand_asset')
        logo['used_in_draft'] = False
        self.chart['input_assets'] = ['assets/logo.png']
        self.assertEqual([], self.validate([self.native, self.chart, logo], adapter='appsso'))


if __name__ == '__main__':
    unittest.main()
