# Hy-MT2 Pinokio

**Hy-MT2** — A Gradio web interface for Tencent's Hy-MT2 translation models, packaged for Pinokio.

Repository: [Tencent-HY-MT2-Pinokio](https://github.com/PierrunoYT/Tencent-HY-MT2-Pinokio)

## Overview

Hy-MT2 is a family of fast-thinking multilingual translation models. This launcher supports:

- **Hy-MT2-1.8B**: Lightweight model for edge devices and real-time translation
- **Hy-MT2-7B**: Higher-accuracy model for complex translation tasks
- **Hy-MT2-30B-A3B**: MoE flagship model (30B total, 3B active per token) for best quality

Both models support mutual translation across **33 languages** with instruction-following modes such as terminology, style, contextual (background), and delimiter preservation.

## Features

- **33 Languages**: Chinese, English, French, Spanish, Japanese, Korean, and 27 more
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
uv pip install -r requirements.txt
```

3. **Run the interface**:

```bash
cd app
python app.py
```

4. **Access the interface** at `http://127.0.0.1:7860`

## Usage

### Basic Translation

1. Select **source language** and **target language**
2. Choose a **model** (1.8B or 7B)
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
- PyTorch 2.0+
- CUDA-capable GPU (recommended)
  - **Hy-MT2-1.8B**: ~4 GB VRAM (BF16)
  - **Hy-MT2-7B**: ~16 GB VRAM (BF16)
  - **Hy-MT2-30B-A3B**: ~24 GB+ VRAM (BF16, MoE with 3B active per token)
- Transformers 5.6.0+
- Gradio 5.0+

## Command Line Options

```bash
cd app
python app.py --help
```

Options:

- `--share`: Create a public Gradio link
- `--server-name`: Server hostname (default: 127.0.0.1)
- `--server-port`: Server port (default: 7860)

## Pinokio Commands

- **Install**: Sets up the Python environment and installs dependencies
- **Start**: Launches the Gradio web interface
- **Update**: Pulls the latest launcher changes
- **Reset**: Removes the virtual environment
- **Save Disk Space**: Deduplicates redundant library files

## API

The Gradio web interface exposes a standard REST API on the same port (default `http://127.0.0.1:7860`).

### Translate — `POST /run/predict`

**Curl**

```bash
curl -X POST http://127.0.0.1:7860/run/predict \
  -H "Content-Type: application/json" \
  -d '{
    "fn_index": 2,
    "data": [
      "Hello, how are you?",
      "英语 (English)",
      "中文 (Chinese)",
      "tencent/Hy-MT2-1.8B",
      "basic",
      "",
      "",
      "",
      "",
      "JSON",
      0.7,
      0.6,
      20,
      1.05
    ]
  }'
```

**Python**

```python
import requests

response = requests.post(
    "http://127.0.0.1:7860/run/predict",
    json={
        "fn_index": 2,
        "data": [
            "Hello, how are you?",   # source_text
            "英语 (English)",          # source_language
            "中文 (Chinese)",          # target_language
            "tencent/Hy-MT2-1.8B",   # model_choice
            "basic",                  # translation_mode
            "",                       # terminology
            "",                       # context
            "",                       # target_style
            "",                       # preferences
            "JSON",                   # format_type
            0.7,                      # temperature
            0.6,                      # top_p
            20,                       # top_k
            1.05,                     # repetition_penalty
        ],
    },
)
translation, status = response.json()["data"]
print(translation)
```

**JavaScript**

```javascript
const response = await fetch("http://127.0.0.1:7860/run/predict", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    fn_index: 2,
    data: [
      "Hello, how are you?",  // source_text
      "英语 (English)",         // source_language
      "中文 (Chinese)",         // target_language
      "tencent/Hy-MT2-1.8B",  // model_choice
      "basic",                 // translation_mode
      "",                      // terminology
      "",                      // context
      "",                      // target_style
      "",                      // preferences
      "JSON",                  // format_type
      0.7,                     // temperature
      0.6,                     // top_p
      20,                      // top_k
      1.05,                    // repetition_penalty
    ],
  }),
});
const { data } = await response.json();
const [translation, status] = data;
console.log(translation);
```

The response `data` array contains `[translation_text, status_message]`.

For the full interactive API schema, visit `http://127.0.0.1:7860/?view=api` while the app is running.

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
