"""
app.py — local Flask server. Serves the frontend and exposes the pipeline
as a simple job API. Run with: python app.py  (see README.md)
"""

import os
import sys
import threading
import traceback
import uuid

from flask import Flask, request, jsonify, send_from_directory, send_file

sys.path.insert(0, os.path.dirname(__file__))
from src.pipeline.job_runner import run_job, JOBS_DIR

app = Flask(__name__, static_folder="static", static_url_path="")

# in-memory job registry (fine for a single-user local tool)
JOBS = {}


def _run_job_background(job_id, topic, script_text, item_a, item_b):
    JOBS[job_id] = {"status": "running", "error": None, "video_path": None}
    try:
        result = run_job(topic=topic, script_text=script_text,
                          item_a=item_a, item_b=item_b)
        JOBS[job_id] = {"status": "done", "error": None,
                         "video_path": result.video_path, "real_job_id": result.job_id}
    except Exception as e:
        JOBS[job_id] = {"status": "failed", "error": str(e), "video_path": None}
        traceback.print_exc()


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json(force=True)
    topic = (data.get("topic") or "").strip()
    script_text = (data.get("script") or "").strip()
    item_a = (data.get("item_a") or "").strip()
    item_b = (data.get("item_b") or "").strip()

    if not script_text:
        return jsonify({"error": "Script is required."}), 400

    job_id = uuid.uuid4().hex[:10]
    thread = threading.Thread(target=_run_job_background,
                               args=(job_id, topic, script_text, item_a, item_b),
                               daemon=True)
    thread.start()
    JOBS[job_id] = {"status": "running", "error": None, "video_path": None}
    return jsonify({"job_id": job_id})


@app.route("/api/status/<job_id>")
def status(job_id):
    job = JOBS.get(job_id)
    if not job:
        return jsonify({"error": "unknown job_id"}), 404
    return jsonify({"status": job["status"], "error": job["error"]})


@app.route("/api/download/<job_id>")
def download(job_id):
    job = JOBS.get(job_id)
    if not job or job["status"] != "done":
        return jsonify({"error": "video not ready"}), 404
    return send_file(job["video_path"], mimetype="video/mp4")


if __name__ == "__main__":
    os.makedirs(JOBS_DIR, exist_ok=True)
    app.run(host="127.0.0.1", port=5000, debug=False)
