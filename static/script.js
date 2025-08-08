function askTitleAndSubmit() {
    const name = prompt("Entrez un nom pour votre vidéo :");
    if (name === null || name.trim() === "") {
        return;
    }
    document.getElementById('videoTitle').value = name.trim();
    document.getElementById('uploadForm').submit();
}

function playVideo(src) {
    const videoPlayer = document.getElementById("videoPlayer");
    videoPlayer.querySelector("source").setAttribute("src", src);
    videoPlayer.load();
    videoPlayer.play();
}

function deleteVideo(event, filename) {
    event.stopPropagation();
    if (confirm("Supprimer cette vidéo ?")) {
        fetch("/delete", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filename: filename })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        });
    }
}
