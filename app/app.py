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

# Model and tokenizer (will be loaded on first use)
model = None
tokenizer = None
model_name = None


def load_model(model_path="tencent/HY-MT1.5-1.8B"):
    """Load the model and tokenizer"""
    global model, tokenizer, model_name
    if model is None or model_name != model_path:
        print(f"Loading model: {model_path}")
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForCausalLM.from_pretrained(
            model_path, 
            device_map="auto",
            torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32
        )
        model_name = model_path
        print("Model loaded successfully!")
    return model, tokenizer


def build_prompt(source_text, target_language, source_language="auto", 
                 translation_mode="basic", terminology="", context=""):
    """Build the prompt based on translation mode"""
    
    # Determine if source is Chinese
    is_chinese_source = source_language == "zh" or source_language == "zh-Hant"
    is_chinese_target = target_language == "zh" or target_language == "zh-Hant"
    target_name_zh = get_language_name(target_language, "zh")
    target_name_en = get_language_name(target_language, "en")
    
    if translation_mode == "terminology" and terminology:
        # Terminology intervention
        source_term, target_term = terminology.split(" -> ") if " -> " in terminology else ("", "")
        if is_chinese_target:
            prompt = f"""参考下面的翻译：
{source_term} 翻译成 {target_term}

将以下文本翻译为{target_name_zh}，注意只需要输出翻译后的结果，不要额外解释：
{source_text}"""
        else:
            prompt = f"""参考下面的翻译：
{source_term} 翻译成 {target_term}

Translate the following segment into {target_name_en}, without additional explanation.

{source_text}"""
    
    elif translation_mode == "contextual" and context:
        # Contextual translation
        if is_chinese_target:
            prompt = f"""{context}
参考上面的信息，把下面的文本翻译成{target_name_zh}，注意不需要翻译上文，也不要额外解释：
{source_text}

"""
        else:
            prompt = f"""{context}
Based on the above information, translate the following text into {target_name_en}, without translating the context above or additional explanation:

{source_text}

"""
    
    elif translation_mode == "formatted":
        # Formatted translation (currently only supports translation to Chinese)
        if target_language not in ["zh", "zh-Hant"]:
            # If target is not Chinese, use basic translation
            if is_chinese_source:
                prompt = f"""将以下文本翻译为{target_name_zh}，注意只需要输出翻译后的结果，不要额外解释：

{source_text}"""
            else:
                prompt = f"""Translate the following segment into {target_name_en}, without additional explanation.

{source_text}"""
        else:
            prompt = f"""将以下<source></source>之间的文本翻译为中文，注意只需要输出翻译后的结果，不要额外解释，原文中的<sn></sn>标签表示标签内文本包含格式信息，需要在译文中相应的位置尽量保留该标签。输出格式为：<target>str</target>

<source>{source_text}</source>"""
    
    else:
        # Basic translation
        if is_chinese_source or is_chinese_target:
            prompt = f"""将以下文本翻译为{target_name_zh}，注意只需要输出翻译后的结果，不要额外解释：

{source_text}"""
        else:
            prompt = f"""Translate the following segment into {target_name_en}, without additional explanation.

{source_text}"""
    
    return prompt


def translate_text(source_text, source_language, target_language, 
                  model_choice, translation_mode, terminology, context,
                  temperature, top_p, top_k, repetition_penalty):
    """Translate text using the model"""
    global model, tokenizer, model_name
    
    if not source_text.strip():
        return "Please enter text to translate.", "Ready. Enter text to translate."
    
    try:
        # Load model if needed
        if model is None or model_name != model_choice:
            status_msg = "Loading model..."
        else:
            status_msg = "Translating..."
        
        model, tokenizer = load_model(model_choice)
        
        # Get language codes
        source_lang_code = LANGUAGES.get(source_language, "en")
        target_lang_code = LANGUAGES.get(target_language, "zh")
        
        # Build prompt
        prompt = build_prompt(
            source_text, 
            target_lang_code, 
            source_lang_code,
            translation_mode,
            terminology,
            context
        )
        
        # Prepare messages
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        # Tokenize
        tokenized_chat = tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=False,
            return_tensors="pt"
        )
        
        # Generate
        with torch.no_grad():
            outputs = model.generate(
                tokenized_chat.to(model.device),
                max_new_tokens=2048,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                repetition_penalty=repetition_penalty,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Decode
        output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract translation (remove the prompt part)
        # The model output includes the input, so we need to extract just the translation
        # Try to find where the actual translation starts
        if prompt in output_text:
            translation = output_text.split(prompt, 1)[-1].strip()
        elif "<|im_start|>assistant" in output_text:
            # Extract after assistant tag
            translation = output_text.split("<|im_start|>assistant", 1)[-1].strip()
        elif "assistant\n" in output_text:
            translation = output_text.split("assistant\n", 1)[-1].strip()
        else:
            # Fallback: return the full output but try to clean it
            translation = output_text
        
        # Clean up common artifacts and chat template markers
        translation = translation.replace("<|im_end|>", "").replace("<|im_start|>", "")
        translation = translation.replace("<|endoftext|>", "").strip()
        
        # Remove any remaining prompt fragments
        for line in prompt.split("\n"):
            if line.strip() and line.strip() in translation:
                translation = translation.replace(line.strip(), "").strip()
        
        return translation, "Translation completed successfully!"
        
    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}\n\n{traceback.format_exc()}"
        return error_msg, f"Error occurred: {str(e)}"


def create_interface():
    """Create the Gradio interface"""
    
    with gr.Blocks(title="HY-MT1.5 Translation", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # 🌐 HY-MT1.5 Translation Interface
            
            **Hunyuan Translation Model Version 1.5** - Supporting mutual translation across 33 languages
            
            Select your model, source and target languages, and translation mode to get started.
            """
        )
        
        with gr.Row():
            with gr.Column(scale=1):
                model_choice = gr.Dropdown(
                    choices=[
                        "tencent/HY-MT1.5-1.8B",
                        "tencent/HY-MT1.5-7B",
                    ],
                    value="tencent/HY-MT1.5-1.8B",
                    label="Model",
                    info="Choose the model size (1.8B is faster, 7B is more accurate)"
                )
                
                source_language = gr.Dropdown(
                    choices=list(LANGUAGES.keys()),
                    value="英语 (English)",
                    label="Source Language"
                )
                
                target_language = gr.Dropdown(
                    choices=list(LANGUAGES.keys()),
                    value="中文 (Chinese)",
                    label="Target Language"
                )
                
                translation_mode = gr.Radio(
                    choices=["basic", "terminology", "contextual", "formatted"],
                    value="basic",
                    label="Translation Mode",
                    info="basic: Standard translation | terminology: With terminology guide | contextual: With context | formatted: Preserve formatting tags"
                )
                
                terminology_input = gr.Textbox(
                    label="Terminology Guide (for terminology mode)",
                    placeholder='e.g., "AI -> 人工智能"',
                    visible=False
                )
                
                context_input = gr.Textbox(
                    label="Context (for contextual mode)",
                    placeholder="Enter context that helps with translation...",
                    lines=3,
                    visible=False
                )
                
                gr.Markdown("### Generation Parameters")
                temperature = gr.Slider(
                    minimum=0.1,
                    maximum=2.0,
                    value=0.7,
                    step=0.1,
                    label="Temperature"
                )
                top_p = gr.Slider(
                    minimum=0.1,
                    maximum=1.0,
                    value=0.6,
                    step=0.05,
                    label="Top-p"
                )
                top_k = gr.Slider(
                    minimum=1,
                    maximum=100,
                    value=20,
                    step=1,
                    label="Top-k"
                )
                repetition_penalty = gr.Slider(
                    minimum=1.0,
                    maximum=2.0,
                    value=1.05,
                    step=0.05,
                    label="Repetition Penalty"
                )
            
            with gr.Column(scale=2):
                source_text = gr.Textbox(
                    label="Source Text",
                    placeholder="Enter text to translate...",
                    lines=10
                )
                
                translate_btn = gr.Button("Translate", variant="primary", size="lg")
                
                status_text = gr.Textbox(
                    label="Status",
                    value="Ready. Click 'Translate' to start.",
                    interactive=False,
                    visible=True
                )
                
                output_text = gr.Textbox(
                    label="Translation",
                    lines=10,
                    interactive=False
                )
                
                gr.Examples(
                    examples=[
                        ["It's on the house.", "英语 (English)", "中文 (Chinese)", "basic"],
                        ["Hello, how are you?", "英语 (English)", "中文 (Chinese)", "basic"],
                        ["Bonjour, comment allez-vous?", "法语 (French)", "英语 (English)", "basic"],
                    ],
                    inputs=[source_text, source_language, target_language, translation_mode],
                    label="Example Translations"
                )
        
        # Show/hide terminology and context inputs based on mode
        def update_mode_visibility(mode):
            return {
                terminology_input: gr.update(visible=(mode == "terminology")),
                context_input: gr.update(visible=(mode == "contextual"))
            }
        
        translation_mode.change(
            update_mode_visibility,
            inputs=[translation_mode],
            outputs=[terminology_input, context_input]
        )
        
        # Translate button action
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
                temperature,
                top_p,
                top_k,
                repetition_penalty
            ],
            outputs=[output_text, status_text]
        )
        
        gr.Markdown(
            """
            ### 📝 Notes:
            - First translation may take longer as the model loads
            - Recommended parameters are pre-set (temperature=0.7, top_p=0.6, top_k=20, repetition_penalty=1.05)
            - For terminology mode: Enter pairs like "source_term -> target_term"
            - For contextual mode: Provide context that helps with translation
            - For formatted mode: Use <sn></sn> tags to preserve formatting
            """
        )
    
    return demo


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="HY-MT1.5 Gradio Interface")
    parser.add_argument("--share", action="store_true", help="Create a public link")
    parser.add_argument("--server-name", type=str, default="127.0.0.1", help="Server name")
    parser.add_argument("--server-port", type=int, default=7860, help="Server port")
    args = parser.parse_args()
    
    demo = create_interface()
    demo.launch(
        share=args.share,
        server_name=args.server_name,
        server_port=args.server_port,
        show_error=True
    )

