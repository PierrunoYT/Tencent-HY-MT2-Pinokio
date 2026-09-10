# Hy-MT2 Pinokio

**Hy-MT2** — A Gradio web interface for Tencent's Hy-MT2 translation models, packaged for Pinokio.

Repository: [Tencent-HY-MT2-Pinokio](https://github.com/PierrunoYT/Tencent-HY-MT2-Pinokio)

## Overview

Hy-MT2 is a family of fast-thinking multilingual translation models. This launcher supports:

- **Hy-MT2-1.8B**: Lightweight model for edge devices and real-time translation
- **Hy-MT2-7B**: Higher-accuracy model for complex translation tasks
- **Hy-MT2-30B-A3B**: MoE flagship model (30B total, 3B active per token) for best quality

All three models support multilingual translation; the interface offers **38 language and variant choices** with instruction-following modes such as terminology, style, contextual (background), and delimiter preservation.

## Features

- **38 language and variant choices**: including Traditional Chinese and Cantonese
- **Translation Modes** (all seven official Hy-MT2 task types):
  - **Basic**: Default translation
  - **Terminology**: Translation with custom terminology guide
  - **Style**: Translation with a target style (formal, casual, etc.)
  - **Personalization**: Translation with numbered user preferences
  - **Delimiters**: Preserve delimiter symbols in the output
  - **Structured Data**: Translate user-facing text in JSON/YAML/XML/etc. while preserving structure
  - **Contextual**: Translation with background information
- **Model Selection**: Choose between 1.8B (fastest), 7B (balanced), or 30B-A3B MoE (best quality)
- **Customizable Parameters**: Temperature, top-p, top-k, and repetition penalty
- **Web Interface**: Gradio UI accessible via browser

## Installation

### Using Pinokio

1. **Install** the app through Pinokio
2. Click **Start** to launch the Gradio interface
3. Open the web UI from the Pinokio interface

### Manual Installation

1. **Clone or download this repository**

2. **Install dependencies** (from the `app` folder):

```bash
cd app
uv venv env
uv pip install --python env/Scripts/python.exe torch==2.7.0 -r requirements.txt
```

The command above is for Windows. On Linux/macOS, use `env/bin/python` instead of `env/Scripts/python.exe`. For GPU support, install the appropriate PyTorch build for your hardware first, as shown in [PyTorch installation instructions](https://pytorch.org/get-started/locally/). The Pinokio installer selects its backend automatically.

3. **Run the interface** from the same `app` folder:

```bash
env/Scripts/python.exe app.py
```

On Linux/macOS, run `env/bin/python app.py`. Open the local URL printed in the terminal (the first available port starting at 7860).

## Usage

### Basic Translation

1. Select **source language** and **target language**
2. Choose a **model** (1.8B, 7B, or 30B-A3B)
3. Enter text in **Source Text**
4. Click **Translate**

### Terminology Mode

1. Select **terminology** from Translation Mode
2. Enter terminology guide, e.g. `AI -> 人工智能` (one pair per line)
3. Enter your text and click **Translate**

### Style Mode

1. Select **style** from Translation Mode
2. Enter a target style, e.g. `formal` or `literary`
3. Enter your text and click **Translate**

### Contextual Mode

1. Select **contextual** from Translation Mode
2. Enter background information that helps disambiguate the source text
3. Enter your text and click **Translate**

### Personalization Mode

1. Select **personalization** from Translation Mode
2. Enter one preference per line (e.g. `Use concise wording`)
3. Enter your text and click **Translate**

### Structured Data Mode

1. Select **structured_data** from Translation Mode
2. Choose the format type (JSON, YAML, XML, etc.)
3. Paste structured content in **Source Text**
4. Click **Translate**

### Delimiters Mode

1. Select **delimiters** from Translation Mode
2. Enter text containing delimiter symbols to preserve
3. Click **Translate**

## Supported Languages

| Language | Code | Language | Code |
|----------|------|----------|------|
| Chinese | zh | English | en |
| French | fr | Portuguese | pt |
| Spanish | es | Japanese | ja |
| Turkish | tr | Russian | ru |
| Arabic | ar | Korean | ko |
| Thai | th | Italian | it |
| German | de | Vietnamese | vi |
| Malay | ms | Indonesian | id |
| Filipino | tl | Hindi | hi |
| Traditional Chinese | zh-Hant | Polish | pl |
| Czech | cs | Dutch | nl |
| Khmer | km | Burmese | my |
| Persian | fa | Gujarati | gu |
| Urdu | ur | Telugu | te |
| Marathi | mr | Hebrew | he |
| Bengali | bn | Tamil | ta |
| Ukrainian | uk | Tibetan | bo |
| Kazakh | kk | Mongolian | mn |
| Uyghur | ug | Cantonese | yue |

## Model Links

- **Hy-MT2-1.8B**: [Hugging Face](https://huggingface.co/tencent/Hy-MT2-1.8B)
- **Hy-MT2-7B**: [Hugging Face](https://huggingface.co/tencent/Hy-MT2-7B)
- **Hy-MT2-30B-A3B**: [Hugging Face](https://huggingface.co/tencent/Hy-MT2-30B-A3B)

Models are downloaded automatically from Hugging Face on first use.

## Generation Parameters

Recommended parameters (pre-set in the interface; sliders auto-update when you change model):

**Hy-MT2-1.8B / Hy-MT2-7B**

- **Temperature**: 0.7
- **Top-p**: 0.6
- **Top-k**: 20
- **Repetition Penalty**: 1.05
- **Max tokens**: 4096

**Hy-MT2-30B-A3B (MoE)**

- **Temperature**: 0.7
- **Top-p**: 1.0
- **Top-k**: -1 (disabled)
- **Repetition Penalty**: 1.0
- **Max tokens**: 4096

## Requirements

- Python 3.10+
- PyTorch 2.7.0 (installed by the launcher)
- CUDA-capable GPU (recommended)
  - **Hy-MT2-1.8B**: ~4 GB VRAM (BF16)
  - **Hy-MT2-7B**: ~16 GB VRAM (BF16)
  - **Hy-MT2-30B-A3B**: ~60 GB for BF16 weights alone, plus runtime memory; fewer active parameters do not reduce stored weights. CPU offload needs sufficient system RAM
- Transformers 5.6.0+
- Gradio 5.50.0
- Windows AMD uses CPU inference; DirectML is not integrated. Intel macOS is unsupported by the required PyTorch version.

## Command Line Options

```bash
cd app
python app.py --help
```

Options:

- `--share`: Create a public Gradio link
- `--server-name`: Server hostname (default: 127.0.0.1)
- `--server-port`: Server port (default: first available starting at 7860)

## Pinokio Commands

- **Install**: Sets up the Python environment and installs dependencies
- **Start**: Launches the Gradio web interface
- **Update**: Pulls the latest launcher changes with a fast-forward merge and reruns dependency installation
- **Reset**: Removes the virtual environment
- **Save Disk Space**: Deduplicates redundant library files

## API

Use the named `/translate` endpoint on the URL printed at startup. The following examples assume port 7860. Inputs use the exact language labels shown in the UI, in the order below; output is `[translation_text, status_message]`.

**Python** (install `gradio_client`):

```python
from gradio_client import Client

client = Client("http://127.0.0.1:7860")
translation, status = client.predict(
    "Hello, how are you?", "英语 (English)", "中文 (Chinese)",
    "tencent/Hy-MT2-1.8B", "basic",
    "", "", "", "",  # terminology, context, target_style, preferences
    "JSON", 0.7, 0.6, 20, 1.05,
    api_name="/translate",
)
print(translation)
```

**JavaScript** (install `@gradio/client`):

```javascript
import { Client } from "@gradio/client";

const client = await Client.connect("http://127.0.0.1:7860");
const result = await client.predict("/translate", [
  "Hello, how are you?", "英语 (English)", "中文 (Chinese)",
  "tencent/Hy-MT2-1.8B", "basic",
  "", "", "", "", // terminology, context, target_style, preferences
  "JSON", 0.7, 0.6, 20, 1.05,
]);
const [translation, status] = result.data;
console.log(translation);
```

**Curl** (Bash syntax; use `curl.exe` and adapt quoting in PowerShell):

```bash
curl -X POST http://127.0.0.1:7860/gradio_api/call/translate \
  -H "Content-Type: application/json" \
  -d '{"data":["Hello, how are you?","英语 (English)","中文 (Chinese)","tencent/Hy-MT2-1.8B","basic","","","","","JSON",0.7,0.6,20,1.05]}'
```

Copy the returned `event_id`, then retrieve the event stream:

```bash
curl -N http://127.0.0.1:7860/gradio_api/call/translate/EVENT_ID
```

The `complete` event contains the two output values. See the app's **Use via API** footer link for its live schema and the [Gradio curl guide](https://www.gradio.app/guides/querying-gradio-apps-with-curl) for event handling.

## Development checks

```bash
python -m unittest discover -s app -p test_app.py -v
node --test tests/launchers.test.js
```

These regression tests use mocked model dependencies; they do not download weights or validate GPU translation quality.

With Gradio 5.50.0 installed, run `python tests/smoke_gradio.py` to check interface construction, the API schema, curl routes, and a blank request against real Gradio.
## Notes

- First translation may take longer while the model downloads and loads
- GPU is recommended for faster inference
- The 1.8B model is fastest; the 7B model is more accurate for complex text
- The 30B-A3B MoE model offers the best quality but requires substantially more GPU memory
- Prompt templates follow the [official Hy-MT2 documentation](https://huggingface.co/tencent/Hy-MT2-1.8B)

## License

Apache 2.0 — see the model card on Hugging Face.

## References

- [Hy-MT2-1.8B on Hugging Face](https://huggingface.co/tencent/Hy-MT2-1.8B)
- [Hy-MT2 Collection](https://huggingface.co/collections/tencent/hy-mt2)
- [Hy-MT2 Report (arXiv:2605.22064)](https://arxiv.org/abs/2605.22064)

## Contact

For questions about the Hy-MT2 models: hunyuan_opensource@tencent.com
