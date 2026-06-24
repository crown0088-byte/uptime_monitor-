from flask import Flask, render_template_string
import os

app = Flask(__name__)
LOG_FILE = "uptime.log"

# --- THE DARK-MODE HTML UI ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Uptime Monitor Dashboard</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: #0d1117;
            color: #c9d1d9;
            padding: 40px;
            margin: 0;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        h1 {
            color: #f0f6fc;
            border-bottom: 1px solid #21262d;
            padding-bottom: 10px;
        }
        .card {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 20px;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .left-side {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .dot {
            width: 14px;
            height: 14px;
            border-radius: 50%;
            display: inline-block;
        }
        .dot.online {
            background-color: #238636;
            box-shadow: 0 0 8px #238636;
        }
        .dot.offline {
            background-color: #da3633;
            box-shadow: 0 0 8px #da3633;
        }
        .url {
            font-weight: bold;
            font-size: 1.1em;
            color: #f0f6fc;
        }
        .meta {
            font-size: 0.85em;
            color: #8b949e;
            margin-top: 4px;
        }
        .badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: bold;
        }
        .badge.online { background-color: rgba(35, 134, 54, 0.15); color: #2ea043; }
        .badge.offline { background-color: rgba(218, 54, 51, 0.15); color: #f85149; }
    </style>
    <meta http-equiv="refresh" content="5">
</head>
<body>
    <div class="container">
        <h1>📡 Core System Uptime Monitor</h1>
        <p style="color: #8b949e;">Page auto-updates every 5 seconds. Reading live metrics from log files.</p>
        
        {% if not states %}
            <div class="card" style="justify-content: center; color: #8b949e;">
                No logs found yet. Run monitor.py to collect data!
            </div>
        {% endif %}

        {% for url, data in states.items() %}
            <div class="card">
                <div class="left-side">
                    <span class="dot {{ 'online' if data.status == 'ONLINE' else 'offline' }}"></span>
                    <div>
                        <div class="url">{{ url }}</div>
                        <div class="meta">Last checked: {{ data.time }}</div>
                    </div>
                </div>
                <div>
                    {% if data.status == 'ONLINE' %}
                        <span class="badge online">ONLINE ({{ data.latency }})</span>
                    {% else %}
                        <span class="badge offline">OFFLINE</span>
                    {% endif %}
                </div>
            </div>
        {% endfor %}
    </div>
</body>
</html>
"""

def parse_log_file():
    """
    Reads uptime.log and parses out the ABSOLUTE LATEST state 
    for every unique target URL found in the log history.
    """
    if not os.path.exists(LOG_FILE):
        return {}

    latest_states = {}

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # --- PARSING PARALLEL LOG LINES ---
            try:
                # Extract timestamp from bracket: "[2026-06-24 16:04:00] SUCCESS - STATUS..."
                timestamp = line[1:20]
                remainder = line[22:]

                if "SUCCESS" in remainder:
                    # Layout: SUCCESS - STATUS: 200 | LATENCY: 96ms | TARGET: https://url.com
                    parts = remainder.split(" | ")
                    latency = parts[1].split(": ")[1]
                    url = parts[2].split(": ")[1]
                    
                    latest_states[url] = {
                        "status": "ONLINE",
                        "latency": latency,
                        "time": timestamp
                    }
                elif "FAILED" in remainder:
                    # Layout: FAILED  - NETWORK UNREACHABLE... | TARGET: https://url.com
                    parts = remainder.split(" | TARGET: ")
                    url = parts[1]
                    
                    latest_states[url] = {
                        "status": "OFFLINE",
                        "latency": "N/A",
                        "time": timestamp
                    }
            except Exception:
                continue # Skip line if it's malformed

    return latest_states

@app.route("/")
def home():
    current_states = parse_log_file()
    return render_template_string(HTML_TEMPLATE, states=current_states)

if __name__ == "__main__":
    print("🚀 Starting local web server...")
    app.run(debug=True, port=5000)