#!/usr/bin/env python3
"""Start the FastAPI backend and the Streamlit frontend together with one command.

    python run.py

Press Ctrl+C once to stop both. Use `python run.py --help` for options.
"""

import argparse
import os
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def backend_is_healthy(base_url: str) -> bool:
    try:
        with urllib.request.urlopen(f"{base_url}/health", timeout=2) as response:
            return response.status == 200
    except OSError:
        return False


def raise_interrupt(*_args: object) -> None:
    raise KeyboardInterrupt


def stop(process: subprocess.Popen) -> None:
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Users & Notes backend and frontend together.")
    parser.add_argument("--backend-port", type=int, default=8000)
    parser.add_argument("--frontend-port", type=int, default=8501)
    parser.add_argument("--reload", action="store_true", help="auto-restart the backend when its code changes")
    parser.add_argument("--no-browser", action="store_true", help="do not open the browser automatically")
    args = parser.parse_args()

    # Treat "terminate" (closing the terminal, docker stop) like Ctrl+C so both servers are stopped.
    signal.signal(signal.SIGTERM, raise_interrupt)

    backend_url = f"http://127.0.0.1:{args.backend_port}"
    backend_cmd = [
        sys.executable, "-m", "uvicorn", "app.main:app",
        "--app-dir", "backend", "--host", "127.0.0.1", "--port", str(args.backend_port),
    ]
    if args.reload:
        backend_cmd += ["--reload", "--reload-dir", "backend"]
    frontend_cmd = [
        sys.executable, "-m", "streamlit", "run", "frontend/app.py",
        "--server.port", str(args.frontend_port),
    ]
    if args.no_browser:
        frontend_cmd += ["--server.headless", "true"]

    print(f"Starting backend on {backend_url} ...")
    backend = subprocess.Popen(backend_cmd, cwd=ROOT)
    frontend: subprocess.Popen | None = None
    try:
        deadline = time.time() + 30
        while not backend_is_healthy(backend_url):
            if backend.poll() is not None:
                print("The backend stopped during startup (is the port already in use?).")
                return 1
            if time.time() > deadline:
                print("The backend did not become healthy within 30 seconds.")
                return 1
            time.sleep(0.5)

        print(f"Backend is ready. API docs: {backend_url}/docs")
        print(f"Starting frontend on http://localhost:{args.frontend_port} ... (Ctrl+C stops both)")
        frontend = subprocess.Popen(frontend_cmd, cwd=ROOT, env={**os.environ, "API_BASE_URL": backend_url})
        while backend.poll() is None and frontend.poll() is None:
            time.sleep(1)
        print("One of the servers stopped, shutting down the other.")
        return 1
    except KeyboardInterrupt:
        print("\nStopping ...")
        return 0
    finally:
        for process in (frontend, backend):
            if process is not None:
                stop(process)


if __name__ == "__main__":
    sys.exit(main())
