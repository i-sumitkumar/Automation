import os
import yaml
from app import app

def load_config():
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    os.environ["OPENAI_API_KEY"] = config.get("openai_api_key", "")
    return config

if __name__ == "__main__":
    config = load_config()
    port = config.get("port", 5000)

    print(f"🚀 Starting Flask server on http://localhost:{port}")
    print("📌 Keep this terminal open while working with the UI (index.html).")

    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
