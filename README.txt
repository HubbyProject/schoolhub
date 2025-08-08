# SchoolHub — Projet complet

## Lancer en local (Windows)
1) Installez FFmpeg et placez `ffmpeg.exe` ici : `C:\ffmpeg\bin\ffmpeg.exe`
   (ou définissez la variable d'env FFMPEG_BIN vers votre binaire)
2) Dans ce dossier : 
   - pip install -r requirements.txt
   - python app.py
3) Ouvrez http://127.0.0.1:5000

## Déployer en public sur Render
1) Poussez ce dossier sur GitHub
2) Sur https://dashboard.render.com -> New -> Web Service -> From repo
3) Render détecte le Dockerfile. Créez le service.
4) Ajoutez un disque persistant (recommandé) :
   - Name: data
   - Mount Path: /data
   - Size: 5 GB
   - (la variable DATA_DIR=/data est déjà gérée dans render.yaml)
5) L'URL publique sera affichée après le déploiement.

## Fonctionnalités
- Upload de .mp4
- Miniature automatique (au milieu) via ffmpeg
- Suppression (vidéo + miniature)
- Interface responsive