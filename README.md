# Refurbishment progress dashboard

A public web page showing progress on the Cape Town 92 Marine refurbishment
tracker. Your laptop reads the tracker Excel file from OneDrive every few
minutes and pushes the numbers to GitHub; the page checks for new numbers
every 60 seconds. Nobody needs to log in to view it.

**What's in this folder**

| File | What it does |
|---|---|
| `index.html` | The dashboard page |
| `dashboard_data.json` | The numbers the page shows (rebuilt automatically) |
| `scripts/refresh_dashboard_data.py` | Reads the tracker and writes `dashboard_data.json` |
| `scripts/publish_dashboard_data.py` | Runs the refresh, then pushes any change to GitHub |
| `scripts/run_autopublish.pyw` | Runs the publish script every 3 minutes in the background |

> **Before you start:** a GitHub Pages link is public. Anyone who has the link
> can see unit details, team names and rand stock values. To leave the rand
> values out, set `INCLUDE_VALUES = False` in `scripts/refresh_dashboard_data.py`.

---

## One-time setup (about 20 minutes)

### 1. Create the GitHub repository

1. Sign up or sign in at <https://github.com>.
2. Click **+** (top right) → **New repository**.
3. Name it `refurb-dashboard`, choose **Public**, and tick **Add a README file**.
4. Click **Create repository**.

### 2. Install Git and Python on your laptop

1. Install **Git for Windows** from <https://git-scm.com/download/win> (the default options are fine).
2. Install **Python 3** from <https://www.python.org/downloads/>. On the first
   installer screen, tick **Add python.exe to PATH**.
3. Open **Command Prompt** and run these, using your own name and the email on your GitHub account:

   ```
   pip install openpyxl
   git config --global user.name "Your Name"
   git config --global user.email "you@example.com"
   ```

### 3. Copy the repository to your laptop and add these files

1. In Command Prompt (replace `YOUR-GITHUB-NAME`):

   ```
   cd %USERPROFILE%\Documents
   git clone https://github.com/YOUR-GITHUB-NAME/refurb-dashboard.git
   ```

   This makes the folder `Documents\refurb-dashboard`.
   Keep this folder **outside** OneDrive, so OneDrive and Git don't fight over it.
2. Copy everything from this download into that folder (`index.html`,
   `dashboard_data.json`, `.gitignore`, `README.md` and the `scripts` folder).
   Replace the README that GitHub created.

### 4. Point the script at the tracker

1. In File Explorer, go to the tracker in your OneDrive folder
   (`002.Operations\Refurbishment_Tracker (2).xlsx`).
2. Right-click it → **Always keep on this device**, so the real file is on the laptop.
3. Hold **Shift**, right-click the file → **Copy as path**.
4. Open `scripts\refresh_dashboard_data.py` in Notepad. Find the line starting
   `TRACKER_PATH = r"` and paste the path between the quotes (delete the extra
   quote marks the copy adds). It should look like:

   ```
   TRACKER_PATH = r"C:\Users\Ahmed\OneDrive\002.Operations\Refurbishment_Tracker (2).xlsx"
   ```
5. Save the file.

### 5. Test it and publish for the first time

In Command Prompt:

```
cd %USERPROFILE%\Documents\refurb-dashboard
python scripts\refresh_dashboard_data.py
git add .
git commit -m "Add dashboard"
git push origin main
```

The first `refresh` line should say how many units it wrote (75).
The first `push` opens a browser window asking you to sign in to GitHub. Sign
in and approve it; Windows remembers it from then on.

### 6. Switch on GitHub Pages

1. On GitHub, open the repository → **Settings** → **Pages** (left menu).
2. Under **Build and deployment**, set **Source** to **Deploy from a branch**,
   branch **main**, folder **/ (root)**, then **Save**.
3. After a minute or two the page shows your link:
   `https://YOUR-GITHUB-NAME.github.io/refurb-dashboard/`

Open it. You should see the dashboard with the tracker's current numbers.

### 7. Make it update automatically

1. Find where Python is: in Command Prompt run `where pythonw`. Copy the first
   line, e.g. `C:\Users\Ahmed\AppData\Local\Programs\Python\Python312\pythonw.exe`.
2. Press **Windows + R**, type `shell:startup` and press Enter. A folder opens.
3. Right-click inside it → **New** → **Shortcut**. For the location, enter the
   pythonw path, a space, and the runner's path in quotes, e.g.:

   ```
   C:\Users\Ahmed\AppData\Local\Programs\Python\Python312\pythonw.exe "C:\Users\Ahmed\Documents\refurb-dashboard\scripts\run_autopublish.pyw"
   ```
4. Name it `Refurb dashboard autopublish` and click **Finish**.
5. Double-click the new shortcut to start it now. Nothing appears on screen;
   that's expected. From now on it starts whenever you log in.

**Test it:** change a status in the tracker and save. Within about 5 minutes
(3 for the laptop to notice, 1–2 for GitHub to publish, then the page's next
60-second check) the dashboard shows the change.

---

## Day to day

- The dashboard only updates while your laptop is **on, awake, logged in and online**.
  If it sleeps, set **Settings → System → Power → Screen and sleep** so it
  doesn't sleep while plugged in.
- Edits made by others (in Excel online or on their computers) reach the
  dashboard once OneDrive has synced them to your laptop.
- The header shows when the data last changed. The dot turns amber if nothing
  has changed for over 24 hours, red if the page can't load the data.
- If the tracker is renamed, moved, or replaced by a new copy (e.g.
  `Refurbishment_Tracker (3).xlsx`), update `TRACKER_PATH` (step 4).
- Keep the tracker's layout: a **Tracker** sheet with the `Job ID` header row,
  and team names on the **Lists** sheet under **Teams**.

## If it stops updating

Open `autopublish.log` in the `refurb-dashboard` folder. The newest entry is at
the bottom.

| What the log says | What to do |
|---|---|
| `tracker not found` | Fix `TRACKER_PATH` (step 4) and check the file is set to "Always keep on this device". |
| `other files ... have unsaved git changes` | You edited a file in the folder. Either undo the change, or commit it: `git add .` then `git commit -m "Update"` then `git push origin main`. |
| `could not pull` / `push ... failed` | Usually no internet. It retries every 3 minutes. If it persists, run `git push origin main` yourself to see the error. |
| No new entries at all | The background runner isn't running. Double-click the startup shortcut (step 7). |
| `Nothing new to publish` | All fine. The tracker simply hasn't changed. |

To stop it: open Task Manager, end the **pythonw.exe** process, and delete the
shortcut from the startup folder.
