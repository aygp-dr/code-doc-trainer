"""CodeDocumentationTrainer - challenges users to write documentation for code snippets and scores them."""
import json
import os
import re
import sqlite3
from datetime import datetime

from flask import Flask, g, jsonify, render_template_string, request

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key-change-in-production")

DB_PATH = os.path.join("data", "app.db")

# ---------------------------------------------------------------------------
# Code Snippets
# ---------------------------------------------------------------------------

SNIPPETS = [
    {
        "id": 1,
        "title": "Binary Search",
        "language": "python",
        "code": '''def binary_search(arr, target):
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1''',
        "keywords": ["sorted", "array", "list", "target", "index", "return", "int", "-1", "not found",
                      "O(log n)", "logarithmic", "mid", "binary"],
        "has_params": ["arr", "target"],
        "has_return": True,
        "has_raises": False,
    },
    {
        "id": 2,
        "title": "Flatten Nested List",
        "language": "python",
        "code": '''def flatten(nested):
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result''',
        "keywords": ["nested", "list", "recursive", "recursion", "flatten", "return", "list",
                      "extend", "append", "isinstance"],
        "has_params": ["nested"],
        "has_return": True,
        "has_raises": False,
    },
    {
        "id": 3,
        "title": "Memoize Decorator",
        "language": "python",
        "code": '''def memoize(func):
    cache = {}
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper''',
        "keywords": ["decorator", "cache", "memoize", "memoization", "function", "wrapper",
                      "args", "arguments", "return", "performance", "dict", "dictionary"],
        "has_params": ["func"],
        "has_return": True,
        "has_raises": False,
    },
    {
        "id": 4,
        "title": "Retry with Backoff",
        "language": "python",
        "code": '''import time

def retry(func, max_attempts=3, backoff=2):
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            time.sleep(backoff ** attempt)''',
        "keywords": ["retry", "attempt", "exception", "error", "backoff", "exponential",
                      "sleep", "max", "raise", "try", "except", "callable"],
        "has_params": ["func", "max_attempts", "backoff"],
        "has_return": True,
        "has_raises": True,
    },
    {
        "id": 5,
        "title": "LRU Cache",
        "language": "python",
        "code": '''from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key):
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)''',
        "keywords": ["LRU", "cache", "least recently used", "capacity", "evict", "OrderedDict",
                      "key", "value", "get", "put", "-1", "not found"],
        "has_params": ["capacity"],
        "has_return": True,
        "has_raises": False,
    },
    {
        "id": 6,
        "title": "Matrix Transpose",
        "language": "python",
        "code": '''def transpose(matrix):
    if not matrix or not matrix[0]:
        return []
    rows, cols = len(matrix), len(matrix[0])
    return [[matrix[r][c] for r in range(rows)] for c in range(cols)]''',
        "keywords": ["matrix", "transpose", "rows", "columns", "2D", "list", "return",
                      "swap", "empty", "nested"],
        "has_params": ["matrix"],
        "has_return": True,
        "has_raises": False,
    },
    {
        "id": 7,
        "title": "Rate Limiter",
        "language": "python",
        "code": '''import time

class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.calls = []

    def allow(self):
        now = time.time()
        self.calls = [t for t in self.calls if now - t < self.period]
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False''',
        "keywords": ["rate", "limit", "limiter", "calls", "period", "time", "window",
                      "max", "allow", "throttle", "boolean", "True", "False"],
        "has_params": ["max_calls", "period"],
        "has_return": True,
        "has_raises": False,
    },
    {
        "id": 8,
        "title": "Merge Sorted Lists",
        "language": "python",
        "code": '''def merge_sorted(list1, list2):
    result = []
    i = j = 0
    while i < len(list1) and j < len(list2):
        if list1[i] <= list2[j]:
            result.append(list1[i])
            i += 1
        else:
            result.append(list2[j])
            j += 1
    result.extend(list1[i:])
    result.extend(list2[j:])
    return result''',
        "keywords": ["merge", "sorted", "list", "two", "pointer", "combine", "order",
                      "return", "O(n)", "linear", "compare"],
        "has_params": ["list1", "list2"],
        "has_return": True,
        "has_raises": False,
    },
    {
        "id": 9,
        "title": "CSV Parser",
        "language": "python",
        "code": '''def parse_csv(text, delimiter=","):
    rows = []
    for line in text.strip().split("\\n"):
        fields = []
        current = ""
        in_quotes = False
        for char in line:
            if char == '"':
                in_quotes = not in_quotes
            elif char == delimiter and not in_quotes:
                fields.append(current.strip())
                current = ""
            else:
                current += char
        fields.append(current.strip())
        rows.append(fields)
    return rows''',
        "keywords": ["CSV", "parse", "delimiter", "comma", "quote", "quoted", "fields",
                      "rows", "text", "string", "return", "list"],
        "has_params": ["text", "delimiter"],
        "has_return": True,
        "has_raises": False,
    },
    {
        "id": 10,
        "title": "Event Emitter",
        "language": "python",
        "code": '''class EventEmitter:
    def __init__(self):
        self._listeners = {}

    def on(self, event, callback):
        self._listeners.setdefault(event, []).append(callback)

    def emit(self, event, *args):
        for callback in self._listeners.get(event, []):
            callback(*args)

    def off(self, event, callback):
        if event in self._listeners:
            self._listeners[event] = [
                cb for cb in self._listeners[event] if cb != callback
            ]''',
        "keywords": ["event", "emitter", "listener", "callback", "subscribe", "publish",
                      "on", "off", "emit", "pattern", "observer"],
        "has_params": ["event", "callback"],
        "has_return": False,
        "has_raises": False,
    },
]

SNIPPETS_BY_ID = {s["id"]: s for s in SNIPPETS}

# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def score_documentation(snippet, doc_text):
    """Score user documentation on four dimensions (0-25 each, 100 total)."""
    doc_lower = doc_text.lower()
    doc_words = set(re.findall(r'\w+', doc_lower))

    # --- Completeness (0-25): covers params, return, raises, purpose ---
    completeness = 0
    # Mentions parameters
    params_mentioned = sum(1 for p in snippet["has_params"] if p.lower() in doc_lower)
    if snippet["has_params"]:
        completeness += int(10 * params_mentioned / len(snippet["has_params"]))
    else:
        completeness += 10
    # Mentions return value
    if snippet["has_return"]:
        if any(w in doc_lower for w in ["return", "returns", "output", "result"]):
            completeness += 8
    else:
        completeness += 8
    # Mentions exceptions/raises
    if snippet["has_raises"]:
        if any(w in doc_lower for w in ["raise", "raises", "exception", "error", "throw"]):
            completeness += 7
        # partial if they mention error handling at all
        elif any(w in doc_lower for w in ["fail", "failure", "retry"]):
            completeness += 4
    else:
        completeness += 7
    completeness = min(25, completeness)

    # --- Accuracy (0-25): uses relevant keywords ---
    keyword_hits = sum(1 for kw in snippet["keywords"] if kw.lower() in doc_lower)
    keyword_ratio = keyword_hits / max(len(snippet["keywords"]), 1)
    accuracy = min(25, int(keyword_ratio * 30))

    # --- Clarity (0-25): length, structure, sentences ---
    clarity = 0
    word_count = len(doc_text.split())
    # Reasonable length (not too short, not excessively long)
    if 20 <= word_count <= 500:
        clarity += 10
    elif 10 <= word_count < 20:
        clarity += 5
    elif word_count > 500:
        clarity += 6
    # Has sentence structure (periods)
    sentences = doc_text.count('.') + doc_text.count(':')
    if sentences >= 2:
        clarity += 8
    elif sentences >= 1:
        clarity += 4
    # Has structure markers (sections, colons, dashes)
    if any(marker in doc_text for marker in ["Args:", "Parameters:", "Returns:", "Raises:",
                                              "Example:", "Note:", "param", "return"]):
        clarity += 7
    elif any(marker in doc_text for marker in ["-", "*", "•", "\n"]):
        clarity += 4
    clarity = min(25, clarity)

    # --- Examples (0-25): includes usage examples ---
    examples = 0
    has_example_header = any(w in doc_lower for w in ["example", "usage", ">>> ", "e.g."])
    has_code_pattern = bool(re.search(r'(>>>|\.\.\.|\w+\(.*\))', doc_text))
    has_expected_output = bool(re.search(r'#\s*\w+|==|output|result', doc_lower))
    if has_example_header:
        examples += 10
    if has_code_pattern:
        examples += 10
    if has_expected_output:
        examples += 5
    examples = min(25, examples)

    total = completeness + accuracy + clarity + examples
    return {
        "completeness": completeness,
        "accuracy": accuracy,
        "clarity": clarity,
        "examples": examples,
        "total": total,
    }


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------


def get_db():
    if "db" not in g:
        os.makedirs("data", exist_ok=True)
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("""CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            snippet_id INTEGER NOT NULL,
            documentation TEXT NOT NULL,
            score_completeness INTEGER DEFAULT 0,
            score_accuracy INTEGER DEFAULT 0,
            score_clarity INTEGER DEFAULT 0,
            score_examples INTEGER DEFAULT 0,
            score_total INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        g.db.commit()
    return g.db


@app.teardown_appcontext
def close_db(e=None):
    db = g.pop("db", None)
    if db:
        db.close()


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

BASE_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'SF Mono',SFMono-Regular,Consolas,'Liberation Mono',Menlo,monospace;
     background:#0d1117;color:#c9d1d9;line-height:1.6}
a{color:#58a6ff;text-decoration:none}
a:hover{text-decoration:underline}
.container{max-width:900px;margin:0 auto;padding:20px}
h1{color:#58a6ff;margin-bottom:4px;font-size:1.5em}
h2{color:#58a6ff;margin:16px 0 8px;font-size:1.2em}
.subtitle{color:#8b949e;margin-bottom:24px;font-size:0.9em}
.card{border:1px solid #30363d;border-radius:8px;padding:16px;margin:12px 0;background:#161b22}
.btn{display:inline-block;padding:8px 20px;border:1px solid #30363d;background:#238636;
     color:#fff;border-radius:6px;cursor:pointer;font-size:14px;font-family:inherit}
.btn:hover{background:#2ea043}
.btn-secondary{background:#21262d;color:#c9d1d9}
.btn-secondary:hover{background:#30363d}
input,textarea,select{background:#0d1117;color:#c9d1d9;border:1px solid #30363d;
     border-radius:6px;padding:8px 12px;width:100%;margin:4px 0;font-family:inherit;font-size:14px}
textarea{min-height:200px;resize:vertical}
pre{background:#0d1117;border:1px solid #30363d;border-radius:6px;padding:16px;
    overflow-x:auto;font-size:13px;line-height:1.5;color:#e6edf3}
code{font-family:'SF Mono',SFMono-Regular,Consolas,'Liberation Mono',Menlo,monospace}
nav{background:#161b22;border-bottom:1px solid #30363d;padding:10px 20px;margin-bottom:20px}
nav a{margin-right:20px;color:#8b949e;font-size:14px}
nav a:hover,nav a.active{color:#58a6ff;text-decoration:none}
.score-bar{height:8px;border-radius:4px;background:#21262d;margin:4px 0;overflow:hidden}
.score-fill{height:100%;border-radius:4px;transition:width 0.3s}
.score-fill.high{background:#238636}
.score-fill.mid{background:#d29922}
.score-fill.low{background:#da3633}
.score-label{display:flex;justify-content:space-between;font-size:13px;color:#8b949e}
.badge{display:inline-block;padding:2px 8px;border-radius:12px;font-size:12px;font-weight:600}
.badge-gold{background:#d29922;color:#0d1117}
.badge-silver{background:#8b949e;color:#0d1117}
.badge-bronze{background:#a0522d;color:#fff}
table{width:100%;border-collapse:collapse;margin:8px 0}
th,td{text-align:left;padding:10px 12px;border-bottom:1px solid #21262d;font-size:14px}
th{color:#8b949e;font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:0.5px}
tr:hover{background:#161b22}
.snippet-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}
.snippet-card{border:1px solid #30363d;border-radius:8px;padding:16px;background:#161b22;
     transition:border-color 0.2s}
.snippet-card:hover{border-color:#58a6ff}
.snippet-card h3{font-size:14px;color:#e6edf3;margin-bottom:4px}
.snippet-card p{font-size:12px;color:#8b949e}
.flash{padding:12px 16px;border-radius:6px;margin:12px 0;font-size:14px}
.flash-success{background:#0f2d1a;border:1px solid #238636;color:#3fb950}
.flash-error{background:#2d0f0f;border:1px solid #da3633;color:#f85149}
"""

NAV_HTML = """
<nav>
  <a href="/" {% if active=='home' %}class="active"{% endif %}>Snippets</a>
  <a href="/leaderboard" {% if active=='leaderboard' %}class="active"{% endif %}>Leaderboard</a>
  <a href="/api/snippets" {% if active=='api' %}class="active"{% endif %}>API</a>
</nav>
"""

HOME_TEMPLATE = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CodeDocumentationTrainer</title>
<style>""" + BASE_CSS + """</style>
</head><body>
""" + NAV_HTML.replace("active=='home'", "True") + """
<div class="container">
<h1>CodeDocumentationTrainer</h1>
<p class="subtitle">Write documentation for code snippets and get scored on completeness, accuracy, clarity, and examples.</p>
<div class="snippet-grid">
{% for s in snippets %}
<a href="/snippet/{{ s.id }}" class="snippet-card" style="text-decoration:none">
  <h3>#{{ s.id }} &mdash; {{ s.title }}</h3>
  <p>{{ s.language | upper }} &middot; {{ s.code.split('\\n') | length }} lines</p>
</a>
{% endfor %}
</div>
</div></body></html>"""

SNIPPET_TEMPLATE = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ snippet.title }} - CodeDocumentationTrainer</title>
<style>""" + BASE_CSS + """</style>
</head><body>
""" + NAV_HTML.replace("active=='home'", "True") + """
<div class="container">
<h1>#{{ snippet.id }} &mdash; {{ snippet.title }}</h1>
<p class="subtitle">Write comprehensive documentation for this {{ snippet.language }} code.</p>

<div class="card">
<pre><code>{{ snippet.code }}</code></pre>
</div>

{% if result %}
<div class="card">
  <h2>Score: {{ result.total }} / 100</h2>
  {% for dim in ['completeness', 'accuracy', 'clarity', 'examples'] %}
  <div style="margin:8px 0">
    <div class="score-label">
      <span>{{ dim | capitalize }}</span>
      <span>{{ result[dim] }} / 25</span>
    </div>
    <div class="score-bar">
      <div class="score-fill {% if result[dim] >= 18 %}high{% elif result[dim] >= 10 %}mid{% else %}low{% endif %}"
           style="width:{{ (result[dim] / 25 * 100) | int }}%"></div>
    </div>
  </div>
  {% endfor %}
</div>
{% endif %}

<form method="POST" style="margin-top:16px">
  <div style="margin-bottom:8px">
    <label for="username" style="font-size:13px;color:#8b949e">Username</label>
    <input name="username" id="username" placeholder="your-name" required
           value="{{ request.form.get('username', '') }}" style="max-width:300px">
  </div>
  <div style="margin-bottom:8px">
    <label for="documentation" style="font-size:13px;color:#8b949e">Your Documentation</label>
    <textarea name="documentation" id="documentation" required
              placeholder="Write a docstring or documentation for the code above...&#10;&#10;Include:&#10;- Description of what it does&#10;- Parameters and their types&#10;- Return value&#10;- Usage examples">{{ request.form.get('documentation', '') }}</textarea>
  </div>
  <button type="submit" class="btn">Submit &amp; Score</button>
  <a href="/" class="btn btn-secondary" style="margin-left:8px">Back</a>
</form>

{% if recent %}
<h2 style="margin-top:24px">Recent Submissions</h2>
{% for sub in recent %}
<div class="card">
  <div style="display:flex;justify-content:space-between;align-items:center">
    <strong>{{ sub.username }}</strong>
    <span style="color:#58a6ff;font-weight:600">{{ sub.score_total }} / 100</span>
  </div>
  <div style="font-size:12px;color:#8b949e;margin-top:4px">{{ sub.created_at }}</div>
</div>
{% endfor %}
{% endif %}
</div></body></html>"""

LEADERBOARD_TEMPLATE = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Leaderboard - CodeDocumentationTrainer</title>
<style>""" + BASE_CSS + """</style>
</head><body>
""" + NAV_HTML.replace("active=='leaderboard'", "True") + """
<div class="container">
<h1>Leaderboard</h1>
<p class="subtitle">Top documentation scores across all snippets.</p>

{% if leaders %}
<div class="card" style="overflow-x:auto">
<table>
<thead>
<tr><th>#</th><th>User</th><th>Snippet</th><th>Completeness</th><th>Accuracy</th><th>Clarity</th><th>Examples</th><th>Total</th><th>Date</th></tr>
</thead>
<tbody>
{% for row in leaders %}
<tr>
  <td>{% if loop.index == 1 %}<span class="badge badge-gold">1</span>
      {% elif loop.index == 2 %}<span class="badge badge-silver">2</span>
      {% elif loop.index == 3 %}<span class="badge badge-bronze">3</span>
      {% else %}{{ loop.index }}{% endif %}</td>
  <td>{{ row.username }}</td>
  <td><a href="/snippet/{{ row.snippet_id }}">#{{ row.snippet_id }}</a></td>
  <td>{{ row.score_completeness }}</td>
  <td>{{ row.score_accuracy }}</td>
  <td>{{ row.score_clarity }}</td>
  <td>{{ row.score_examples }}</td>
  <td style="color:#58a6ff;font-weight:600">{{ row.score_total }}</td>
  <td style="font-size:12px;color:#8b949e">{{ row.created_at }}</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>
{% else %}
<div class="card"><p style="color:#8b949e">No submissions yet. <a href="/">Start documenting!</a></p></div>
{% endif %}
</div></body></html>"""

# ---------------------------------------------------------------------------
# Web Routes
# ---------------------------------------------------------------------------


@app.route("/")
def index():
    return render_template_string(HOME_TEMPLATE, snippets=SNIPPETS, active="home")


@app.route("/snippet/<int:snippet_id>", methods=["GET", "POST"])
def snippet_view(snippet_id):
    snippet = SNIPPETS_BY_ID.get(snippet_id)
    if not snippet:
        return "Snippet not found", 404

    result = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        documentation = request.form.get("documentation", "").strip()
        if username and documentation:
            result = score_documentation(snippet, documentation)
            db = get_db()
            db.execute(
                """INSERT INTO submissions
                   (username, snippet_id, documentation, score_completeness,
                    score_accuracy, score_clarity, score_examples, score_total)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (username, snippet_id, documentation,
                 result["completeness"], result["accuracy"],
                 result["clarity"], result["examples"], result["total"]),
            )
            db.commit()

    db = get_db()
    recent = db.execute(
        "SELECT * FROM submissions WHERE snippet_id = ? ORDER BY created_at DESC LIMIT 10",
        (snippet_id,),
    ).fetchall()

    return render_template_string(
        SNIPPET_TEMPLATE, snippet=snippet, result=result, recent=recent, active="home",
    )


@app.route("/leaderboard")
def leaderboard():
    db = get_db()
    leaders = db.execute(
        "SELECT * FROM submissions ORDER BY score_total DESC, created_at ASC LIMIT 50"
    ).fetchall()
    return render_template_string(LEADERBOARD_TEMPLATE, leaders=leaders, active="leaderboard")


# ---------------------------------------------------------------------------
# JSON API
# ---------------------------------------------------------------------------


@app.route("/api/snippets")
def api_snippets():
    return jsonify([{"id": s["id"], "title": s["title"], "language": s["language"],
                     "code": s["code"]} for s in SNIPPETS])


@app.route("/api/snippets/<int:snippet_id>")
def api_snippet(snippet_id):
    snippet = SNIPPETS_BY_ID.get(snippet_id)
    if not snippet:
        return jsonify({"error": "not found"}), 404
    return jsonify({"id": snippet["id"], "title": snippet["title"],
                    "language": snippet["language"], "code": snippet["code"]})


@app.route("/api/submit", methods=["POST"])
def api_submit():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    snippet_id = data.get("snippet_id")
    username = (data.get("username") or "").strip()
    documentation = (data.get("documentation") or "").strip()

    if not snippet_id or not username or not documentation:
        return jsonify({"error": "snippet_id, username, and documentation are required"}), 400

    snippet = SNIPPETS_BY_ID.get(snippet_id)
    if not snippet:
        return jsonify({"error": "snippet not found"}), 404

    result = score_documentation(snippet, documentation)

    db = get_db()
    cursor = db.execute(
        """INSERT INTO submissions
           (username, snippet_id, documentation, score_completeness,
            score_accuracy, score_clarity, score_examples, score_total)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (username, snippet_id, documentation,
         result["completeness"], result["accuracy"],
         result["clarity"], result["examples"], result["total"]),
    )
    db.commit()

    return jsonify({
        "id": cursor.lastrowid,
        "snippet_id": snippet_id,
        "username": username,
        "scores": result,
    }), 201


@app.route("/api/leaderboard")
def api_leaderboard():
    db = get_db()
    rows = db.execute(
        "SELECT * FROM submissions ORDER BY score_total DESC, created_at ASC LIMIT 50"
    ).fetchall()
    return jsonify([dict(r) for r in rows])


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)
