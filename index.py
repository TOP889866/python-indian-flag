from flask import Flask, request, send_file, render_template_string, jsonify
from collections import defaultdict, deque
from typing import Dict
import tempfile
import os
import time
import html
import hashlib
from flag import create_flag_with_footer, validate_name

app = Flask(__name__)

# === Rate Limiting ===
_ip_hits: Dict[str, deque] = defaultdict(deque)
RATE_LIMIT = 5
TIME_WINDOW = 10

# === In-memory cache for images ===
cache_dir = os.path.join(tempfile.gettempdir(), "flag_cache")
os.makedirs(cache_dir, exist_ok=True)
image_cache: Dict[str, str] = {}  # hash -> file path
CACHE_TTL = 60 * 60 * 24  # 1 day

def is_rate_limited(ip: str) -> bool:
    now = time.time()
    hits = _ip_hits[ip]
    while hits and now - hits[0] > TIME_WINDOW:
        hits.popleft()
    if len(hits) >= RATE_LIMIT:
        return True
    hits.append(now)
    return False

def get_cache_key(name: str) -> str:
    """Create a hash key for caching"""
    return hashlib.sha256(name.encode("utf-8")).hexdigest()

def clean_cache():
    """Remove old cache files to save memory/disk"""
    now = time.time()
    for key, path in list(image_cache.items()):
        if not os.path.exists(path):
            image_cache.pop(key, None)
        elif now - os.path.getmtime(path) > CACHE_TTL:
            os.remove(path)
            image_cache.pop(key, None)

@app.after_request
def set_security_headers(response):
    response.headers.update({
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Cache-Control": "public, max-age=86400"
    })
    return response

HTML_FORM = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, shrink-to-fit=no">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>Indian Flag Generator</title>
    <meta name="description" content="A special 🇮🇳 Happy Independence Day greeting for your friends and Family Members.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Hind+Madurai:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            background: #121212;
            color: #E0E0E0;
            font-family: "Hind Madurai", sans-serif;
            margin: 0;
            padding: 10px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        h1 {
            color: #FFB300;
            margin: 15px 0;
            font-family: "Hind Madurai", sans-serif;
            text-align: center;
        }
        .container {
            max-width: 500px;
            width: 100%;
            background: #1E1E1E;
            padding: 20px;
            border-radius: 8px;
            box-sizing: border-box;
            box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        }
        input {
            width: 100%;
            font-family: "Hind Madurai", sans-serif;
            padding: 12px;
            font-size: 16px;
            border: none;
            border-radius: 6px;
            margin-bottom: 15px;
            outline: none;
            background: #2C2C2C;
            color: #E0E0E0;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            padding: 12px;
            font-family: "Hind Madurai", sans-serif;
            font-size: 16px;
            background: #FF5722;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            transition: background 0.3s;
        }
        button:hover {
            background: #E64A19;
        }
        .terminal {
            background: #000;
            color: #00FF41;
            font-family: monospace;
            padding: 10px;
            height: 200px;
            overflow-y: auto;
            margin-top: 15px;
            border-radius: 6px;
            font-size: 14px;
        }
        img {
            margin-top: 15px;
            max-width: 100%;
            border-radius: 8px;
        }
        #downloadBtn {
           font-family: "Hind Madurai", sans-serif;
            margin-top: 10px;
            display: none;
            background: #4CAF50;
        }
        #downloadBtn:hover {
            background: #43A047;
        }
        @media (max-width: 480px) {
            .container {
                padding: 15px;
            }
            input, button {
                font-size: 14px;
                padding: 10px;
            }
            .terminal {
                font-size: 12px;
                height: 150px;
            }
        }
    </style>
</head>
<body>
    <h1>🇮🇳 Indian Flag Generator</h1>
    <div class="container">
        <input type="text" id="name" placeholder="Enter Your Name" maxlength="30" required aria-label="Your Name">
        <button onclick="generateFlag()">Generate Flag</button>
        <button id="downloadBtn">Download Flag</button>
        <div class="terminal" id="terminal"></div>
        <img id="flagImage" style="display:none;" alt="Generated Flag">
    </div>

    <script>
        function logToTerminal(message) {
            const terminal = document.getElementById("terminal");
            terminal.innerHTML += message + "<br>";
            terminal.scrollTop = terminal.scrollHeight;
        }

        function generateFlag() {
            document.getElementById("flagImage").style.display = "none";
            document.getElementById("downloadBtn").style.display = "none";
            document.getElementById("terminal").innerHTML = "";

            const name = document.getElementById("name").value.trim();
            if (!name) {
                logToTerminal("❌ Please enter a name.");
                return;
            }

            logToTerminal("> Starting flag generation...");
            setTimeout(() => logToTerminal("> Validating name..."), 500);
            setTimeout(() => {
                fetch(`/generate?name=${encodeURIComponent(name)}`)
                    .then(response => {
                        if (!response.ok) throw new Error("Server error");
                        return response.blob();
                    })
                    .then(blob => {
                        logToTerminal("> Drawing Indian flag...");
                        setTimeout(() => {
                            logToTerminal("> Adding footer text...");
                            const url = URL.createObjectURL(blob);
                            const img = document.getElementById("flagImage");
                            img.src = url;
                            img.style.display = "block";

                            const downloadBtn = document.getElementById("downloadBtn");
                            downloadBtn.href = url;
                            downloadBtn.download = "indian_flag.png";
                            downloadBtn.style.display = "block";

                            logToTerminal("> ✅ Flag generated successfully!");
                        }, 800);
                    })
                    .catch(err => {
                        logToTerminal("❌ " + err.message);
                    });
            }, 1000);
        }

        document.getElementById("downloadBtn").addEventListener("click", function() {
            const link = document.createElement('a');
            link.href = document.getElementById("flagImage").src;
            link.download = "indian_flag.png";
            link.click();
        });
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_FORM)

@app.route("/generate")
def generate_flag():
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if is_rate_limited(client_ip):
        return jsonify({"error": "Too many requests. Please wait."}), 429

    raw_name = request.args.get("name", "").strip()
    safe_name = html.escape(raw_name)
    if not safe_name:
        return jsonify({"error": "Invalid name"}), 400

    try:
        name = validate_name(safe_name)

        # === Check cache ===
        clean_cache()
        cache_key = get_cache_key(name)
        if cache_key in image_cache and os.path.exists(image_cache[cache_key]):
            return send_file(image_cache[cache_key], mimetype="image/png")

        # === Generate and store in cache ===
        image_path = os.path.join(cache_dir, f"{cache_key}.png")
        create_flag_with_footer(name, image_path)
        image_cache[cache_key] = image_path

        return send_file(image_path, mimetype="image/png")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()
