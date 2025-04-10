import openai
import os
import re
import yaml
import traceback

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

openai.api_key = config.get("openai_api_key", "")

# Debug flag from configuration. Set debug_llm: true in config.yaml to enable extra logging.
DEBUG = config.get("debug_llm", False)

# Model pricing (per 1K tokens)
MODEL_COST = {
    "gpt-3.5-turbo-0125": {"prompt": 0.0005, "completion": 0.0015},
    "gpt-4-turbo": {"prompt": 0.01, "completion": 0.03}
}

def extract_answer(text):
    # Use case-insensitive matching to capture answer choices a-d.
    match = re.search(r'Answer Choice:\s*\(?([a-d])\)?', text, flags=re.IGNORECASE)
    return match.group(1).lower() if match else "?"

def extract_evidence(text):
    return re.findall(r'"([^"]+)"', text)

def call_gpt(prompt, model="gpt-3.5-turbo-0125"):
    print("🔑 Using model:", model)
    try:
        res = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
    except Exception as e:
        if DEBUG:
            print("❌ Exception in call_gpt:")
            traceback.print_exc()
        raise e  # Re-raise the exception after logging if debugging is enabled

    usage = res["usage"]
    prompt_tokens = usage["prompt_tokens"]
    completion_tokens = usage["completion_tokens"]
    total_tokens = usage["total_tokens"]

    pricing = MODEL_COST.get(model, {"prompt": 0, "completion": 0})
    cost = (prompt_tokens * pricing["prompt"] + completion_tokens * pricing["completion"]) / 1000

    print(f"🧾 {model} | Prompt: {prompt_tokens} | Completion: {completion_tokens} | Total: {total_tokens} | 💸 ${cost:.5f}")

    return res["choices"][0]["message"]["content"], cost

def run_dual_personas(prompt_a, prompt_b, model_a="gpt-3.5-turbo-0125", model_b="gpt-4-turbo"):
    out_a, cost_a = call_gpt(prompt_a, model_a)
    out_b, cost_b = call_gpt(prompt_b, model_b)

    return {
        "personaA": {
            "model": model_a,
            "output": out_a,
            "answer": extract_answer(out_a),
            "evidence": extract_evidence(out_a),
            "cost": round(cost_a, 5)
        },
        "personaB": {
            "model": model_b,
            "output": out_b,
            "answer": extract_answer(out_b),
            "evidence": extract_evidence(out_b),
            "cost": round(cost_b, 5)
        },
        "total_cost": round(cost_a + cost_b, 5)
    }
