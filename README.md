# 🤖 Peoplefirst Meeting Room Booking Automation

> **Auto-books Meeting Room No 02 — Building 30/E Wing/SF — 20:00 to 22:00**
> Powered by Python + Selenium | Execution Time: ~6–9 seconds

---

## 📋 Table of Contents

- [What This Does](#what-this-does)
- [Requirements](#requirements)
- [Installation](#installation)
- [First-Time Setup (OTP Login)](#first-time-setup-otp-login)
- [Running the Script](#running-the-script)
- [Expected Output](#expected-output)
- [How It Works](#how-it-works)
- [Troubleshooting](#troubleshooting)
- [Important Rules](#important-rules)

---

## 🎯 What This Does

This script **fully automates** the Peoplefirst CRBS room booking portal in **6–9 seconds**:

| Step | Action |
|------|--------|
| 1 | Opens Chrome with saved login session |
| 2 | Navigates to booking portal |
| 3 | Selects Location → Reliance Corporate Park |
| 4 | Sets Date → 12/6/2026 |
| 5 | Sets Start Time → 20:00 |
| 6 | Sets End Time → 22:00 |
| 7 | Selects Building → Building 30-2F |
| 8 | Selects Wing → E |
| 9 | Clicks Search Available Rooms |
| 10 | Finds and clicks Meeting Room No 02 |
| 11 | Accepts Terms & Conditions |
| 12 | Enters Booking Title → ISOC |
| 13 | Confirms booking |

**Zero manual interaction required after first-time login.**

---

## ⚙️ Requirements

| Requirement | Version / Detail |
|---|---|
| Python | 3.9 or higher |
| selenium | `pip install selenium` |
| Chrome Browser | Any recent version |
| ChromeDriver | Must match your Chrome version |
| OS | Windows 10 / 11 |

### Install Dependencies

```bash
pip install selenium
```

---

## 📁 File Structure

```
Peoplefirst Automation/
│
├── meeting_final.py          ← Main automation script
├── README.md                 ← This file
└── MyAutoProfile/            ← Created automatically on first run
    └── (Chrome session data stored here)
```

> **Profile path used by script:**
> ```
> C:\Users\HP\Desktop\MyAutoProfile
> ```
> This folder stores your login session. **Do not delete it.**

---

## 🔐 First-Time Setup (OTP Login)

You only need to do this **once**.

### Step 1 — Run the script

```bash
python meeting_final.py
```

Chrome will open and navigate to the Peoplefirst portal.

### Step 2 — Login manually

Complete the login using your credentials and OTP verification.

### Step 3 — Close Chrome correctly

**Do NOT click the X button.** Always use this command:

```bash
taskkill /F /IM chrome.exe /T
```

This saves your session correctly so OTP is never asked again.

---

## ▶️ Running the Script

After first-time login, every future run is just:

```bash
python meeting_final.py
```

That's it. The script handles everything automatically.

---

## ✅ Expected Output

```
🚀 Launching Chrome at Max Speed...
⚡ Navigating to booking portal...
    ✅ Portal loaded.
[*] Step: Location → Reliance Corporate Park
    ✅ Location → Reliance Corporate Park selected.
[*] Step: Booking Date → 12/6/2026...
    ✅ Booking Date set.
[*] Step: Start Time → 20:00
    ✅ Start Time → 20:00 selected.
[*] Step: End Time → 22:00
    ✅ End Time → 22:00 selected.
[*] Waiting for Building dropdown AJAX...
[*] Step: Building → Building 30-2F
    ✅ Building → Building 30-2F selected.
[*] Waiting for Wing dropdown AJAX...
[*] Step: Wing → E
    ✅ Wing → E selected.
[*] Clicking 'Search Available Rooms'...
    ✅ Search triggered. Waiting for room cards...
    ✅ Room results loaded.
[*] Scanning for 'Meeting Room No 02'...
    📄 Scanning page 1...
    🎯 'Meeting Room No 02' found on page 1!
[*] Clicking room card (inner element)...
    ✅ Room card clicked.
[*] Waiting for Terms & Conditions modal...
    ✅ T&C modal appeared.
    ✅ Agree button found: 'I Agree'
    ✅ 'I agree' clicked.
[*] Waiting for booking details modal...
    ✅ Booking modal appeared.
[*] Entering Booking Title 'ISOC'...
    ✅ Booking Title set to 'ISOC'.
[*] Clicking 'Confirm Booking'...
    ✅ 'Confirm Booking' clicked.

🏆 BOOM! Booking confirmed!
    Room  : Meeting Room No 02
    Date  : 12-Jun-2026
    Time  : 20:00 – 22:00
    Title : ISOC
```

---

## ⚡ How It Works (Technical Summary)

### Speed Optimizations

This script is built for **maximum speed**:

| Technique | What it does |
|---|---|
| `page_load_strategy = eager` | Doesn't wait for full page load — acts as soon as DOM is ready |
| `--blink-settings=imagesEnabled=false` | Skips all image downloads |
| JS injection | Clicks, inputs, events all done via JavaScript — no browser simulation delay |
| `js_poll()` | Polls DOM every 30–50ms instead of fixed `time.sleep()` waits |
| Combined XPath (`\|`) | Checks all button variants in one WebDriverWait call |
| Total fixed sleep | Only **0.20 seconds** of hardcoded sleep in entire script |

### Angular Component Handling

The portal uses Angular custom elements. The room card is structured as:

```
owl-item (carousel wrapper)
  └─ lib-room-card  ← Angular host (NO click handler)
       └─ div.rmcrd ← ACTUAL clickable element ✅
```

The script finds `div.rmcrd` and dispatches a full mouse event chain (`mouseenter → mouseover → mousedown → mouseup → click`) — exactly like a real user click.

### React Input Handling

Standard `send_keys()` doesn't work on React-controlled inputs. The script uses JavaScript's native `HTMLInputElement` setter to bypass React's synthetic event system.

---

## 🛠️ Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| OTP asked again | Chrome was closed using X button | Run script → login again → `taskkill /F /IM chrome.exe /T` |
| `SessionNotCreatedException` | ChromeDriver version mismatch | Download ChromeDriver matching your Chrome version from [chromedriver.chromium.org](https://chromedriver.chromium.org) |
| Portal loads but hangs | Network slow / portal down | Wait and retry. Script timeouts are set to handle slow AJAX |
| Room not found | Room No 02 not available on that date/time | Manually check portal availability |
| `ModuleNotFoundError: selenium` | Selenium not installed | `pip install selenium` |
| Script runs but no booking | T&C modal button text changed | Check console output for button debug info |

---

## ⚠️ Important Rules

### ✅ Always close Chrome like this:

```bash
taskkill /F /IM chrome.exe /T
```

### ❌ Never close Chrome using the X button

Closing Chrome normally **may corrupt the session** and require OTP login again.

### ✅ Session Persistence

Your login session is stored at:

```
C:\Users\HP\Desktop\MyAutoProfile
```

As long as this folder exists and session is valid, the script runs **without any manual login**.

---

## 📌 Quick Reference

```bash
# Install
pip install selenium

# First time only
python meeting_final.py
# → Login with OTP manually
taskkill /F /IM chrome.exe /T

# Every run after that
python meeting_final.py
```

---

*Automation built for Reliance ISOC — Peoplefirst CRBS Portal*
*Script: meeting_final.py | Profile: MyAutoProfile | Target: Meeting Room No 02*
