## Run Instructions

### First-Time Login

Run the script:

```bash
python meeting.py
```

A Chrome browser window will open.

Complete the login process manually using OTP authentication.

After successful login, close Chrome using:

```bash
taskkill /F /IM chrome.exe /T
```

This closes all Chrome processes while preserving the automation profile and session data.

---

### Subsequent Runs

After the initial OTP verification:

```bash
python meeting.py
```

The browser will open automatically using the saved Chrome profile.

The script will:

1. Reuse the existing authenticated session.
2. Skip OTP verification.
3. Navigate directly to the booking portal.
4. Start the booking process automatically.
5. Search and reserve the configured meeting room.

---

## Important Notes

### Do NOT Close Chrome Normally

Avoid closing Chrome manually using the **X** button.

If Chrome is closed normally, the session may not be saved correctly and the portal can require OTP verification again.

Always terminate Chrome using:

```bash
taskkill /F /IM chrome.exe /T
```

This ensures:

* Session data remains available.
* Login state is preserved.
* Automation continues to work without repeated OTP verification.

---

### Session Persistence

The script uses a dedicated Chrome profile:

```python
profile_path = r"C:\Users\HP\Desktop\MyAutoProfile"
```

All login cookies, session tokens, and browser data are stored in this profile directory.

As long as the session remains valid, the automation can launch Chrome and continue directly to the booking workflow without requiring another OTP login.

---

### Recommended Workflow

#### First Time

```bash
python meeting.py
```

→ Login using OTP

```bash
taskkill /F /IM chrome.exe /T
```

#### Every Future Run

```bash
python meeting.py
```

→ Browser opens automatically

→ Existing login session is reused

→ Booking automation starts automatically
