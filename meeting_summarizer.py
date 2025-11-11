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
  <title>🧠 Meeting Summarizer</title>
  <style>
    :root {
      --bg: #fdfcfb;
      --card-bg: #ffffff;
      --accent: #4b8bf4;
      --text: #2b2b2b;
      --subtle: #6e6e6e;
      --shadow: rgba(0, 0, 0, 0.1);
      --radius: 12px;
    }

    body {
      background: var(--bg);
      font-family: "Inter", "Segoe UI", Arial, Helvetica, sans-serif;
      max-width: 720px;
      margin: 40px auto;
      padding: 20px;
      color: var(--text);
      text-align: center;
    }

    h2 {
      font-size: 2rem;
      margin-bottom: 0.25rem;
      color: var(--text);
    }

    p {
      color: var(--subtle);
      font-size: 1rem;
      margin-bottom: 1.5rem;
    }

    form {
      background: var(--card-bg);
      padding: 2rem 1.5rem;
      border-radius: var(--radius);
      box-shadow: 0 6px 16px var(--shadow);
      transition: 0.3s ease;
    }

    form:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 20px var(--shadow);
    }

    textarea {
      width: 100%;
      height: 240px;
      padding: 0.8rem;
      font-size: 0.95rem;
      border: 1.6px solid #dcdcdc;
      border-radius: var(--radius);
      resize: vertical;
      transition: 0.2s;
    }

    textarea:focus {
      outline: none;
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(75, 139, 244, 0.2);
    }

    button {
      background: var(--accent);
      color: white;
      font-weight: 600;
      border: none;
      border-radius: var(--radius);
      padding: 0.8rem 1.6rem;
      font-size: 1rem;
      cursor: pointer;
      margin-top: 12px;
      transition: all 0.2s ease;
    }

    button:hover {
      background: #357ae8;
      transform: translateY(-1px);
    }

    h3 {
      margin-top: 2rem;
      color: var(--text);
      font-size: 1.25rem;
    }

    pre {
      text-align: left;
      white-space: pre-wrap;
      background: #f7faff;
      padding: 1rem;
      border-radius: var(--radius);
      border: 1px solid #dfe3f0;
      font-family: "Consolas", monospace;
      font-size: 0.9rem;
      line-height: 1.4;
      color: #2b2b2b;
      box-shadow: 0 4px 10px var(--shadow);
    }

    footer {
      margin-top: 3rem;
      font-size: 0.85rem;
      color: var(--subtle);
    }

    footer span {
      color: var(--accent);
      font-weight: 600;
    }
  </style>
</head>
<body>
  <h2>🧠 Meeting Summarizer</h2>
  <p>Paste meeting transcript or notes below → get minutes, action items, and decisions.</p>
  
  <form id="f">
    <textarea id="text" placeholder="Paste transcript or notes here..."></textarea><br/>
    <button type="submit">✨ Summarize</button>
  </form>
  
  <h3>📋 Result</h3>
  <pre id="out">{
  "minutes": [
    "Homepage prototype ready; visuals to be finalized by Wednesday.",
    "User feedback survey will be sent by Friday.",
    "Client meeting rescheduled to next Monday at 10 AM."
  ],
  "action_items": [
    {"task": "Finalize homepage visuals", "owner": "Design team", "due": "Wednesday"},
    {"task": "Send user feedback survey", "owner": "Charlie", "due": "Friday"},
    {"task": "Prepare presentation slides", "owner": "David", "due": "Sunday"},
    {"task": "Schedule follow-up call", "owner": "Alice", "due": "Tuesday"}
  ],
  "decisions": [
    "Feature rollout postponed until after QA approval next week."
  ]
}
</pre>

  <footer>Built with <span>Flask</span> & 💡 by <span>Shivanshi Verma</span></footer>

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
