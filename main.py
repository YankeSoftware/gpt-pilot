#!/usr/bin/env python

import os.path
import sys
from typing import List, Optional
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="GPT-Pilot",
    debug=True
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Models
class ProjectBase(BaseModel):
    name: str
    description: str

class Project(ProjectBase):
    id: str
    status: str
    created_at: str

class ProjectCreate(ProjectBase):
    pass

class ProjectList(BaseModel):
    projects: List[Project]

# In-memory storage for demo
projects = {}

@app.get("/")
async def root():
    logger.debug("Root endpoint called")
    return {"message": "GPT-Pilot API is running"}

@app.get("/health")
async def health_check(response: Response):
    try:
        logger.debug("Health check endpoint called")
        return {"status": "healthy", "timestamp": str(os.path.getmtime(__file__))}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"status": "unhealthy", "error": str(e)}

@app.get("/api/projects", response_model=ProjectList)
async def list_projects():
    logger.debug("List projects endpoint called")
    return {"projects": list(projects.values())}

@app.get("/api/projects/{project_id}", response_model=Project)
async def get_project(project_id: str, response: Response):
    logger.debug(f"Get project endpoint called for id: {project_id}")
    if project_id not in projects:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Project not found"}
    return projects[project_id]

@app.post("/api/projects", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(project: ProjectCreate):
    logger.debug(f"Create project endpoint called with data: {project}")
    project_id = str(len(projects) + 1)  # Simple ID generation
    new_project = Project(
        id=project_id,
        name=project.name,
        description=project.description,
        status="active",
        created_at=datetime.now().isoformat()
    )
    projects[project_id] = new_project
    return new_project

@app.post("/api/projects/{project_id}/start")
async def start_development(project_id: str, response: Response):
    logger.debug(f"Start development endpoint called for id: {project_id}")
    if project_id not in projects:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Project not found"}
    projects[project_id].status = "active"
    return {"status": "Development started"}

@app.post("/api/projects/{project_id}/pause")
async def pause_development(project_id: str, response: Response):
    logger.debug(f"Pause development endpoint called for id: {project_id}")
    if project_id not in projects:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Project not found"}
    projects[project_id].status = "paused"
    return {"status": "Development paused"}

try:
    from core.cli.main import run_pythagora
except ImportError as err:
    logger.error(f"Error importing module: {err}")
    sys.exit(1)

def main():
    logger.info("Starting GPT-Pilot server...")
    if "--cli" in sys.argv:
        sys.exit(run_pythagora())
    else:
        try:
            logger.info("Starting web server - access via http://localhost:8000")
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=8000,
                log_level="debug",
                access_log=True,
                timeout_keep_alive=65
            )
        except Exception as e:
            logger.error(f"Server failed to start: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    main()