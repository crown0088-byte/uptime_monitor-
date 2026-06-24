# 📡 Core System Uptime Monitor & Operations Deck

An automated, zero-dependency network health probe and live operations dashboard built in Python. 

---

## 🌍 Global Scope & Purpose

In an enterprise environment, infrastructure must be monitored 24/7/365. The global scope of this service is to act as an un-siloed **Watchdog**. Instead of a human manually testing whether a website is functioning, this system operates autonomously in the background to answer two critical operational questions:

1. **Live State:** Are our core web services currently responding to public traffic?
2. **Forensics:** When an outage occurs, at what exact timestamp did it fail, and was it a Layer 3 (DNS Resolver) or Layer 7 (HTTP Server) network failure?

---

## 🏗️ Technology Stack

* **Python 3 (`urllib`):** The network probing engine. Intentionally uses the native Python Standard Library to eliminate third-party dependency bloat. Constructs raw HTTP requests, enforces strict 5-second socket timeouts, and injects custom `User-Agent` headers to prevent CDN bot-mitigation firewalls (Cloudflare/Akamai) from rejecting the pings.
* **Flask:** A lightweight Python micro-framework used strictly as a decoupled, read-only presentation layer to serve the HTML interface.
* **Flat-File Streams (`.log`):** Operates as a stateless database. `uptime.log` holds continuous latency receipts; `downtime.log` acts as an isolated, permanent incident ledger for system crashes.
* **HTML5 / CSS3:** Natively written into the dashboard script; rendered in dark-mode to reduce eye strain in Network Operations Center (NOC) environments.
* **DOM Meta-Refresh:** A client-side HTML directive that instructs the web browser to automatically re-fetch the dashboard payload every 5 seconds, creating a pseudo-live data stream without the heavy server overhead of WebSockets.

---

## 📂 Project Structure
uptime_monitor-/
│
├── monitor.py          # Background daemon (Network Prober)
├── dashboard.py        # Foreground server (Flask UI Viewer)
├── urls.txt            # Target domains to track
├── uptime.log          # Autonomously generated success stream
├── downtime.log        # Autonomously generated incident reports
└── README.md           # Systems architecture documentation


Step-by-Step Local Deployment Guide
Follow these instructions to spin up the monitoring suite inside a local development environment.

Step 1: Clone the Repository
Open your terminal (Git Bash or Command Prompt) and pull the project files to your local machine:

Bash
git clone [https://github.com/crown0088-byte/uptime_monitor-.git](https://github.com/crown0088-byte/uptime_monitor-.git)
cd uptime_monitor-
Step 2: Define Target URLs
Open the urls.txt file in any standard text editor and define the domains you wish to monitor (one URL per line):
[https://www.google.com](https://www.google.com)
[https://www.python.org](https://www.python.org)
[https://this-domain-is-100-percent-dead.com](https://this-domain-is-100-percent-dead.com)
Step 3: Install the UI Server
Install Flask (the single required external package):

Bash
pip install flask
Step 4: Launch the Decoupled Architecture (Dual-Terminal)
Because this system separates the Collector (monitor.py) from the Presenter (dashboard.py), the two scripts run as entirely independent processes. You must open two separate terminal windows inside the project folder.

In Terminal Window A (Start the Collector):

Bash
python monitor.py
(Keep this window open. It will enter an infinite loop, testing the target URLs every 10 seconds).

In Terminal Window B (Start the Presenter):

Bash
python dashboard.py
Step 5: Access the Operations Deck
Open any standard web browser and navigate to the local web server address:

[http://127.0.0.1:5000](http://127.0.0.1:5000)
(The page will autonomously refresh every 5 seconds to display live network speeds and green/red operational statuses).
