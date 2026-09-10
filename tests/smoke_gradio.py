"""Run with Gradio 5.50.0 installed; model libraries are mocked."""
import asyncio
import importlib.util
from pathlib import Path
import sys
from unittest.mock import MagicMock, patch

import gradio as gr
from fastapi.testclient import TestClient

with patch.dict(sys.modules, {name: MagicMock() for name in ('torch', 'transformers')}):
    spec = importlib.util.spec_from_file_location('translation_app', Path(__file__).resolve().parents[1] / 'app' / 'app.py')
    app = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app)

demo = app.create_interface()
with TestClient(gr.routes.App.create_app(demo)) as client:
    config = client.get('/config')
    assert config.status_code == 200
    endpoint = next(d for d in config.json()['dependencies'] if d['api_name'] == 'translate')
    assert len(endpoint['inputs']) == 14
    assert len(endpoint['outputs']) == 2
    schema = client.get('/gradio_api/info')
    assert schema.status_code == 200
    assert '/translate' in schema.json()['named_endpoints']
    routes = client.get('/openapi.json').json()['paths']
    assert '/gradio_api/call/{api_name}' in routes
    assert '/gradio_api/call/{api_name}/{event_id}' in routes

result = asyncio.run(demo.process_api(
    endpoint['id'],
    ['', '英语 (English)', '中文 (Chinese)', 'tencent/Hy-MT2-1.8B',
     'basic', '', '', '', '', 'JSON', 0.7, 0.6, 20, 1.05],
))
assert result['data'] == ['Please enter text to translate.', 'Ready. Enter text to translate.']
demo.close()
print('Gradio interface, named API schema, curl routes, and blank request passed.')
