# BetMines Pro - Deployment Guide

This guide covers deploying the app locally as a 24/7 background service, or deploying to the cloud (Render, Railway, Docker/VPS) with a public HTTPS URL.

---

## ⚽ App Icon
The app now uses a custom football (soccer ball) SVG icon across:
* **Browser Tab Favicon** (`static/ball.svg`)
* **Header Branding Logo**
* **Mobile / PWA Touch Icon**

---

## 1. Local Production Deployment (Run 24/7 on your PC)

To run the app continuously in the background on your machine:

1. Double-click **`start.bat`** (or execute `python start_app.py`).
2. The server binds to `http://127.0.0.1:8000` (or `http://0.0.0.0:8000` to access from your phone on local Wi-Fi).
3. SQLite database (`data/betmines.db`) will continuously persist your sync history.

---

## 2. Free Cloud Deployment on Render (Recommended)

[Render](https://render.com) offers a free cloud tier that can host Docker apps:

1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Deploy BetMines Pro"
   git remote add origin https://github.com/YOUR_USERNAME/betmines-pro.git
   git push -u origin main
   ```
2. **Create New Web Service on Render**:
   - Go to [dashboard.render.com](https://dashboard.render.com) and click **New + > Web Service**.
   - Connect your GitHub repository.
   - Render will detect the `Dockerfile` automatically (or select **Docker** as environment).
3. **Deploy**:
   - Click **Deploy Web Service**.
   - Render installs Playwright Chromium and launches `uvicorn server:app`.
   - You get a free public URL: `https://betmines-pro.onrender.com`.

---

## 3. Cloud Deployment on Railway

1. Install Railway CLI or go to [railway.app](https://railway.app).
2. Connect your GitHub repository.
3. Railway automatically detects `Dockerfile` and builds the Playwright environment.
4. Add a public domain under **Settings > Generate Domain**.

---

## 4. Docker / VPS Deployment

To run with Docker on any VPS (Ubuntu, Debian, AWS, DigitalOcean):

```bash
# Build the Docker image
docker build -t betmines-pro .

# Run the container
docker run -d -p 8000:8000 --name betmines_app --restart unless-stopped betmines-pro
```

Access at `http://YOUR_SERVER_IP:8000`.
