from __future__ import annotations
from typing import Iterable, List
from flask import Blueprint, jsonify, request, render_template
from src import ai_engine
from src.chat_agent import ChatMessage, EpicChatAgent

bp = Blueprint("chat", __name__)  # no prefix here

@bp.get("/chat")  # page at /chat
def chat_page():
    return render_template("chat.html")

def _load_history(messages: Iterable[dict]) -> List[ChatMessage]:
    out: List[ChatMessage] = []
    for raw in messages or []:
        try:
            out.append(ChatMessage.from_mapping(raw))
        except Exception:
            continue
    return out

@bp.post("")
def chat_endpoint():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message") or "").strip()
    if not message:
        return jsonify({"error": "message_required", "message": "Please provide a prompt."}), 400

    agent = EpicChatAgent(history=_load_history(payload.get("history")))
    reply = agent.respond(message)

    return jsonify({
        "reply": reply.to_dict(),
        "history": agent.serialise_history(),
        "mode": "openai" if ai_engine.using_live_model() else "mock",
    })
