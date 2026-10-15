import re
from itertools import islice
from youtube_comment_downloader import YoutubeCommentDownloader

def extract_video_id(url):
    m = re.search(r"(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_-]{11})", url)
    return m.group(1) if m else None

def has_text(s):
    return any(ch.isalpha() for ch in s)

def fetch_comments(url, max_comments=100):
    vid = extract_video_id(url)
    if not vid:
        raise ValueError("Invalid YouTube URL")
    dl = YoutubeCommentDownloader()
    gen = dl.get_comments_from_url(f"https://www.youtube.com/watch?v={vid}")
    out = []
    for c in islice(gen, max_comments * 3):
        if has_text(c["text"]):
            out.append(c["text"])
        if len(out) >= max_comments:
            break
    return vid, out
    