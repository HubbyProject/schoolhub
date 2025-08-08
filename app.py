import os
import subprocess
from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Dossiers (DATA_DIR=/data pour Render ; sinon "static" en local)
BASE_DIR = os.environ.get("DATA_DIR", "static")
VIDEO_FOLDER = os.path.join(BASE_DIR, "videos")
THUMB_FOLDER = os.path.join(BASE_DIR, "thumbnails")
os.makedirs(VIDEO_FOLDER, exist_ok=True)
os.makedirs(THUMB_FOLDER, exist_ok=True)

# ffmpeg : détecte binaire Windows local sinon 'ffmpeg' (Docker/Render)
DEFAULT_WIN = r"C:\ffmpeg\bin\ffmpeg.exe"
FFMPEG_BIN = os.environ.get("FFMPEG_BIN") or (DEFAULT_WIN if os.path.exists(DEFAULT_WIN) else "ffmpeg")

def get_video_middle_seconds(video_path: str) -> float:
    '''Retourne ~la moitié de la durée en secondes (fallback = 1.0).'''
    try:
        proc = subprocess.run(
            [FFMPEG_BIN, "-i", video_path, "-f", "null", "-"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        for line in proc.stderr.splitlines():
            if "Duration:" in line:
                part = line.split("Duration:")[1].split(",")[0].strip()
                h, m, s = part.split(":")
                total = int(h) * 3600 + int(m) * 60 + float(s)
                return max(1.0, total / 2.0)
    except Exception:
        pass
    return 1.0

def generate_thumbnail(video_path: str, thumb_path: str):
    '''Capture 1 frame au milieu (320x180 jpg).'''
    middle = get_video_middle_seconds(video_path)
    cmd = [
        FFMPEG_BIN, "-ss", str(middle), "-i", video_path,
        "-vframes", "1", "-q:v", "2", "-s", "320x180",
        thumb_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)

@app.route("/")
def index():
    videos = []
    for f in os.listdir(VIDEO_FOLDER):
        if f.lower().endswith(".mp4"):
            videos.append({"name": f, "thumb": os.path.splitext(f)[0] + ".jpg"})
    videos.sort(key=lambda x: x["name"].lower())
    return render_template("index.html", videos=videos)

@app.route("/upload", methods=["POST"])
def upload():
    if "video" not in request.files:
        return "Aucun fichier", 400
    file = request.files["video"]
    if file.filename == "":
        return "Nom de fichier vide", 400

    filename = secure_filename(file.filename)
    video_path = os.path.join(VIDEO_FOLDER, filename)
    file.save(video_path)

    thumb_path = os.path.join(THUMB_FOLDER, os.path.splitext(filename)[0] + ".jpg")
    generate_thumbnail(video_path, thumb_path)

    return redirect(url_for("index"))

@app.route("/delete", methods=["POST"])
def delete():
    data = request.get_json() or {}
    filename = data.get("filename")
    if not filename:
        return jsonify(success=False, error="Aucun nom fourni"), 400

    video_path = os.path.join(VIDEO_FOLDER, filename)
    thumb_path = os.path.join(THUMB_FOLDER, os.path.splitext(filename)[0] + ".jpg")

    if os.path.exists(video_path):
        os.remove(video_path)
    if os.path.exists(thumb_path):
        os.remove(thumb_path)

    return jsonify(success=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)