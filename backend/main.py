from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.upload import router as upload_router
import os

app = FastAPI(title="Tennis AI", description="AI-powered tennis stroke analysis")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API routes BEFORE static files
app.include_router(upload_router, prefix="/api")

# Serve static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Serve the main HTML file for all non-API routes
@app.get("/")
async def read_index():
    return FileResponse('frontend/index.html')

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # If it's an API route, let it pass through
    if full_path.startswith("api/"):
        return {"error": "API route not found"}
    
    # Check if the requested file exists
    file_path = os.path.join("frontend", full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # For all other routes, serve the main HTML (SPA routing)
    return FileResponse('frontend/index.html')
