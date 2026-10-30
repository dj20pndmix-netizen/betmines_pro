"""
run_phone_app.py
Starts the BetMines Pro engine with a dedicated, secure HTTPS Cloudflare tunnel
so you can install it onto your Android phone (or any device) with 1 tap.
"""

import subprocess
import time
import re
import sys
import os

def run():
    print("=" * 70)
    print("  ⚽ BETMINES PRO - ANDROID & MULTI-DEVICE LAUNCHER")
    print("=" * 70)
    print("[*] Starting backend engine on port 8000...")
    
    # Start uvicorn server in background
    server_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    time.sleep(2)
    print("[*] Starting secure HTTPS tunnel for Android PWA installation...")

    cloudflared_path = os.path.join(os.path.dirname(__file__), "cloudflared.exe")
    if not os.path.exists(cloudflared_path):
        print("[-] cloudflared.exe not found.")
        return

    tunnel_proc = subprocess.Popen(
        [cloudflared_path, "tunnel", "--url", "http://127.0.0.1:8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )

    https_url = None
    start_time = time.time()
    while time.time() - start_time < 30:
        line = tunnel_proc.stdout.readline()
        if not line:
            continue
        match = re.search(r'https://[a-zA-Z0-9_\-]+\.trycloudflare\.com', line)
        if match:
            https_url = match.group(0)
            break

    if https_url:
        print("\n" + "=" * 70)
        print("  🎉 SECURE HTTPS INSTALL LINK FOR YOUR ANDROID PHONE:")
        print(f"  👉  {https_url}")
        print("=" * 70)
        print("  HOW TO INSTALL ON ANDROID:")
        print("  1. Open Chrome on your phone and go to the link above.")
        print("  2. Tap 'Install App' banner (or tap 3 dots ⋮ -> 'Install app').")
        print("  3. The app installs with the ⚽ Football Icon on your home screen!")
        print("=" * 70 + "\n")
    else:
        print("[-] Could not retrieve tunnel URL. Check internet connection.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Stopping server and tunnel...")
        server_proc.terminate()
        tunnel_proc.terminate()

if __name__ == "__main__":
    run()
