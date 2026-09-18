# server/main.py
# FastAPI data proxy. Add real integrations per endpoint.
# Run: uvicorn server.main:app --reload --port 8000
# The Vite dev server proxies /api/* here automatically.
# In production, serve the built React app as a static mount.
import sys
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Ensure data_mock is properly recognized as a package for relative imports
sys.path.insert(0, str(Path(__file__).parent))

# Import routers
from routes import weather, climate, calendar, news, media, layout


app = FastAPI()

# Register routers
app.include_router(layout.router)
app.include_router(weather.router)
app.include_router(climate.router)
app.include_router(calendar.router)
app.include_router(news.router)
app.include_router(media.router)

# ── Middleware ────────────────────────────────────────────────────────────
# Comma-separated origins allow both local development and LAN-hosted clients.
cors_origins = [
    origin.strip()
    for origin in os.environ.get(
        "CORS_ORIGINS", "http://localhost:5173"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
