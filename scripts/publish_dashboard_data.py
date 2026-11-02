r"""
publish_dashboard_data.py

1. Pulls the latest from GitHub
2. Rebuilds dashboard_data.json from the tracker (refresh_dashboard_data.py)
3. If it changed, commits and pushes it to GitHub

Run it directly to test:  python scripts\publish_dashboard_data.py
run_autopublish.pyw calls it every few minutes.
"""

import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = "dashboard_data.json"
# Stop a console window flashing up each time when run in the background
NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0


def run(cmd):
    print(f"[publish] $ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, creationflags=NO_WINDOW)
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    return result


def changed_files():
    out = run(["git", "status", "--porcelain"]).stdout
    return [line[3:].strip().strip('"') for line in out.splitlines() if line.strip()]


def main():
    others = [f for f in changed_files() if f != DATA_FILE]
    if others:
        print(f"[publish] ERROR: other files in the repo folder have unsaved git changes: {others}\n"
              "Commit or undo them (e.g. in GitHub Desktop) - auto-publish only handles the data file.")
        sys.exit(1)

    if run(["git", "pull", "--rebase", "--autostash", "origin", "main"]).returncode != 0:
        print("[publish] ERROR: could not pull from GitHub (no internet, or a conflict).")
        sys.exit(1)

    refresh = subprocess.run([sys.executable, os.path.join(REPO_ROOT, "scripts", "refresh_dashboard_data.py")],
                             cwd=REPO_ROOT, creationflags=NO_WINDOW)
    if refresh.returncode != 0:
        print("[publish] ERROR: refresh_dashboard_data.py failed.")
        sys.exit(1)

    if DATA_FILE not in changed_files():
        print("[publish] Nothing new to publish.")
        return

    run(["git", "add", DATA_FILE])
    run(["git", "commit", "-m", "Update dashboard data"])
    if run(["git", "push", "origin", "main"]).returncode != 0:
        print("[publish] ERROR: push to GitHub failed.")
        sys.exit(1)
    print("[publish] Published.")


if __name__ == "__main__":
    main()
