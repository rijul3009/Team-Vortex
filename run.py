"""
Intelligent Expense & Budget Monitoring System - Python Runner
Launches both Backend API (Port 5000) and Frontend UI (Port 5173),
waits for services to be ready, and automatically opens the dashboard.
"""

import os
import sys
import time
import subprocess
import threading
import webbrowser
import urllib.request
from pathlib import Path

# Unbuffered stdout for instant terminal feedback
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(line_buffering=True)

# Paths
ROOT_DIR = Path(__file__).resolve().parent
SERVER_DIR = ROOT_DIR / "server"
CLIENT_DIR = ROOT_DIR / "client"

# Add standard Node.js directory to PATH if needed on Windows
NODE_PATHS = [r"C:\Program Files\nodejs", r"C:\Program Files (x86)\nodejs"]
for np in NODE_PATHS:
    if os.path.exists(np) and np not in os.environ.get("PATH", ""):
        os.environ["PATH"] = np + os.pathsep + os.environ.get("PATH", "")

NPM_CMD = "npm.cmd" if sys.platform == "win32" else "npm"

def print_banner():
    banner = """
=============================================================================
      INTELLIGENT EXPENSE AND BUDGET MONITORING SYSTEM
=============================================================================
  Frontend URL : http://localhost:5173
  Backend API  : http://localhost:5000
  Health Check : http://localhost:5000/health

  Demo Credentials:
    Email    : demo@financial.com
    Password : Password123!
    (Or click '1-Click Demo Sign In' on the login screen)
=============================================================================
"""
    print(banner)

def stream_logs(process, prefix):
    """Streams output from a subprocess with a color/prefix tag."""
    try:
        for line in iter(process.stdout.readline, ''):
            if line:
                print(f"[{prefix}] {line.strip()}")
    except Exception:
        pass

def wait_for_url(url, timeout=30):
    """Waits until a URL responds with HTTP 200/healthy."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "HealthChecker"})
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status in (200, 304):
                    return True
        except Exception:
            pass
        time.sleep(1)
    return False

def kill_process_tree(proc):
    """Cleanly terminates a process and all its children on Windows/Unix."""
    if proc is None or proc.poll() is not None:
        return
    try:
        if sys.platform == "win32":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            proc.terminate()
            proc.wait(timeout=3)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass

def is_service_online(url):
    """Checks if an HTTP service is already active and responding."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "HealthChecker"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            return resp.status in (200, 304)
    except Exception:
        return False

def main():
    print_banner()

    backend_running = is_service_online("http://localhost:5000/health")
    frontend_running = is_service_online("http://localhost:5173")

    if backend_running and frontend_running:
        print("[+] Both Backend (Port 5000) and Frontend (Port 5173) are ALREADY RUNNING!", flush=True)
        print("[*] Opening http://localhost:5173 in your default browser...", flush=True)
        webbrowser.open("http://localhost:5173")
        print("\n[OK] System is live at http://localhost:5173. You are all set!\n", flush=True)
        return

    backend_proc = None
    frontend_proc = None

    if backend_running:
        print("[+] Backend is already running on port 5000.")
    else:
        print("[*] Starting Backend Server (Express + Prisma SQLite)...")
        backend_proc = subprocess.Popen(
            [NPM_CMD, "run", "dev"],
            cwd=str(SERVER_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        t_backend = threading.Thread(target=stream_logs, args=(backend_proc, "BACKEND"), daemon=True)
        t_backend.start()

    if frontend_running:
        print("[+] Frontend is already running on port 5173.")
    else:
        print("[*] Starting Frontend Server (Vite + React)...")
        frontend_proc = subprocess.Popen(
            [NPM_CMD, "run", "dev"],
            cwd=str(CLIENT_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        t_frontend = threading.Thread(target=stream_logs, args=(frontend_proc, "FRONTEND"), daemon=True)
        t_frontend.start()

    print("[*] Waiting for services to initialize...")
    time.sleep(2)

    # Check health and open browser
    backend_ready = wait_for_url("http://localhost:5000/health", timeout=15)
    if backend_ready:
        print("[+] Backend API is online at http://localhost:5000")
    else:
        print("[!] Backend is starting up...")

    frontend_ready = wait_for_url("http://localhost:5173", timeout=15)
    if frontend_ready:
        print("[+] Frontend is online at http://localhost:5173")
        print("[*] Opening http://localhost:5173 in your default browser...")
        webbrowser.open("http://localhost:5173")
    else:
        print("[!] Frontend may still be starting up, visit http://localhost:5173 once ready.")

    print("\n[OK] Running. Press Ctrl+C at any time to stop.\n")

    try:
        while True:
            if backend_proc and backend_proc.poll() is not None:
                print(f"[!] Backend stopped with code {backend_proc.poll()}")
                break
            if frontend_proc and frontend_proc.poll() is not None:
                print(f"[!] Frontend stopped with code {frontend_proc.poll()}")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Shutting down servers gracefully...")
    finally:
        kill_process_tree(backend_proc)
        kill_process_tree(frontend_proc)
        print("[+] Servers stopped successfully.")

if __name__ == "__main__":
    main()
