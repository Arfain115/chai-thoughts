import json
import os
import threading
import uuid
import webbrowser
from datetime import datetime

import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template_string, make_response

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")
os.makedirs(DATA_DIR, exist_ok=True)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-3.1-flash-lite"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

COOKIE_NAME = "chai_uid"
COOKIE_MAX_AGE = 60 * 60 * 24 * 365 * 5  # 5 years, so it survives closing the site

app = Flask(__name__)

PAGE = """<!doctype html>
<html><head><meta charset="utf-8">
<title>chai thoughts</title>
<style>
  * { box-sizing: border-box; }
  body { margin:0; display:flex; height:100vh; font-family: -apple-system, Segoe UI, sans-serif; background:#0d0d0d; color:#eaeaea; }

  #sidebar { width:300px; border-right:1px solid #242424; padding:18px; display:flex; flex-direction:column; }
  #sidebar h2 { font-size:15px; margin:0 0 20px; color:#eee; }
  #analyzeBtn { padding:10px 14px; border-radius:8px; border:1px solid #333; background:#1a1a1a; color:#888; font-size:13px; cursor:not-allowed; text-align:left; }
  #analyzeBtn.ready { color:#eaeaea; cursor:pointer; border-color:#444; }
  #analyzeBtn.ready:hover { background:#222; }
  #analysis { margin-top:16px; font-size:13px; line-height:1.6; color:#bbb; white-space:pre-wrap; }
  #hint { font-size:11px; color:#555; margin-top:8px; }

  #main { flex:1; display:flex; flex-direction:column; }
  #chatArea { flex:1; overflow-y:auto; padding:32px 24px 12px; display:flex; flex-direction:column; gap:10px; }
  .bubble { align-self:flex-end; background:#1c1c1c; border:1px solid #2a2a2a; padding:10px 14px; border-radius:14px 14px 2px 14px; max-width:60%; font-size:14px; }

  #inputBar { padding:20px 24px 28px; display:flex; justify-content:center; }
  #entry { width:100%; max-width:600px; padding:14px 18px; font-size:16px; background:#161616; border:1px solid #2a2a2a; border-radius:24px; color:#eaeaea; outline:none; }
  #entry:focus { border-color:#555; }

  #chaiOverlay { position:fixed; inset:0; display:flex; align-items:center; justify-content:center; flex-direction:column; pointer-events:none; opacity:0; }
  #chaiOverlay.show { animation: chaiPop 1.4s ease; }
  #chaiOverlay .emoji { font-size:64px; }
  #chaiOverlay .msg { margin-top:8px; font-size:15px; color:#eee; background:#000a; padding:6px 14px; border-radius:20px; }
  @keyframes chaiPop {
    0%   { opacity:0; transform: scale(0.8) translateY(10px); }
    20%  { opacity:1; transform: scale(1) translateY(0); }
    80%  { opacity:1; }
    100% { opacity:0; transform: scale(0.95) translateY(-10px); }
  }
</style></head>
<body>

  <div id="sidebar">
    <h2>chai thoughts</h2>
    <div id="analyzeBtn">analyze your thoughts</div>
    <div id="hint">{{ hint }}</div>
    <div id="analysis"></div>
  </div>

  <div id="main">
    <div id="chatArea">
      {% for e in entries %}<div class="bubble">{{ e }}</div>{% endfor %}
    </div>
    <div id="inputBar">
      <input id="entry" type="text" placeholder="what's on your mind?" autocomplete="off" autofocus>
    </div>
  </div>

  <div id="chaiOverlay">
    <div class="emoji">🍵</div>
    <div class="msg">enjoy your chai</div>
  </div>

<script>
const input = document.getElementById('entry');
const chatArea = document.getElementById('chatArea');
const overlay = document.getElementById('chaiOverlay');
const analyzeBtn = document.getElementById('analyzeBtn');
const analysisBox = document.getElementById('analysis');
const hint = document.getElementById('hint');

let count = {{ entries|length }};

function refreshAnalyzeState() {
  if (count >= 3) {
    analyzeBtn.classList.add('ready');
    hint.textContent = '';
  } else {
    analyzeBtn.classList.remove('ready');
    hint.textContent = `log ${3 - count} more to unlock`;
  }
}
refreshAnalyzeState();
chatArea.scrollTop = chatArea.scrollHeight;

input.addEventListener('keydown', async (e) => {
  if (e.key === 'Enter' && input.value.trim()) {
    const text = input.value.trim();
    input.value = '';

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = text;
    chatArea.appendChild(bubble);
    chatArea.scrollTop = chatArea.scrollHeight;

    overlay.classList.remove('show');
    void overlay.offsetWidth;
    overlay.classList.add('show');

    await fetch('/log', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({text})
    });

    count++;
    refreshAnalyzeState();
  }
});

analyzeBtn.addEventListener('click', async () => {
  if (count < 3) return;
  analysisBox.textContent = 'thinking...';
  const res = await fetch('/analyze', { method: 'POST' });
  const data = await res.json();
  analysisBox.textContent = data.result || data.error || 'something went wrong.';
});
</script>
</body></html>"""


def log_path_for(uid):
    return os.path.join(DATA_DIR, f"{uid}.jsonl")


def load_entries(uid):
    path = log_path_for(uid)
    if not os.path.exists(path):
        return []
    entries = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def get_uid():
    return request.cookies.get(COOKIE_NAME)


@app.route("/")
def index():
    uid = get_uid()
    new_uid = uid is None
    if new_uid:
        uid = str(uuid.uuid4())

    entries = load_entries(uid)
    texts = [e["text"] for e in entries]
    hint_text = "" if len(texts) >= 3 else f"log {3 - len(texts)} more to unlock"

    resp = make_response(render_template_string(PAGE, entries=texts, hint=hint_text))
    if new_uid:
        resp.set_cookie(COOKIE_NAME, uid, max_age=COOKIE_MAX_AGE, httponly=True, samesite="Lax")
    return resp


@app.route("/log", methods=["POST"])
def log():
    uid = get_uid()
    if not uid:
        return jsonify({"ok": False, "error": "no session"}), 400

    data = request.get_json()
    text = (data.get("text") or "").strip()
    if text:
        entry = {"timestamp": datetime.now().isoformat(timespec="seconds"), "text": text}
        with open(log_path_for(uid), "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return jsonify({"ok": True})


def trim_to_words(text, limit=30):
    words = text.split()
    if len(words) <= limit:
        return text
    return " ".join(words[:limit]).rstrip(",.;:") + "..."


@app.route("/analyze", methods=["POST"])
def analyze():
    uid = get_uid()
    if not uid:
        return jsonify({"error": "no session"}), 400

    if not GEMINI_API_KEY:
        return jsonify({"error": "no GEMINI_API_KEY set on the server."}), 400

    entries = load_entries(uid)
    texts = [e["text"] for e in entries]
    if len(texts) < 3:
        return jsonify({"error": "log a few more entries first."}), 400

    joined = "\n".join(f"- {t}" for t in texts)
    prompt = (
        "Here are someone's short daily journal entries, one per chai break:\n\n"
        f"{joined}\n\n"
        "In one short sentence, reflect back a recurring theme you notice. "
        "Stay honest, but lean toward a warm, encouraging, positive framing where the "
        "entries genuinely allow it — don't invent positivity that isn't there. "
        "No jargon, no clinical language. "
        "HARD LIMIT: under 30 words, no exceptions. Just the sentence, nothing else."
    )

    try:
        resp = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        result = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        result = trim_to_words(result, 30)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": f"couldn't reach Gemini: {e}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    is_hosted = bool(os.environ.get("RENDER") or os.environ.get("SPACE_ID") or os.environ.get("PORT"))
    if not is_hosted:
        threading.Timer(1.0, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
    app.run(host="0.0.0.0", port=port, debug=False)
