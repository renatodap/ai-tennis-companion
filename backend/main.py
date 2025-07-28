from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.upload import router as upload_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # or ["*"] for all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, prefix="/api")

from fastapi.staticfiles import StaticFiles

# Serve static files and handle SPA routing
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
