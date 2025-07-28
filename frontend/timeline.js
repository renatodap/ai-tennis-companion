async function loadTimeline() {
    const res = await fetch("timeline.json");
    const timeline = await res.json();
    const container = document.getElementById("timeline-container");

    container.innerHTML = ""; // clear previous

    timeline.forEach(event => {
        const div = document.createElement("div");
        div.className = "event";

        div.innerHTML = `
      <h3>${event.stroke.toUpperCase()}</h3>
      <div class="thumbs">
        <img src="frames/${event.start}" alt="Start Frame">
        <img src="/frames/${event.end}" alt="End Frame">
      </div>
      <p>${event.start} → ${event.end}</p>
      <button onclick="seekVideo(${event.start_sec})">▶ Jump to ${event.start_sec}s</button>
    `;

        container.appendChild(div);
    });
}

function seekVideo(time) {
    const video = document.getElementById("video");
    video.currentTime = time;
    video.play();
}

loadTimeline();

document.getElementById("upload-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById("video-file");
    const status = document.getElementById("upload-status");
    const file = fileInput.files[0];

    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    status.textContent = "⏳ Uploading and analyzing...";

    try {
        const res = await fetch("http://localhost:8000/api/analyze", {
            method: "POST",
            body: formData,
        });

        // … inside your submit handler …
        if (!res.ok) throw new Error("Failed to analyze video");

        // get the returned filename (optional: you can modify analyze to return it)
        const data = await res.json();

        // … after successful fetch and before loadTimeline()
        const vid = document.getElementById("video");

        // Force-reload the new sample_video.mp4 by appending a timestamp query
        vid.src = `sample_video.mp4?cache_bust=${Date.now()}`;
        vid.load();

        // now refresh timeline
        status.textContent = "✅ Analysis complete. Refreshing timeline…";
        await new Promise(r => setTimeout(r, 500));
        loadTimeline();

    } catch (err) {
        console.error(err);
        status.textContent = "❌ Upload failed.";
    }
});
git