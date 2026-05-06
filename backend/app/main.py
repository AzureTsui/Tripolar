import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from app.config import CORS_ORIGINS
from app.database import init_db
from app.routers import articles, categories, sources, ai_tools

app = FastAPI(title="Tripolar", description="AI Product Radar")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ORIGINS] if CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(articles.router)
app.include_router(categories.router)
app.include_router(sources.router)
app.include_router(ai_tools.router)

# Serve built frontend in production
frontend_dist = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "frontend", "dist"
)

if os.path.isdir(frontend_dist):
    app.mount(
        "/assets",
        StaticFiles(directory=os.path.join(frontend_dist, "assets")),
        name="assets",
    )

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(404)
        # Serve static files at root (favicon.ico, etc.)
        if full_path:
            file_path = os.path.join(frontend_dist, full_path)
            if os.path.isfile(file_path):
                return FileResponse(file_path)
        # SPA fallback
        index_path = os.path.join(frontend_dist, "index.html")
        if os.path.isfile(index_path):
            return FileResponse(index_path, media_type="text/html")
        return JSONResponse(
            {"detail": "Frontend not built. Run: cd frontend && npm run build"},
            status_code=501,
        )


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok"}
