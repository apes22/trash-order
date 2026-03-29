"""TIC Management — main FastAPI application."""

import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

import time
from backend.database import create_tables
from backend.auth import verify_pin, create_token
from backend.ordering import router as ordering_router
from backend.pricing import router as pricing_router

# Import sling scheduler routes
from sling.api import app as sling_app

app = FastAPI(title="TIC Management", version="1.0.0")

# Create database tables on startup
@app.on_event("startup")
def startup():
    for attempt in range(5):
        try:
            create_tables()
            print("Database connected and tables created.")
            return
        except Exception as e:
            print(f"DB connection attempt {attempt + 1}/5 failed: {e}")
            if attempt < 4:
                time.sleep(3)
    print("WARNING: Could not connect to database on startup. Will retry on first request.")

# ===== AUTH =====

@app.post("/api/login")
async def login(data: dict):
    pin = data.get("pin", "")
    role = verify_pin(pin)
    if role:
        token = create_token(role)
        return {"token": token, "role": role}
    return JSONResponse(status_code=401, content={"error": "Wrong PIN"})

# ===== ORDERING GUIDE ROUTES =====
app.include_router(ordering_router)
app.include_router(pricing_router)

# ===== SLING SCHEDULER ROUTES =====
# Mount the sling FastAPI app at /sling-api
app.mount("/sling-api", sling_app)

# ===== STATIC FILES =====
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ===== SPA ROUTES =====
@app.get("/")
async def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/schedule/{path:path}")
async def schedule_page(path: str = ""):
    return FileResponse(os.path.join(STATIC_DIR, "schedule", "index.html"))


@app.get("/pricing/{path:path}")
async def pricing_page(path: str = ""):
    return FileResponse(os.path.join(STATIC_DIR, "pricing", "index.html"))


@app.get("/{path:path}")
async def spa_fallback(path: str):
    file_path = os.path.join(STATIC_DIR, path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))
