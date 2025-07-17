"""
InboxCast FastAPI Web Application
Main entry point for the demo web app showcasing end-to-end functionality.
"""

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.routers import auth, rss, content, audio

# Load environment variables from local.env
load_dotenv(dotenv_path="local.env")

# Create FastAPI app
app = FastAPI(
    title="InboxCast Demo",
    description="Demo web app for converting inbox emails and RSS feeds into podcast-style audio",
    version="0.1.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(rss.router, prefix="/api/rss", tags=["rss"])
app.include_router(content.router, prefix="/api/content", tags=["content"])
app.include_router(audio.router, prefix="/api/audio", tags=["audio"])


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main demo page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "InboxCast Demo"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)