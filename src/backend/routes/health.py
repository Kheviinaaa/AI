from flask import Blueprint, jsonify
import time

bp = Blueprint("health", __name__)
_start = time.time()

@bp.get("/health")
def health():
    uptime = round(time.time() - _start, 2)
    return jsonify({"status": "ok", "uptime_sec": uptime})

