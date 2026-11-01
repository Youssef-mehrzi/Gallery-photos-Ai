from flask import Flask, render_template, request, jsonify
import os
import requests

app = Flask(__name__)

# Dossier win n'sajlou el videowet مؤقتاً قبل إرسالها للديسكورد
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# حط هنا رابط الـ Webhook الخاص بقناة Discord متاعك
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1566467697921753138/OFyLYOzINR7s8BdcheUpf27-BJb7i9OwwplEMIRHoK152MY0kBdMqGXJTHvUpEyih5lz"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({"status": "error", "message": "No video found"}), 400
    
    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({"status": "error", "message": "Empty filename"}), 400
    
    file_path = os.path.join(UPLOAD_FOLDER, video_file.filename)
    video_file.save(file_path)
    
    # Send video to Discord via Webhook
    try:
        with open(file_path, 'rb') as f:
            response = requests.post(
                DISCORD_WEBHOOK_URL,
                data={"content": "🎥 New periodic verification video recorded!"},
                files={"file": f}
            )
        # Clean local file after sending
        os.remove(file_path)
        
        if response.status_code in [200, 204]:
            return jsonify({"status": "success", "message": "Video sent to Discord!"})
        else:
            return jsonify({"status": "error", "message": "Failed to send to Discord"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
