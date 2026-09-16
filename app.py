import os
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from google import genai
from chatbot_config import SYSTEM_PROMPT

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

client = genai.Client(api_key=api_key) if api_key else None

@app.get("/")
def home():
    return render_template("index.html")

@app.post("/chat")
def chat():
    if client is None:
        return jsonify({"error": "GEMINI_API_KEY is not configured."}), 500

    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Please enter a message."}), 400

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[
                {"role": "user", "parts": [{"text": SYSTEM_PROMPT + "\n\nUser question:\n" + message}]}
            ],
        )
        answer = (response.text or "").strip()
        if not answer:
            answer = "I could not generate a response. Please try again."
        return jsonify({"answer": answer})
    except Exception as exc:
        app.logger.exception("Gemini request failed")
        return jsonify({"error": f"Unable to contact Gemini right now: {exc}"}), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
