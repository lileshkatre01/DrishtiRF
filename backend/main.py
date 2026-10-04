from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
from backend.core.logging import logger
from backend.db.session import Base, engine
from backend.api.routers import health, upload, results, ws

# Auto-create SQLite database tables for development scaffold
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Automated analysis of .IQ and .WAV files with signal parameter extraction (SIH 2026 PS 26147)"
)

# CORS configuration for Vite React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(health.router, prefix=settings.API_V1_STR)
app.include_router(upload.router, prefix=settings.API_V1_STR)
app.include_router(results.router, prefix=settings.API_V1_STR)
app.include_router(ws.router, prefix=settings.API_V1_STR)

import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.core.utils import resource_path

@app.get("/api")
def root_api():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health"
    }

# Mount static frontend assets if frontend/dist exists (Desktop standalone / Production build)
dist_dir = resource_path(os.path.join("frontend", "dist"))
if os.path.exists(dist_dir):
    assets_dir = os.path.join(dist_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str = ""):
        if full_path.startswith("api") or full_path.startswith("docs") or full_path.startswith("openapi.json") or full_path.startswith("ws"):
            return None
        file_path = os.path.join(dist_dir, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(dist_dir, "index.html"))
else:
    @app.get("/")
    def root():
        return {
            "message": f"Welcome to {settings.PROJECT_NAME} API",
            "docs": "/docs",
            "health": f"{settings.API_V1_STR}/health"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
