import yt_dlp

opts = {
    "skip_download": True,
    "getcomments": True,
    "quiet": True,
    "nocheckcertificate": True,
    "extractor_args": {"youtube": {"max_comments": ["5"]}},
}
with yt_dlp.YoutubeDL(opts) as y:
    info = y.extract_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ", download=False)

for c in info.get("comments", []):
    print(c["text"])