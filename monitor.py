import urllib.request
import urllib.error
import time
from datetime import datetime

# --- CONFIGURATION ---
CONFIG_FILE = "urls.txt"
MAIN_LOG = "uptime.log"
DOWNTIME_LOG = "downtime.log"
CHECK_INTERVAL_SECONDS = 10  # How often to loop


def load_targets():
    """Reads the URLs from urls.txt, stripping out any blank lines."""
    with open(CONFIG_FILE, "r") as file:
        return [line.strip() for line in file if line.strip()]


def write_to_log(filename, message):
    """Safely appends a timestamped log message to a file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, "a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] {message}\n")


def ping(url):
    """
    Attempts to fetch a URL. 
    Calculates latency if successful; catches the exact HTTP/Network error if it goes down.
    """
    # Force 'https://' if the user was lazy in the config file
    if not url.startswith("http"):
        url = "https://" + url

    start_time = time.time()

    try:
        # We pass a custom User-Agent so security firewalls don't mistake us for a spam bot
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Python Lightweight Uptime Monitor/1.0)'}
        )
        
        # Open the URL with a strict 5-second timeout
        response = urllib.request.urlopen(req, timeout=5)
        
        latency_ms = int((time.time() - start_time) * 1000)
        status_code = response.getcode()

        msg = f"STATUS: {status_code} | LATENCY: {latency_ms}ms | TARGET: {url}"
        print(f"  🟢 OK   -> {msg}")
        write_to_log(MAIN_LOG, f"SUCCESS - {msg}")

    except urllib.error.HTTPError as e:
        # The server answered, but with a crash code (e.g., 404 Not Found, 500 Internal Error)
        msg = f"HTTP ERROR {e.code} ({e.reason}) | TARGET: {url}"
        trigger_down_alert(url, msg)

    except urllib.error.URLError as e:
        # The server didn't even answer (Domain dead, DNS failed, or server unplugged)
        msg = f"NETWORK UNREACHABLE ({e.reason}) | TARGET: {url}"
        trigger_down_alert(url, msg)

    except Exception as e:
        msg = f"SYSTEM CRASH ({str(e)}) | TARGET: {url}"
        trigger_down_alert(url, msg)


def trigger_down_alert(url, error_message):
    """Handles the fail-state: prints red to console, logs to downtime.log."""
    print(f"  🔴 DOWN -> {error_message}")
    write_to_log(MAIN_LOG, f"FAILED  - {error_message}")
    write_to_log(DOWNTIME_LOG, f"🚨 DOWNTIME DETECTED: {error_message}")


# --- THE MAIN DAEMON LOOP ---
if __name__ == "__main__":
    urls = load_targets()
    print(f"\n📡 [UPTIME MONITOR v1.0] Booting up... Loaded {len(urls)} targets.")
    print(f"Logging standard pings to '{MAIN_LOG}' and outages to '{DOWNTIME_LOG}'.")
    print("Press [Ctrl + C] in this window anytime to shut the daemon down.\n" + "="*70)

    try:
        while True:
            for website in urls:
                ping(website)
            
            print(f"\n💤 Next sweep in {CHECK_INTERVAL_SECONDS} seconds...\n" + "-"*70)
            time.sleep(CHECK_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\n🛑 Monitor safely shut down by user.")