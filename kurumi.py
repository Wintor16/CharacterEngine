#!/usr/bin/env python3
"""
Kurumi AI - One-File Launcher
Does everything: setup venv, install deps, start Ollama, pull model, run CLI or Web UI
"""

import os
import sys
import subprocess
import time
import shutil
from pathlib import Path

# ─── CONFIG ───
PROJECT_DIR = Path(__file__).parent.absolute()
VENV_DIR = PROJECT_DIR / "kurumi_venv"
MODEL = "gemma3:4b"
OLLAMA_URL = "http://localhost:11434"
WEB_PORT = 8000
# ──────────────

def run(cmd, check=True, capture=False, bg=False):
    """Run shell command."""
    cwd = str(PROJECT_DIR)
    if bg:
        return subprocess.Popen(cmd, shell=True, cwd=cwd)
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=capture, text=True)
    if check and result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        print(result.stderr)
        sys.exit(1)
    return result

def ollama_running():
    """Check if Ollama server is up."""
    try:
        import urllib.request
        urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=2)
        return True
    except:
        return False

def model_exists():
    """Check if model is pulled."""
    try:
        import urllib.request, json
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=5) as resp:
            data = json.load(resp)
            return any(MODEL in m.get('name', '') for m in data.get('models', []))
    except:
        return False

def ensure_venv():
    """Create venv and install packages."""
    if not VENV_DIR.exists():
        print("📦 Creating virtual environment...")
        run(f'python3 -m venv "{VENV_DIR}"')
    
    pip = VENV_DIR / "bin" / "pip"
    print("📦 Installing dependencies...")
    run(f'"{pip}" install -q ollama fastapi uvicorn jinja2')

def ensure_ollama():
    """Start Ollama if not running."""
    if ollama_running():
        print("✅ Ollama already running")
        return
    
    print("🚀 Starting Ollama...")
    if shutil.which("ollama"):
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        print("❌ Ollama not installed. Install from https://ollama.ai")
        sys.exit(1)
    
    # Wait for Ollama to be ready
    for _ in range(30):
        if ollama_running():
            print("✅ Ollama ready")
            return
        time.sleep(1)
    print("❌ Ollama failed to start")
    sys.exit(1)

def ensure_model():
    """Pull model if missing."""
    if model_exists():
        print(f"✅ Model {MODEL} already exists")
        return
    
    print(f"⬇️  Pulling model {MODEL} (this may take a minute)...")
    run(f"ollama pull {MODEL}")
    print("✅ Model ready")

def run_cli():
    """Run CLI chat."""
    python = VENV_DIR / "bin" / "python"
    print("\n🎭 Starting CLI mode... (type 'exit' to quit)\n")
    os.execv(str(python), [str(python), "main.py", "cli"])

def run_web():
    """Run web UI."""
    python = VENV_DIR / "bin" / "python"
    print(f"\n🌐 Starting Web UI at http://localhost:{WEB_PORT}")
    print("   Press Ctrl+C to stop\n")
    
    # Open browser after a moment
    import threading
    def open_browser():
        time.sleep(2)
        import webbrowser
        webbrowser.open(f"http://localhost:{WEB_PORT}")
    threading.Thread(target=open_browser, daemon=True).start()
    
    os.execv(str(python), [str(python), "main.py", "web"])

def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║  Kurumi Tokisaki AI — Spirit of Time                      ║
║  Nightmare · Zafkiel's Wielder · One-Click Launcher       ║
╚══════════════════════════════════════════════════════════╝
""")
    
    # Change to project dir
    os.chdir(PROJECT_DIR)
    
    # Setup
    ensure_venv()
    ensure_ollama()
    ensure_model()
    
    # Choose mode
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        print("Choose mode:")
        print("  1) CLI Chat (terminal)")
        print("  2) Web UI (browser)")
        print("  3) Both (web in background + CLI)")
        mode = input("Enter choice [1/2/3]: ").strip()
    
    if mode in ("1", "cli"):
        run_cli()
    elif mode in ("2", "web"):
        run_web()
    elif mode in ("3", "both"):
        # Start web in background, then CLI
        python = VENV_DIR / "bin" / "python"
        web_proc = subprocess.Popen([str(python), "main.py", "web"])
        time.sleep(2)
        import webbrowser
        webbrowser.open(f"http://localhost:{WEB_PORT}")
        print("\n🌐 Web UI running at http://localhost:8000")
        print("🎭 Starting CLI mode...\n")
        try:
            run_cli()
        finally:
            web_proc.terminate()
    else:
        print("Invalid choice")
        sys.exit(1)

if __name__ == "__main__":
    main()