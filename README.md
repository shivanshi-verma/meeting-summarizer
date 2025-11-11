# 🧠 Meeting Summarizer

**Author:** [Shivanshi Verma](https://github.com/shivanshi-verma)

A lightweight web app built with **Flask** and **OpenAI GPT** that helps turn meeting transcripts into clear, structured summaries.
It automatically identifies **minutes**, **action items**, and **decisions**, making post-meeting follow-ups easier for teams.

---

## 🌟 Features

✅ Paste or upload meeting transcripts
✅ Generates concise minutes and decisions
✅ Detects action items with owners and due dates
✅ Works even without OpenAI (built-in fallback)
✅ Simple web interface built with Flask
✅ Returns clean JSON output for easy reuse

---

## 🧠 Tech Stack

| Part             | Technology                      |
| ---------------- | ------------------------------- |
| **Language**     | Python 3.11+                    |
| **Framework**    | Flask                           |
| **AI Model**     | OpenAI GPT (ChatCompletion API) |
| **Frontend**     | HTML, CSS, JavaScript           |
| **Offline Mode** | Local rule-based extraction     |

---

## 🚀 Getting Started

```bash
# Clone this repository
git clone https://github.com/shivanshi-verma/meeting-summarizer.git
cd meeting-summarizer

# Install required packages
pip install -r requirements.txt

# (Optional) Set your OpenAI key for GPT-based summaries
export OPENAI_API_KEY="sk-..."        # macOS / Linux
# setx OPENAI_API_KEY "sk-..."        # Windows

# Run the app
python meeting_summarizer.py
```

Once the server starts, open your browser and go to:
👉 **[http://localhost:5000](http://localhost:5000)**

---

## 🧩 Example

**Input:**

```
Alice: We need to finalize the report by Friday.  
Bob: I'll handle the charts and send them tomorrow.  
Charlie: We agreed to postpone the deployment until QA approval.  
Action: Follow-up meeting on Monday. Owner: Alice.
```

**Output:**

```json
{
  "minutes": [
    "Report to be finalized by Friday.",
    "Bob will prepare and share the charts."
  ],
  "action_items": [
    {"task": "Finalize report", "owner": "Alice", "due": "Friday"},
    {"task": "Prepare charts", "owner": "Bob", "due": "Tomorrow"},
    {"task": "Follow-up meeting", "owner": "Alice", "due": "Monday"}
  ],
  "decisions": [
    "Deployment postponed until QA approval."
  ]
}
```

---

## 💻 Fallback Mode

If no `OPENAI_API_KEY` is provided, the app switches to a **local rule-based summarizer**.
It still extracts essential **action items** and **decisions** using pattern-matching and keyword logic — ensuring basic functionality even offline.

---

## 👩‍💻 Author

**Shivanshi Verma**
Interested in **AI**, **IoT**, and **practical automation tools** that make everyday workflows easier.
Built with **Flask** and a touch of **AI magic**, making meetings easier to digest.


