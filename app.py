import os
import re
from collections import Counter
from emoji_utils import predict_with_emoji, prepare_text 

import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from lingualens_core import explain_text
from emoji_utils import predict_with_emoji

API_KEY = os.environ.get("YT_API_KEY")
THRESHOLD = 0.75  # below this top-class confidence -> "Uncertain"

app = Flask(__name__)
CORS(app)


def classify(text):
    res = predict_with_emoji(text)
    label = res["label"]
    if max(res["scores"].values()) < THRESHOLD:
        label = "Uncertain"
    return {"text": text, "label": label, "scores": res["scores"],
            "source": res.get("source", "model")}


def extract_video_id(url):
    m = re.search(r"(?:youtu\.be/|v=|/shorts/|/embed/)([A-Za-z0-9_-]{11})", url)
    if m:
        return m.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url):
        return url
    return None


def fetch_comments(video_id, limit=200):
    yt = build("youtube", "v3", developerKey=API_KEY)
    comments, token = [], None
    while len(comments) < limit:
        res = yt.commentThreads().list(
            part="snippet", videoId=video_id, maxResults=100,
            pageToken=token, textFormat="plainText",
        ).execute()
        comments += [i["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                     for i in res["items"]]
        token = res.get("nextPageToken")
        if not token:
            break
    return comments[:limit]


def get_text():
    data = request.get_json(silent=True) or {}
    text = str(data.get("text", "")).strip()
    return text if text else None


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/")
def home():
    return send_from_directory(".", "index.html")


@app.post("/predict")
def predict():
    text = get_text()
    if not text:
        return jsonify({"error": "Send JSON like {\"text\": \"...\"}"}), 400
    r = classify(text)
    return jsonify({"label": r["label"], "scores": r["scores"], "source": r["source"]})


@app.post("/explain")
def explain():
    text = get_text()
    if not text:
        return jsonify({"error": "Send JSON like {\"text\": \"...\"}"}), 400
    return jsonify(explain_text(prepare_text(text)))


@app.post("/youtube")
def youtube():
    if not API_KEY:
        return jsonify({"error": "Server missing YT_API_KEY environment variable."}), 500
    data = request.get_json(silent=True) or {}
    vid = extract_video_id(str(data.get("url", "")))
    if not vid:
        return jsonify({"error": "Could not find a video ID in that link."}), 400
    try:
        n = min(int(data.get("max_comments", 100)), 500)
    except (TypeError, ValueError):
        n = 100
    try:
        comments = fetch_comments(vid, n)
    except HttpError as e:
        reason = ""
        try:
            reason = e.error_details[0].get("reason", "")
        except Exception:
            pass
        if reason == "commentsDisabled":
            return jsonify({"error": "Comments are disabled on this video."}), 400
        if reason == "videoNotFound":
            return jsonify({"error": "Video not found."}), 404
        return jsonify({"error": f"YouTube API error: {reason or e}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    if not comments:
        return jsonify({"error": "No comments found."}), 400

    results = [classify(c) for c in comments]
    summary = dict(Counter(x["label"] for x in results))
    return jsonify({"video_id": vid, "total": len(results),
                    "summary": summary, "results": results})


@app.post("/csv")
def csv_upload():
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "Upload a CSV with form field 'file'"}), 400
    try:
        df = pd.read_csv(f, encoding="utf-8", on_bad_lines="skip")
    except Exception as e:
        return jsonify({"error": f"Could not read CSV: {e}"}), 400

    col = request.form.get("column")
    if not col or col not in df.columns:
        names = ["comment", "comments", "text", "review", "reviews", "content", "body", "tweet"]
        lower = {c.lower().strip(): c for c in df.columns}
        col = next((lower[n] for n in names if n in lower), None)
        if col is None:
            obj = df.select_dtypes(include="object").columns
            if len(obj) == 0:
                return jsonify({"error": "No text column found"}), 400
            col = obj[0]

    n = min(int(request.form.get("max_rows", 500)), 500)
    texts = [str(t).strip() for t in df[col].dropna().tolist() if str(t).strip()][:n]
    if not texts:
        return jsonify({"error": "No text rows found"}), 400

    results = [classify(t) for t in texts]
    summary = dict(Counter(x["label"] for x in results))
    return jsonify({"column_used": col, "total": len(results),
                    "summary": summary, "results": results})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)