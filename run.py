#!/usr/bin/env python3
"""
Kurumi Tokisaki AI Launcher
Run this script to start the AI chatbot.
"""

import sys
import subprocess
import os

def main():
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(script_dir, 'kurumi_venv', 'bin', 'python')
    main_py = os.path.join(script_dir, 'main.py')
    
    if not os.path.exists(venv_python):
        print("Virtual environment not found. Please run:")
        print("  python3 -m venv kurumi_venv")
        print("  kurumi_venv/bin/pip install ollama fastapi uvicorn jinja2")
        sys.exit(1)
    
    if len(sys.argv) > 1 and sys.argv[1] == 'web':
        # Run web server
        subprocess.run([venv_python, main_py, 'web'])
    else:
        # Run CLI
        subprocess.run([venv_python, main_py, 'cli'])

if __name__ == '__main__':
    main()