import os
import io
import csv
import json
import re

from flask import (
    Flask, render_template, request, redirect, url_for, flash,
    send_file, jsonify, abort
)

from models.nlp_engine import analyze_comment
from models.bias_audit import audit
from database import db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
MAX_COMMENTS = 5000  # NFR: Performance — batch cap per SRS

app = Flask(__name__)
app.secret_key = "lingualens-dev-secret"  # dev only; use env var in production
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB upload cap

YOUTUBE_URL_RE = re.compile(
    r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)([\w-]{11})"
)


def get_youtube_video_id(url):
    m = YOUTUBE_URL_RE.search(url or "")
    return m.group(1) if m else None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    """FR1: Data Ingestion — CSV upload or YouTube URL."""
    source_type = request.form.get("source_type", "csv")

    rows = []  # list of raw comment strings
    source_ref = None

    if source_type == "youtube":
        yt_url = request.form.get("youtube_url", "").strip()
        video_id = get_youtube_video_id(yt_url)
        if not video_id:
            flash("That doesn't look like a valid YouTube video URL.", "error")
            return redirect(url_for("index"))
        # NOTE: Live YouTube Data API v3 fetching requires a server-side API
        # key (SRS Security requirement: "never exposed in client-side
        # code"). This prototype does not ship a key, so we generate a
        # clearly-labelled sample comment set for the given video so the
        # rest of the pipeline (FR2-FR5) can be demoed end-to-end. Swap in
        # a real `youtube.commentThreads().list()` call here once a key is
        # configured via the YOUTUBE_API_KEY environment variable.
        rows = _demo_youtube_comments(video_id)
        source_ref = yt_url
    else:
        file = request.files.get("csv_file")
        if not file or file.filename == "":
            flash("Please choose a CSV file to upload.", "error")
            return redirect(url_for("index"))
        if not file.filename.lower().endswith(".csv"):
            flash("Only .csv files are supported.", "error")
            return redirect(url_for("index"))
        try:
            stream = io.StringIO(file.stream.read().decode("utf-8-sig"), newline=None)
            reader = csv.DictReader(stream)
            col = None
            if reader.fieldnames:
                for candidate in ("comment", "review", "text", "Comment", "Review", "Text"):
                    if candidate in reader.fieldnames:
                        col = candidate
                        break
                if col is None:
                    col = reader.fieldnames[0]
            for r in reader:
                val = (r.get(col) or "").strip()
                if val:
                    rows.append(val)
        except Exception as e:
            flash(f"Could not parse CSV: {e}", "error")
            return redirect(url_for("index"))
        source_ref = file.filename

    if not rows:
        flash("No usable comments found in the input.", "error")
        return redirect(url_for("index"))

    if len(rows) > MAX_COMMENTS:
        flash(f"Input has {len(rows)} comments; only processing the first {MAX_COMMENTS}.", "error")
        rows = rows[:MAX_COMMENTS]

    results = []
    for raw in rows:
        r = analyze_comment(raw)
        r["raw_text"] = raw
        results.append(r)

    bias_result = audit(results)
    analysis_id = db.save_analysis(source_type, source_ref, results, bias_result)

    return redirect(url_for("dashboard", analysis_id=analysis_id))


def _demo_youtube_comments(video_id):
    """Placeholder comment generator so the pipeline is demoable without a
    live YouTube Data API key. Clearly a stand-in — see comment above."""
    return [
        "This video is semma nalla, really enjoyed it!",
        "bakwaas video, waste of time honestly",
        "adipoli content da, keep it up!",
        "not bad but could be better",
        "baagundi ra explanation, chala helpful",
        "worst editing ever, so boring",
        "romba informative video, thanks!",
        "mosham quality audio, couldn't hear anything",
        "This is amazing, loved every part of it",
        "kevalam, don't waste your time on this",
        "kollam presentation, well done team",
        "faltu content, expected more from this channel",
        "great explanation, very clear and simple",
        "ghatiya thumbnail but decent video overall",
        "zabardast! ekdum mast tha yeh video",
    ]


@app.route("/dashboard/<int:analysis_id>")
def dashboard(analysis_id):
    analysis, comments = db.get_analysis(analysis_id)
    if not analysis:
        abort(404)

    language_counts, emotion_counts, sentiment_counts = {}, {}, {"Positive": 0, "Negative": 0, "Neutral": 0}
    for c in comments:
        language_counts[c["language"]] = language_counts.get(c["language"], 0) + 1
        emotion_counts[c["emotion"]] = emotion_counts.get(c["emotion"], 0) + 1
        sentiment_counts[c["sentiment"]] = sentiment_counts.get(c["sentiment"], 0) + 1

    top_positive = sorted(
        [c for c in comments if c["sentiment"] == "Positive"],
        key=lambda x: x["confidence"], reverse=True
    )[:5]
    top_negative = sorted(
        [c for c in comments if c["sentiment"] == "Negative"],
        key=lambda x: x["confidence"], reverse=True
    )[:5]

    bias_result = audit(comments)  # recompute for display (per_language table)

    return render_template(
        "dashboard.html",
        analysis=analysis,
        comments=comments,
        language_counts=language_counts,
        emotion_counts=emotion_counts,
        sentiment_counts=sentiment_counts,
        top_positive=top_positive,
        top_negative=top_negative,
        bias=bias_result,
    )


@app.route("/history")
def history():
    analyses = db.list_analyses()
    return render_template("history.html", analyses=analyses)


@app.route("/history/delete/<int:analysis_id>", methods=["POST"])
def delete_history(analysis_id):
    db.delete_analysis(analysis_id)
    flash("Analysis deleted.", "success")
    return redirect(url_for("history"))


@app.route("/export/<int:analysis_id>")
def export_csv(analysis_id):
    analysis, comments = db.get_analysis(analysis_id)
    if not analysis:
        abort(404)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["comment", "language", "sentiment", "confidence", "emotion", "uncertain"])
    for c in comments:
        writer.writerow([
            c["raw_text"], c["language"], c["sentiment"],
            c["confidence"], c["emotion"], bool(c["is_uncertain"])
        ])
    buf.seek(0)
    return send_file(
        io.BytesIO(buf.getvalue().encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"lingualens_analysis_{analysis_id}.csv",
    )


@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", message="Analysis not found."), 404


@app.errorhandler(413)
def too_large(e):
    flash("File too large (max 10 MB).", "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    db.init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
