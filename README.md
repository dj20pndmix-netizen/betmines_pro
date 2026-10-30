# TikTok Auto-Like & Auto-Follow Bot

An automated assistant that browses TikTok videos, watches them for randomized human-like durations, and automatically likes videos and follows creators while adhering to safe rate limits.

---

## 🚀 Features

- **Persistent Session Storage:** Log in once using your normal browser window (supports 2FA, QR code, Google/Apple sign-in). Your session cookies remain saved locally in `tiktok_profile/`.
- **Feed Modes:**
  - **For You Feed (`foryou`):** Likes and follows directly from your personalized feed.
  - **Hashtag Feed (`hashtag`):** Targets videos under specific hashtags (e.g., `#gaming`, `#fitness`, `#tech`).
- **Human Behavior Emulation:**
  - Randomized watch time per video (e.g., 6–15 seconds) before taking action.
  - Configurable like & follow probability (e.g., likes ~75% of videos, follows ~30% of creators) so activity does not appear synthetic.
  - Subtle mouse movement simulation and human-like delays.
- **Safety Caps & Limits:** Auto-stops once maximum like and follow goals are reached.
- **Graceful Controls:** Stop anytime with `Ctrl + C` and receive a full session summary.

---

## 📁 Project Structure

```text
tiktok/
├── run.py              # Interactive console launcher menu
├── login_helper.py     # Secure manual login tool to save your session
├── tiktok_bot.py       # Core automation engine
├── config.json         # Configuration parameters and limits
└── tiktok_profile/     # (Created after login) Local Chromium profile & cookies
```

---

## 🛠️ How to Use

### Step 1: Open Terminal in this folder
```bash
cd C:\Users\user\Downloads\tiktok
```

### Step 2: Launch the Console
```bash
python run.py
```

### Step 3: First-Time Login (Option 1)
1. Select **Option 1** (`Login / Manage TikTok Account`).
2. A Chromium window will open to `tiktok.com/login`.
3. Sign in to your TikTok account as you normally would (scan QR code, password, 2FA, or Google login).
4. Once you are logged in and see your feed, go back to the terminal and press **Enter**.
5. Your login session will be saved in `tiktok_profile/`. You won't have to log in again!

### Step 4: Run the Bot (Option 2 or 3)
- Choose **Option 2** to automate on your **For You** page.
- Choose **Option 3** to automate on a **Hashtag** (e.g. `tech`, `cooking`, `fyp`).

---

## ⚙️ Configuration (`config.json`)

You can edit settings directly via **Option 4** in `python run.py` or by opening `config.json`:

```json
{
  "mode": "foryou",
  "target_hashtag": "fyp",
  "max_likes": 25,
  "max_follows": 10,
  "like_probability": 0.75,
  "follow_probability": 0.30,
  "min_watch_seconds": 6,
  "max_watch_seconds": 15,
  "min_delay_between_actions": 3,
  "max_delay_between_actions": 7,
  "headless": false
}
```

---

## 🛡️ Best Practices & Safety Tips

1. **Keep Limits Conservative:** 
   - Recommended maximum: **20–30 likes** and **10–15 follows** per session.
   - Run 1–2 sessions per day with several hours in between to avoid TikTok shadowbans or temporary action blocks.
2. **Watch Time:** 
   - Never set watch time to 0. Real users watch at least 5–15 seconds of a clip.
3. **Probabilities:** 
   - Keeping `like_probability` around 60–80% and `follow_probability` around 20–35% prevents the algorithm from detecting robotic 1:1 patterns.
