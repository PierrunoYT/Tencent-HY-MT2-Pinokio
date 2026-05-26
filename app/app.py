import gradio as gr
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Language mapping
LANGUAGES = {
    "中文 (Chinese)": "zh",
    "英语 (English)": "en",
    "法语 (French)": "fr",
    "葡萄牙语 (Portuguese)": "pt",
    "西班牙语 (Spanish)": "es",
    "日语 (Japanese)": "ja",
    "土耳其语 (Turkish)": "tr",
    "俄语 (Russian)": "ru",
    "阿拉伯语 (Arabic)": "ar",
    "韩语 (Korean)": "ko",
    "泰语 (Thai)": "th",
    "意大利语 (Italian)": "it",
    "德语 (German)": "de",
    "越南语 (Vietnamese)": "vi",
    "马来语 (Malay)": "ms",
    "印尼语 (Indonesian)": "id",
    "菲律宾语 (Filipino)": "tl",
    "印地语 (Hindi)": "hi",
    "繁体中文 (Traditional Chinese)": "zh-Hant",
    "波兰语 (Polish)": "pl",
    "捷克语 (Czech)": "cs",
    "荷兰语 (Dutch)": "nl",
    "高棉语 (Khmer)": "km",
    "缅甸语 (Burmese)": "my",
    "波斯语 (Persian)": "fa",
    "古吉拉特语 (Gujarati)": "gu",
    "乌尔都语 (Urdu)": "ur",
    "泰卢固语 (Telugu)": "te",
    "马拉地语 (Marathi)": "mr",
    "希伯来语 (Hebrew)": "he",
    "孟加拉语 (Bengali)": "bn",
    "泰米尔语 (Tamil)": "ta",
    "乌克兰语 (Ukrainian)": "uk",
    "藏语 (Tibetan)": "bo",
    "哈萨克语 (Kazakh)": "kk",
    "蒙古语 (Mongolian)": "mn",
    "维吾尔语 (Uyghur)": "ug",
    "粤语 (Cantonese)": "yue",
}
LABELS_BY_CODE = {code: label for label, code in LANGUAGES.items()}

TRANSLATION_MODES = [
    "basic",
    "terminology",
    "style",
    "personalization",
    "delimiters",
    "structured_data",
    "contextual",
]

FORMAT_TYPES = ["JSON", "YAML", "XML", "HTML", "Markdown", "CSV"]

MODELS = {
    "tencent/Hy-MT2-1.8B": {
        "label": "Hy-MT2-1.8B (~4 GB VRAM)",
        "vram": "~4 GB VRAM in BF16",
    },
    "tencent/Hy-MT2-7B": {
        "label": "Hy-MT2-7B (~16 GB VRAM)",
        "vram": "~16 GB VRAM in BF16",
    },
}

# Model and tokenizer (loaded on first use)
model = None
tokenizer = None
model_name = None


def get_language_name(language_code, instruction_language="en"):
    """Return the model-facing language name instead of an ISO code."""
    label = LABELS_BY_CODE.get(language_code)
    if not label:
        return language_code

    if instruction_language == "zh":
        return label.split(" (", 1)[0]

    if "(" in label and label.endswith(")"):
        return label.rsplit("(", 1)[-1][:-1]

    return label


def use_chinese_prompt(source_code, target_code):
    return source_code in ("zh", "zh-Hant") or target_code in ("zh", "zh-Hant")


def format_terminology(terminology, use_zh):
    """Convert user terminology lines to Hy-MT2 reference format."""
    lines = []
    for raw_line in terminology.strip().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if " -> " in line:
            source_term, target_term = line.split(" -> ", 1)
            source_term = source_term.strip()
            target_term = target_term.strip()
        elif "->" in line:
            source_term, target_term = line.split("->", 1)
            source_term = source_term.strip()
            target_term = target_term.strip()
        elif " 翻译成 " in line:
            lines.append(line)
            continue
        elif " translates to " in line.lower():
            lines.append(line)
            continue
        else:
            continue

        if use_zh:
            lines.append(f"{source_term} 翻译成 {target_term}")
        else:
            lines.append(f"{source_term} translates to {target_term}")

    return "\n".join(lines)


def format_preferences(preferences):
    """Number user preference lines for personalization mode."""
    items = [line.strip() for line in preferences.strip().splitlines() if line.strip()]
    formatted = []
    for index, item in enumerate(items, start=1):
        if item.startswith(("1", "2", "3", "4", "5", "6", "7", "8", "9")) and "、" in item[:3]:
            formatted.append(item)
        else:
            formatted.append(f"{index}、**{item}**")
    return formatted


def unload_model():
    """Release the loaded model to free GPU memory before switching sizes."""
    global model, tokenizer, model_name
    if model is None:
        return
    del model
    del tokenizer
    model = None
    tokenizer = None
    model_name = None
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    print("Previous model unloaded.")


def load_model(model_path="tencent/Hy-MT2-1.8B"):
    """Load the model and tokenizer."""
    global model, tokenizer, model_name
    if model is not None and model_name == model_path:
        return model, tokenizer

    if model is not None and model_name != model_path:
        unload_model()

    print(f"Loading model: {model_path}")
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
        device_map="auto",
        trust_remote_code=True,
    )
    model.eval()
    model_name = model_path
    print("Model loaded successfully!")
    return model, tokenizer


def build_prompt(
    source_text,
    target_lang_code,
    source_lang_code,
    translation_mode="basic",
    terminology="",
    context="",
    target_style="",
    preferences="",
    format_type="JSON",
):
    """Build the prompt using official Hy-MT2 translation task templates."""
    use_zh = use_chinese_prompt(source_lang_code, target_lang_code)
    target_name_zh = get_language_name(target_lang_code, "zh")
    target_name_en = get_language_name(target_lang_code, "en")

    if translation_mode == "terminology" and terminology.strip():
        term_block = format_terminology(terminology, use_zh)
        if use_zh:
            prompt = f"""参考下面的翻译：
{term_block}
将以下文本翻译为{target_name_zh}，注意只需要输出翻译后的结果，不要额外解释：

{source_text}"""
        else:
            prompt = f"""Reference the following translations:
{term_block}
Translate the following text into {target_name_en}. Note that you must ONLY output the translated result without any additional explanation:

{source_text}"""

    elif translation_mode == "style" and target_style.strip():
        if use_zh:
            prompt = f"""请将以下文本翻译为{target_name_zh}。
注意翻译的风格要严格符合【**{target_style}**】

{source_text}"""
        else:
            prompt = f"""Please translate the following text into {target_name_en}. Note that the translation style must strictly conform to [{target_style}]:

{source_text}"""

    elif translation_mode == "personalization" and preferences.strip():
        pref_lines = format_preferences(preferences)
        if use_zh:
            task_lines = "\n".join(pref_lines)
            prompt = f"""【待翻译文本】
{source_text}

【翻译任务】
{task_lines}
4、将【待翻译文本】翻译为{target_name_zh}。"""
        else:
            task_lines = "\n".join(
                f"{index}. {line.lstrip('123456789、').strip('*')}"
                for index, line in enumerate(pref_lines, start=1)
            )
            prompt = f"""[Source Text]
{source_text}

[Translation Tasks]
{task_lines}
4. Translate the [Source Text] into {target_name_en}."""

    elif translation_mode == "delimiters":
        if use_zh:
            prompt = f"""请将以下文本准确翻译为{target_name_zh}。
你必须在译文中保留等量的分隔符，绝对不可遗漏、转义或翻译该符号，并注意分隔符的位置。

{source_text}"""
        else:
            prompt = f"""Please accurately translate the following text into {target_name_en}.
You must retain the exact same number of delimiters in the translation. Strictly do not omit, escape, or translate these symbols, and pay close attention to their placement.

{source_text}"""

    elif translation_mode == "structured_data":
        if use_zh:
            prompt = f"""# 任务目标
将下方 {source_text} 中的 {format_type} 格式数据翻译为{target_name_zh}。

# 严格约束
1. 结构锁定：绝对保持原有的 {format_type} 数据结构、缩进和层级完全不变。
2. 选择性翻译：仅翻译面向用户展示的可见文本内容。
3. 禁止修改：严禁翻译或更改任何代码标签、键名 (Key)、变量占位符（如 {{{{var}}}}、${{var}}、%s、%d 等）或代码属性。

# 数据输入
{source_text}"""
        else:
            prompt = f"""### Task
Translate the user-facing text within the following {format_type} data into {target_name_en}.

### Strict Rules
1. Structure Preservation: You MUST preserve the original {format_type} data structure, nesting, hierarchy, and indentation exactly as they are.
2. Selective Translation: Translate ONLY the visible, user-facing text content/values.
3. Strict Non-Translation: NEVER translate or alter code tags, keys, properties, object names, or variable placeholders. Leave them exactly in their original English/code form.

### Source Data
{source_text}"""

    elif translation_mode == "contextual" and context.strip():
        if use_zh:
            prompt = f"""【背景信息】
{context}

请结合背景信息将以下文本翻译为{target_name_zh}。

【待翻译文本】
{source_text}"""
        else:
            prompt = f"""[Background Information]
{context}

Please translate the following text into {target_name_en}, taking the provided background information into consideration.

[Source Text]
{source_text}"""

    else:
        if use_zh:
            prompt = f"""将以下文本翻译为{target_name_zh}，注意只需要输出翻译后的结果，不要额外解释：

{source_text}"""
        else:
            prompt = f"""Translate the following text into {target_name_en}. Note that you should only output the translated result without any additional explanation:

{source_text}"""

    return prompt


def translate_text(
    source_text,
    source_language,
    target_language,
    model_choice,
    translation_mode,
    terminology,
    context,
    target_style,
    preferences,
    format_type,
    temperature,
    top_p,
    top_k,
    repetition_penalty,
):
    """Translate text using the Hy-MT2 model."""
    if not source_text.strip():
        return "Please enter text to translate.", "Ready. Enter text to translate."

    try:
        model, tokenizer = load_model(model_choice)
        model_label = MODELS.get(model_choice, {}).get("label", model_choice)

        source_lang_code = LANGUAGES.get(source_language, "en")
        target_lang_code = LANGUAGES.get(target_language, "zh")

        prompt = build_prompt(
            source_text,
            target_lang_code,
            source_lang_code,
            translation_mode,
            terminology,
            context,
            target_style,
            preferences,
            format_type,
        )

        messages = [{"role": "user", "content": prompt}]
        inputs = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt",
        ).to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=4096,
                temperature=temperature,
                top_p=top_p,
                top_k=int(top_k),
                repetition_penalty=repetition_penalty,
            )

        translation = tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[-1]:],
            skip_special_tokens=True,
        ).strip()

        return translation, f"Translation completed with {model_label}."

    except Exception as e:
        import traceback

        error_msg = f"Error: {str(e)}\n\n{traceback.format_exc()}"
        return error_msg, f"Error occurred: {str(e)}"


def create_interface():
    """Create the Gradio interface."""

    with gr.Blocks(title="Hy-MT2 Translation", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # Hy-MT2 Translation Interface

            Official prompt templates for
            [Hy-MT2-1.8B](https://huggingface.co/tencent/Hy-MT2-1.8B) and
            [Hy-MT2-7B](https://huggingface.co/tencent/Hy-MT2-7B).
            Supports all seven Hy-MT2 translation task types across 33 languages.
            """
        )

        with gr.Row():
            with gr.Column(scale=1):
                model_choice = gr.Dropdown(
                    choices=list(MODELS.keys()),
                    value="tencent/Hy-MT2-1.8B",
                    label="Model",
                    info="1.8B ~4 GB VRAM | 7B ~16 GB VRAM (BF16). Switching models unloads the previous one.",
                )

                source_language = gr.Dropdown(
                    choices=list(LANGUAGES.keys()),
                    value="英语 (English)",
                    label="Source Language",
                )

                target_language = gr.Dropdown(
                    choices=list(LANGUAGES.keys()),
                    value="中文 (Chinese)",
                    label="Target Language",
                )

                translation_mode = gr.Radio(
                    choices=TRANSLATION_MODES,
                    value="basic",
                    label="Translation Mode",
                    info="basic | terminology | style | personalization | delimiters | structured_data | contextual",
                )

                terminology_input = gr.Textbox(
                    label="Terminology Guide",
                    placeholder="AI -> 人工智能\nmachine learning -> 机器学习",
                    lines=4,
                    visible=False,
                )

                target_style_input = gr.Textbox(
                    label="Target Style",
                    placeholder="e.g. formal, casual, literary",
                    visible=False,
                )

                preferences_input = gr.Textbox(
                    label="User Preferences",
                    placeholder="Use concise wording\nKeep product names unchanged",
                    lines=4,
                    visible=False,
                )

                format_type_input = gr.Dropdown(
                    choices=FORMAT_TYPES,
                    value="JSON",
                    label="Format Type",
                    visible=False,
                )

                context_input = gr.Textbox(
                    label="Background Information",
                    placeholder="Enter background context that helps with translation...",
                    lines=4,
                    visible=False,
                )

                gr.Markdown("### Generation Parameters")
                temperature = gr.Slider(0.1, 2.0, value=0.7, step=0.1, label="Temperature")
                top_p = gr.Slider(0.1, 1.0, value=0.6, step=0.05, label="Top-p")
                top_k = gr.Slider(1, 100, value=20, step=1, label="Top-k")
                repetition_penalty = gr.Slider(1.0, 2.0, value=1.05, step=0.05, label="Repetition Penalty")

            with gr.Column(scale=2):
                source_text = gr.Textbox(
                    label="Source Text",
                    placeholder="Enter text to translate...",
                    lines=10,
                )

                translate_btn = gr.Button("Translate", variant="primary", size="lg")

                status_text = gr.Textbox(
                    label="Status",
                    value="Ready. Click 'Translate' to start.",
                    interactive=False,
                )

                output_text = gr.Textbox(
                    label="Translation",
                    lines=10,
                    interactive=False,
                )

                gr.Examples(
                    examples=[
                        ["It's on the house.", "英语 (English)", "中文 (Chinese)", "basic"],
                        ["Hello, how are you?", "英语 (English)", "中文 (Chinese)", "basic"],
                        ["Bonjour, comment allez-vous?", "法语 (French)", "英语 (English)", "basic"],
                    ],
                    inputs=[source_text, source_language, target_language, translation_mode],
                    label="Example Translations",
                )

        def update_mode_visibility(mode):
            return {
                terminology_input: gr.update(visible=(mode == "terminology")),
                target_style_input: gr.update(visible=(mode == "style")),
                preferences_input: gr.update(visible=(mode == "personalization")),
                format_type_input: gr.update(visible=(mode == "structured_data")),
                context_input: gr.update(visible=(mode == "contextual")),
            }

        translation_mode.change(
            update_mode_visibility,
            inputs=[translation_mode],
            outputs=[
                terminology_input,
                target_style_input,
                preferences_input,
                format_type_input,
                context_input,
            ],
        )

        translate_btn.click(
            translate_text,
            inputs=[
                source_text,
                source_language,
                target_language,
                model_choice,
                translation_mode,
                terminology_input,
                context_input,
                target_style_input,
                preferences_input,
                format_type_input,
                temperature,
                top_p,
                top_k,
                repetition_penalty,
            ],
            outputs=[output_text, status_text],
        )

        gr.Markdown(
            """
            ### Notes
            - Recommended inference params for 1.8B/7B: temperature=0.7, top_p=0.6, top_k=20, repetition_penalty=1.05, max_tokens=4096
            - Hy-MT2-7B needs roughly 16 GB GPU memory in BF16; use 1.8B on smaller GPUs
            - Language names in prompts use Chinese names for Chinese prompts and English names for English prompts
            - Terminology mode accepts `source -> target` pairs, converted to the official reference format automatically
            - Structured data mode preserves keys, tags, and placeholders while translating visible text
            """
        )

    return demo


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Hy-MT2 Gradio Interface")
    parser.add_argument("--share", action="store_true", help="Create a public link")
    parser.add_argument("--server-name", type=str, default="127.0.0.1", help="Server name")
    parser.add_argument("--server-port", type=int, default=7860, help="Server port")
    args = parser.parse_args()

    demo = create_interface()
    demo.launch(
        share=args.share,
        server_name=args.server_name,
        server_port=args.server_port,
        show_error=True,
    )
