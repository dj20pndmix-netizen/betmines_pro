# Deployment & Release Engineering Manual
**Project:** BetMines Pro Prediction & Synchronization Engine  
**Standard:** Master Professional App Development Standard (MPADS v1.0)  
**Revision:** 1.0.0

---

## 1. Supported Deployment Targets

### Target 1: 24/7 Cloud Platform (Render / Railway / Fly.io)
- **Container**: `Dockerfile` based on `python:3.11-slim`.
- **System Dependencies**: Includes Playwright-managed Chromium and required Linux graphics libraries.
- **Configuration**: Declarative `render.yaml` provisions web services on `0.0.0.0:$PORT`.
- **SSL / HTTPS**: Automatic Let's Encrypt certificates enabling instantaneous Android PWA installation.

### Target 2: Local & LAN Multi-Device Deployment
- **Script**: `start_phone.bat` or `python run_phone_app.py`.
- **Tunneling**: Bundles Cloudflare Tunnel (`cloudflared`) to generate a secure HTTPS gateway (`*.trycloudflare.com`) for direct Android mobile installation over local network boundaries.

---

## 2. Release Acceptance Checklist

- [x] Functional requirements verified against live BetMines feeds.
- [x] Automated test suite passing with zero failures.
- [x] SQLite schema verified with proper indexing.
- [x] PWA manifest and service worker compliant with Android Chrome install specifications.
- [x] Rollback plan documented.
