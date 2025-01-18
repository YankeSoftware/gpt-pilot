#!/usr/bin/env python

import os.path
import sys
from fastapi import FastAPI
import uvicorn

# Create FastAPI app
app = FastAPI(title="GPT-Pilot")

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

try:
    from core.cli.main import run_pilot
except ImportError as err:
    pilot_root = os.path.dirname(__file__)
    venv_path = os.path.join(pilot_root, "venv")
    requirements_path = os.path.join(pilot_root, "requirements.txt")
    if sys.prefix == sys.base_prefix:
        venv_python_path = os.path.join(venv_path, "scripts" if sys.platform == "win32" else "bin", "python")
        print(f"Python environment is not set up: module `{err.name}` is missing.", file=sys.stderr)
        print(f"Please run setup.bat (Windows) or setup.sh (Unix) to set up the environment.", file=sys.stderr)
    else:
        print(f"Environment not completely set up: module `{err.name}` is missing", file=sys.stderr)
        print(f"Please run `{sys.executable} -m pip install -e .` to finish setup.", file=sys.stderr)
    sys.exit(1)

def main():
    if "--cli" in sys.argv:
        sys.exit(run_pilot())
    else:
        uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()