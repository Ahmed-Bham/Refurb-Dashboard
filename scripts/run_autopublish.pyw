r"""
run_autopublish.pyw

Runs publish_dashboard_data.py every few minutes, silently in the background
(.pyw files run with pythonw.exe, so there is no console window).
Put a shortcut to this file in your Startup folder so it starts at log-in.
Output goes to autopublish.log in the repo folder.
"""

import datetime
import os
import subprocess
import sys
import time

MINUTES_BETWEEN_RUNS = 3

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(REPO_ROOT, "autopublish.log")
PUBLISH = os.path.join(REPO_ROOT, "scripts", "publish_dashboard_data.py")
NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
# Use python.exe (not pythonw.exe) for the child so its output can be logged
PYTHON = sys.executable.replace("pythonw.exe", "python.exe")


def log(text):
    # Keep the log small: start a fresh one when it passes ~1 MB
    if os.path.exists(LOG) and os.path.getsize(LOG) > 1_000_000:
        os.replace(LOG, LOG + ".old")
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(text)


while True:
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        result = subprocess.run([PYTHON, PUBLISH], cwd=REPO_ROOT, capture_output=True, text=True,
                                creationflags=NO_WINDOW, timeout=300)
        log(f"\n=== {stamp} (exit {result.returncode}) ===\n{result.stdout}{result.stderr}")
    except Exception as error:
        log(f"\n=== {stamp} ERROR ===\n{error}\n")
    time.sleep(MINUTES_BETWEEN_RUNS * 60)
