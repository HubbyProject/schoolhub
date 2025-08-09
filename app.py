from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import subprocess
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 📂 Dossiers (persistants si DATA_DIR=/data est défini sur Render)
BASE_DIR = os.environ.get("DATA_DIR", "static")
VIDEO_FOLDER = os.path.join(BASE_DIR, "videos")
THUMB_FOLDER = os.path.join(BASE_DIR, "thumbnails")
METADATA_FILE = os.path.join(BASE_DIR, "metadata.json")

os.makedirs(VIDEO_FOLDER, exist_ok=True)
os.makedirs(THUMB_FOLDER, exist_ok=True)

# 🔎 FFmpeg: Windows local OU Linux (Render)
DEFAULT_WIN = r"C:\ffmpeg\bin\ffmpeg.exe"
FFMPEG_BIN = os.environ.get("FFMPEG_BIN") or (DEFAULT_WIN if os.path.exists(DEFAULT_WIN) else "ffmpeg")

def load_metadata():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_metadata(metadata):
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

def get_video_middle_seconds(video_path: str) -> float:
    # Essaie d’estimer la durée pour capturer au milieu (sinon fallback 1s)
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

def generate_thumbnail(video_path, thumb_path):
    middle = get_video_middle_seconds(video_path)
    cmd = [
        FFMPEG_BIN,
        "-ss", str(middle),
        "-i", video_path,
        "-vframes", "1",
        "-q:v", "2",
        "-s", "320x180",
        thumb_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)

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

    # 📸 Miniature (au milieu)
    thumb_name = os.path.splitext(filename)[0] + ".jpg"
    thumb_path = os.path.join(THUMB_FOLDER, thumb_name)
    generate_thumbnail(save_path, thumb_path)

    # 💾 Titre
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
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
