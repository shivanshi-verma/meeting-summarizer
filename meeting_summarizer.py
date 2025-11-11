"""
Meeting Summarizer - Flask app
Author: Shivanshi Verma
"""

import os
import re
import json
import time
from flask import Flask, request, jsonify, render_template_string

# Optional OpenAI usage
USE_OPENAI = bool(os.getenv("OPENAI_API_KEY"))
if USE_OPENAI:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# ---- HTML front-end ----
INDEX_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Meeting Summarizer</title>
  <style>
    body{font-family:Arial,Helvetica,sans-serif;max-width:900px;margin:30px auto;padding:10px}
    textarea{width:100%;height:240px;padding:8px;font-size:14px}
    button{padding:8px 12px;font-size:14px;margin-top:10px}
    pre{white-space:pre-wrap;background:#f7f7f7;padding:12px;border-radius:6px}
  </style>
</head>
<body>
  <h2>Meeting Summarizer</h2>
  <p>Paste meeting transcript or notes below → get minutes, action items, and decisions.</p>
  <form id="f">
    <textarea id="text" placeholder="Paste transcript or notes here..."></textarea><br/>
    <button type="submit">Summarize</button>
  </form>
  <h3>Result</h3>
  <pre id="out">No summary yet.</pre>

<script>
document.getElementById('f').onsubmit = async (e) => {
  e.preventDefault();
  const txt = document.getElementById('text').value;
  if (!txt.trim()) { alert("Paste transcript first."); return; }
  document.getElementById('out').textContent = "Working...";
  const res = await fetch('/summarize', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({text: txt})
  });
  const j = await res.json();
  document.getElementById('out').textContent = JSON.stringify(j, null, 2);
};
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(INDEX_HTML)

# ---- Simple local fallback summarizer ----
def heuristic_extract(text):
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    sentences = re.split(r'(?<=[.!?])\s+', text)
    minutes = sentences[:5]
    action_items, decisions = [], []

    for line in lines:
        if re.search(r'\b(will|action|assign|todo|follow up|owner)\b', line, re.I):
            action_items.append(line)
        if re.search(r'\b(decide|agreed|approved|concluded)\b', line, re.I):
            decisions.append(line)

    return {
        "minutes": minutes,
        "action_items": action_items,
        "decisions": decisions
    }

# ---- OpenAI-based summarizer ----
def gpt_summarize(text):
    prompt = f"""
    You are a meeting assistant.
    Extract:
    - concise minutes (bullets)
    - clear action items (with owners and due dates if present)
    - main decisions.
    Return JSON with keys minutes, action_items, decisions.
    Transcript:
    {text[:6000]}
    """
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            max_tokens=500,
            temperature=0.2
        )
        out = resp.choices[0].message.content.strip()
        return json.loads(out)
    except Exception as e:
        return {"error": str(e), **heuristic_extract(text)}

# ---- Flask endpoint ----
@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json() or {}
    text = data.get("text", "")
    if not text.strip():
        return jsonify({"error": "No text provided"}), 400
    start = time.time()
    result = gpt_summarize(text) if USE_OPENAI else heuristic_extract(text)
    return jsonify({
        "source": "openai" if USE_OPENAI else "heuristic",
        "time_s": round(time.time()-start, 2),
        **result
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
