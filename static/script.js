function playVideo(src) {
  const videoPlayer = document.getElementById("videoPlayer");
  videoPlayer.querySelector("source").setAttribute("src", src);
  videoPlayer.load();
  videoPlayer.play();
}
function deleteVideo(event, filename) {
  event.stopPropagation();
  if (!confirm(`Supprimer ${filename} ?`)) return;
  fetch('/delete', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) location.reload();
    else alert("Erreur : " + (data.error || "suppression échouée"));
  });
}