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
    from core.cli.main import run_pythagora
except ImportError as err:
    print(f"Error importing module: {err}", file=sys.stderr)
    sys.exit(1)

def main():
    if "--cli" in sys.argv:
        sys.exit(run_pythagora())
    else:
        uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()