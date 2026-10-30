"""
start_app.py
Entry point to launch BetMines Pro Prediction & Sync Engine.
Binds to 0.0.0.0 so you can access and install it on your Android phone,
tablets, and other devices connected to your Wi-Fi network.
"""

import socket
import webbrowser
import threading
import time
import uvicorn

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def open_browser():
    time.sleep(1.5)
    print("\n[+] Opening BetMines Pro Dashboard in your browser: http://127.0.0.1:8000 ...")
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    ip = get_local_ip()
    print("=" * 70)
    print("  ⚽ BETMINES PRO - 100% SYNC & BEST PREDICTION APP")
    print("=" * 70)
    print("  🖥️  LOCAL PC ACCESS:     http://127.0.0.1:8000")
    print(f"  📱  ANDROID & DEVICES:   http://{ip}:8000")
    print("=" * 70)
    print("  [!] On your Android phone, open the URL above in Chrome")
    print("      and tap 'Install App' or 'Add to Home screen' to install!")
    print("=" * 70)
    print("[*] Press Ctrl+C in terminal to stop server.\n")

    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
