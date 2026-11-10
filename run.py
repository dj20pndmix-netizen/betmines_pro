"""
run.py
Convenience entry point for BetMines Pro.
Directs directly to start_app.py to launch the local BetMines Pro prediction dashboard.
"""

import sys
import os

if __name__ == "__main__":
    import start_app
    # Execute start_app main routine
    ip = start_app.get_local_ip()
    print("=" * 70)
    print("  ⚽ BETMINES PRO - 100% SYNC & BEST PREDICTION APP")
    print("=" * 70)
    print("  🖥️  LOCAL PC ACCESS:     http://127.0.0.1:8000")
    print(f"  📱  ANDROID & DEVICES:   http://{ip}:8000")
    print("=" * 70)
    print("  [!] Opening dashboard in browser: http://127.0.0.1:8000")
    print("[*] Press Ctrl+C in terminal to stop server.\n")

    import threading
    import uvicorn

    threading.Thread(target=start_app.open_browser, daemon=True).start()
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
