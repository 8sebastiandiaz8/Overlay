import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from backend.config import settings
from backend.database import get_pool, close_pool
from backend.routers import auth, overlays, widgets, store, payments, websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    if settings.DATABASE_URL:
        await get_pool()
    yield
    await close_pool()


app = FastAPI(
    title="OverlayForge",
    description="Platform for streamers to create custom overlays and widgets",
    version="0.1.0",
    lifespan=lifespan,
)

# Static files
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_dir = os.path.join(base_dir, "frontend", "static")
templates_dir = os.path.join(base_dir, "frontend", "templates")

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# Routers
app.include_router(auth.router)
app.include_router(overlays.router)
app.include_router(widgets.router)
app.include_router(store.router)
app.include_router(payments.router)
app.include_router(websocket.router)


@app.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    """Landing page."""
    return templates.TemplateResponse("landing.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Dashboard page."""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/editor/{overlay_id}", response_class=HTMLResponse)
async def editor_page(request: Request, overlay_id: str):
    """Overlay editor page."""
    return templates.TemplateResponse("editor.html", {"request": request, "overlay_id": overlay_id})


@app.get("/store", response_class=HTMLResponse)
async def store_page(request: Request):
    """Widget store page."""
    return templates.TemplateResponse("store.html", {"request": request})


@app.get("/overlay/{token}", response_class=HTMLResponse)
async def overlay_live(request: Request, token: str):
    """Public overlay URL for OBS Browser Source."""
    return templates.TemplateResponse("overlay_live.html", {"request": request, "token": token})
