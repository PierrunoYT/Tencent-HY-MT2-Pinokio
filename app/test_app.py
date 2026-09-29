"""Offline regression tests; no model downloads or GPU required."""
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock, patch


with patch.dict(sys.modules, {name: MagicMock() for name in ('gradio', 'torch', 'transformers')}):
    spec = importlib.util.spec_from_file_location('translation_app', Path(__file__).with_name('app.py'))
    app = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app)


class TranslationTests(unittest.TestCase):
    def setUp(self):
        app.model = app.tokenizer = app.model_name = None

    def test_sampling_overrides_inherited_defaults(self):
        for top_k in (-1, 0, 20):
            kwargs = app.build_generation_kwargs(0.7, 1.0, top_k, 1.0)
            self.assertTrue(kwargs['do_sample'])
            self.assertEqual(kwargs['top_k'], max(0, top_k))

    def test_preference_numbering_and_numeric_content(self):
        for count in (1, 3, 10):
            preferences = '\n'.join(f'{i}. Keep term {i}' for i in range(1, count + 1))
            for target, suffix in [('en', '. Translate'), ('zh', '、将')]:
                prompt = app.build_prompt('hello', target, 'fr', 'personalization', preferences=preferences)
                self.assertIn(f'{count + 1}{suffix}', prompt)
        prompt = app.build_prompt('hello', 'en', 'fr', 'personalization', preferences='2026 terminology')
        self.assertIn('1. 2026 terminology', prompt)
        self.assertEqual(app.format_preferences('1.\n2、\n3) Be brief'), ['1、**Be brief**'])

    def test_structured_data_occurs_once(self):
        for target in ('en', 'zh'):
            prompt = app.build_prompt('{"title":"Hello"}', target, 'fr', 'structured_data')
            self.assertEqual(prompt.count('{"title":"Hello"}'), 1)

    def test_invalid_terminology_is_reported(self):
        for text in ('invalid', 'source -> ', 'AI -> IA\nML = AA'):
            with self.assertRaises(ValueError):
                app.format_terminology(text, False)
        self.assertEqual(app.format_terminology('AI -> IA', False), 'AI translates to IA')

    def test_mode_without_required_input_is_rejected_before_load(self):
        with patch.object(app, 'load_model') as loader:
            for mode in ('terminology', 'style', 'personalization', 'contextual'):
                translation, status = app.translate_text(
                    'hello', '英语 (English)', '中文 (Chinese)', next(iter(app.MODELS)),
                    mode, '', ' ', '', '1.', 'JSON', 0.7, 0.6, 20, 1.05,
                )
                self.assertIn(mode, status)
            loader.assert_not_called()

    def test_null_api_inputs_and_validation_errors(self):
        args = [None, '英语 (English)', '中文 (Chinese)', next(iter(app.MODELS)),
                'basic', None, None, None, None, 'JSON', 0.7, 0.6, 20, 1.05]
        self.assertEqual(app.translate_text(*args)[0], 'Please enter text to translate.')
        with patch.object(app, 'load_model', return_value=(MagicMock(), MagicMock())):
            args[0], args[4], args[5] = 'hello', 'terminology', 'bad line'
            translation, status = app.translate_text(*args)
        self.assertNotIn('Traceback', translation)
        self.assertTrue(status.startswith('Invalid input'))

    def test_failed_load_does_not_publish_partial_state(self):
        with patch.object(app.AutoModelForCausalLM, 'from_pretrained', side_effect=RuntimeError('out of memory')):
            with self.assertRaises(RuntimeError):
                app.load_model()
        self.assertIsNone(app.model)
        self.assertIsNone(app.tokenizer)
        self.assertIsNone(app.model_name)

    def test_unknown_model_is_rejected_before_download(self):
        with patch.object(app.AutoTokenizer, 'from_pretrained') as loader:
            with self.assertRaises(ValueError):
                app.load_model('unknown/model')
            loader.assert_not_called()

    def test_cached_model_is_reused(self):
        app.model = MagicMock()
        app.tokenizer = MagicMock()
        app.model_name = next(iter(app.MODELS))
        with patch.object(app.AutoModelForCausalLM, 'from_pretrained') as loader:
            self.assertEqual(app.load_model(app.model_name), (app.model, app.tokenizer))
            loader.assert_not_called()

    def test_unload_collects_before_emptying_cache(self):
        app.model = MagicMock()
        calls = []
        with patch.object(app.gc, 'collect', side_effect=lambda: calls.append('collect')),              patch.object(app.torch.cuda, 'is_available', return_value=True),              patch.object(app.torch.cuda, 'empty_cache', side_effect=lambda: calls.append('empty')):
            app.unload_model()
        self.assertIsNone(app.model)
        self.assertEqual(calls, ['collect', 'empty'])

    def test_cuda_without_bf16_uses_float16(self):
        with patch.object(app.torch.cuda, 'is_available', return_value=True), \
             patch.object(app.torch.cuda, 'is_bf16_supported', return_value=False), \
             patch.object(app.AutoModelForCausalLM, 'from_pretrained') as loader:
            app.load_model()
            self.assertIs(loader.call_args.kwargs['dtype'], app.torch.float16)


if __name__ == '__main__':
    unittest.main()
