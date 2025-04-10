from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from retriever import embed_question, search_chunks
from prompt_builder import build_prompts
from llm_runner import run_dual_personas
from prepare_pdf import prepare
from datetime import datetime
import os, json, yaml
from flask_cors import CORS

with open("config.yaml") as f:
    CONFIG = yaml.safe_load(f)

TOP_K = CONFIG.get("top_k", 5)
LOG_DIR = CONFIG.get("log_dir", "logs")
CURRENT_PDF_PATH = "cache/current_pdf.pdf"
MODEL_A_DIR = "Result/Model_A"
MODEL_B_DIR = "Result/Model_B"
PROMPT_DIR = "prompts"
PROMPT_A_PATH = os.path.join(PROMPT_DIR, "prompt_a.txt")
PROMPT_B_PATH = os.path.join(PROMPT_DIR, "prompt_b.txt")

app = Flask(__name__)
CORS(app)

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(MODEL_A_DIR, exist_ok=True)
os.makedirs(MODEL_B_DIR, exist_ok=True)
os.makedirs(PROMPT_DIR, exist_ok=True)

def prepend_txt_log(filepath, lines):
    separator = "\n" + ("=" * 120) + "\n"
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    log_content = "\n".join(lines) + separator

    if not os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(log_content)
        print(f"✅ File created and log written to {filepath}")
    else:
        with open(filepath, "r", encoding="utf-8") as f:
            existing_content = f.read()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(log_content + existing_content)
        print(f"✅ Log prepended to existing file at {filepath}")

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    pdf_file = request.files.get("pdf")
    if not pdf_file:
        return jsonify({"message": "❌ No PDF uploaded."}), 400
    try:
        filename = secure_filename(pdf_file.filename)
        os.makedirs("cache", exist_ok=True)
        full_path = os.path.join("cache", "current_pdf.pdf")
        pdf_file.save(full_path)
        prepare(full_path)
        return jsonify({"message": f"✅ PDF '{filename}' uploaded and processed."}), 200
    except Exception as e:
        print("❌ PDF processing error:", str(e))
        return jsonify({"message": "❌ Server error while processing PDF."}), 500

@app.route('/update_prompt_a', methods=['POST'])
def update_prompt_a():
    instructions = request.json.get("instructions", "")
    with open(PROMPT_A_PATH, "w", encoding="utf-8") as f:
        f.write(instructions)
    return jsonify({"message": "✅ Prompt A updated successfully."})

@app.route('/update_prompt_b', methods=['POST'])
def update_prompt_b():
    instructions = request.json.get("instructions", "")
    with open(PROMPT_B_PATH, "w", encoding="utf-8") as f:
        f.write(instructions)
    return jsonify({"message": "✅ Prompt B updated successfully."})

@app.route('/get_prompts', methods=['GET'])
def get_prompts():
    prompt_a = open(PROMPT_A_PATH).read() if os.path.exists(PROMPT_A_PATH) else ""
    prompt_b = open(PROMPT_B_PATH).read() if os.path.exists(PROMPT_B_PATH) else ""
    return jsonify({"promptA": prompt_a, "promptB": prompt_b})

@app.route('/run_mcq', methods=['POST'])
def run_mcq():
    data = request.json
    question = data['question']
    ground_truth = data.get('ground_truth', '').strip().lower()
    model_a = data.get("model_a", CONFIG.get("model_a", "gpt-3.5-turbo-0125"))
    model_b = data.get("model_b", CONFIG.get("model_b", "gpt-3.5-turbo-0125"))

    vec = embed_question(question)
    chunks = search_chunks(vec, top_k=TOP_K)
    context = "\n\n".join(chunks['chunk_text'].tolist())

    p_a, p_b = build_prompts(question, context)
    now = datetime.now()
    timestamp = now.strftime('%Y%m%d_%H%M%S')
    readable_time = now.strftime('%Y-%m-%d %H:%M:%S')

    def write_input_log(persona, model, prompt, output_dir):
        log_lines = [
            f"Timestamp: {timestamp}",
            f"Datetime: {readable_time}",
            f"Model: {model}",
            f"Persona: {persona}",
            "\nPrompt:\n" + prompt,
            f"\nGround Truth: {ground_truth}"
        ]
        filepath = os.path.join(output_dir, f"{persona}_Input.txt")
        prepend_txt_log(filepath, log_lines)

    write_input_log("Model_A", model_a, p_a, MODEL_A_DIR)
    write_input_log("Model_B", model_b, p_b, MODEL_B_DIR)

    try:
        print("Sending to Model A:")
        print(p_a)
        print("\nSending to Model B:")
        print(p_b)
        result = run_dual_personas(p_a, p_b, model_a=model_a, model_b=model_b)
    except Exception as e:
        # Separate error logs including the respective prompt for each model.
        fail_lines_a = [
            f"Timestamp: {timestamp}",
            f"Datetime: {readable_time}",
            f"Model A: {model_a}",
            f"❌ LLM call failed: {str(e)}",
            "\nPrompt (Model A):\n" + p_a,
        ]
        fail_lines_b = [
            f"Timestamp: {timestamp}",
            f"Datetime: {readable_time}",
            f"Model A: {model_b}",
            f"❌ LLM call failed: {str(e)}",
            "\nPrompt (Model B):\n" + p_b,
        ]
        prepend_txt_log(os.path.join(MODEL_A_DIR, "Model_A_Output.txt"), fail_lines_a)
        prepend_txt_log(os.path.join(MODEL_B_DIR, "Model_B_Output.txt"), fail_lines_b)
        return jsonify({"error": "❌ LLM call failed.", "details": str(e)}), 500

    def write_output_log(persona, content, prompt, output_dir):
        log_lines = [
            f"Timestamp: {timestamp}",
            f"Datetime: {readable_time}",
            f"Prompt:\n{prompt}",
            f"Ground Truth: {ground_truth}",
            f"Output:\n{content['output']}",
            "\nEvidence:"
        ] + ["- " + ev for ev in content.get("evidence", [])] + [
            f"\nCost: ${content['cost']:.5f}"
        ]
        filepath = os.path.join(output_dir, f"{persona}_Output.txt")
        prepend_txt_log(filepath, log_lines)

    write_output_log("Model_A", result['personaA'], p_a, MODEL_A_DIR)
    write_output_log("Model_B", result['personaB'], p_b, MODEL_B_DIR)

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
