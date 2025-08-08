from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import subprocess
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 📂 Dossiers
BASE_DIR = "static"
VIDEO_FOLDER = os.path.join(BASE_DIR, "videos")
THUMB_FOLDER = os.path.join(BASE_DIR, "thumbnails")
METADATA_FILE = os.path.join(BASE_DIR, "metadata.json")

os.makedirs(VIDEO_FOLDER, exist_ok=True)
os.makedirs(THUMB_FOLDER, exist_ok=True)

# Charger les titres enregistrés
def load_metadata():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Sauvegarder les titres
def save_metadata(metadata):
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

# 🎯 Page d'accueil
@app.route("/")
def index():
    metadata = load_metadata()
    videos = []
    for f in os.listdir(VIDEO_FOLDER):
        if f.lower().endswith(".mp4"):
            thumb = os.path.splitext(f)[0] + ".jpg"
            title = metadata.get(f, os.path.splitext(f)[0])
            videos.append({"name": f, "thumb": thumb, "title": title})
    return render_template("index.html", videos=videos)

# 📤 Upload vidéo
@app.route("/upload", methods=["POST"])
def upload():
    if "video" not in request.files:
        return redirect(url_for("index"))

    file = request.files["video"]
    if file.filename == "":
        return redirect(url_for("index"))

    filename = secure_filename(file.filename)
    save_path = os.path.join(VIDEO_FOLDER, filename)
    file.save(save_path)

    # 📸 Génération miniature au milieu de la vidéo
    thumb_name = os.path.splitext(filename)[0] + ".jpg"
    thumb_path = os.path.join(THUMB_FOLDER, thumb_name)
    try:
        subprocess.run([
            "C:/ffmpeg/bin/ffmpeg.exe",
            "-i", save_path,
            "-ss", "00:00:01",
            "-vframes", "1",
            thumb_path
        ], check=True)
    except Exception as e:
        print("Erreur miniature:", e)

    # 💾 Sauvegarde du titre
    title = request.form.get("title", "").strip()
    if not title:
        title = os.path.splitext(filename)[0]
    metadata = load_metadata()
    metadata[filename] = title
    save_metadata(metadata)

    return redirect(url_for("index"))

# 🗑 Suppression vidéo
@app.route("/delete", methods=["POST"])
def delete_video():
    data = request.get_json()
    filename = data.get("filename")

    video_path = os.path.join(VIDEO_FOLDER, filename)
    thumb_path = os.path.join(THUMB_FOLDER, os.path.splitext(filename)[0] + ".jpg")

    if os.path.exists(video_path):
        os.remove(video_path)
    if os.path.exists(thumb_path):
        os.remove(thumb_path)

    metadata = load_metadata()
    if filename in metadata:
        del metadata[filename]
        save_metadata(metadata)

    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
