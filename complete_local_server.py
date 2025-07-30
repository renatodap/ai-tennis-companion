#!/usr/bin/env python3
"""
🎾 TennisViz Complete Local Development Server
Serves frontend files + handles backend API for video uploads
"""

import os
import sys
import json
import asyncio
import threading
import webbrowser
import time
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(title="TennisViz Local Dev Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get project paths
PROJECT_ROOT = Path(__file__).parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
BACKEND_DIR = PROJECT_ROOT / "backend"

# Ensure directories exist
FRONTEND_DIR.mkdir(exist_ok=True)
BACKEND_DIR.mkdir(exist_ok=True)

@app.get("/")
async def root():
    """Serve the main app"""
    return FileResponse(FRONTEND_DIR / "tennisviz-app.html")

@app.get("/tennisviz-app.html")
async def serve_app():
    """Serve the main app"""
    return FileResponse(FRONTEND_DIR / "tennisviz-app.html")

@app.post("/api/upload")
async def upload_video(file: UploadFile = File(...)):
    """Handle video upload"""
    print(f"🎾 Received video upload: {file.filename}")
    
    if not file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="File must be a video")
    
    # Save uploaded file temporarily
    upload_path = BACKEND_DIR / "temp_uploads"
    upload_path.mkdir(exist_ok=True)
    
    file_path = upload_path / file.filename
    
    try:
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        print(f"✅ Video saved: {file_path}")
        
        # Return mock analysis results for now
        mock_results = {
            "status": "success",
            "filename": file.filename,
            "size": len(content),
            "message": "Video uploaded successfully! Analysis would start here.",
            "timeline": [
                {
                    "time": 2.5,
                    "stroke_type": "forehand",
                    "confidence": 0.85,
                    "description": "Clean forehand with good follow-through"
                },
                {
                    "time": 5.1,
                    "stroke_type": "backhand", 
                    "confidence": 0.78,
                    "description": "Two-handed backhand, slightly late contact"
                },
                {
                    "time": 8.3,
                    "stroke_type": "serve",
                    "confidence": 0.92,
                    "description": "First serve with good toss placement"
                }
            ],
            "analytics": {
                "total_strokes": 3,
                "forehand_count": 1,
                "backhand_count": 1,
                "serve_count": 1,
                "average_confidence": 0.85
            },
            "ai_insights": {
                "summary": "Good overall technique with consistent stroke mechanics. Focus on timing for backhand shots.",
                "recommendations": [
                    "Work on earlier preparation for backhand shots",
                    "Maintain current serve toss consistency",
                    "Continue developing forehand power"
                ]
            }
        }
        
        return mock_results
        
    except Exception as e:
        print(f"❌ Error processing upload: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")

@app.post("/api/analyze")
async def analyze_video():
    """Mock video analysis endpoint"""
    print("🔍 Starting video analysis...")
    
    # Simulate processing time
    await asyncio.sleep(2)
    
    return {
        "status": "completed",
        "message": "Analysis completed successfully!",
        "results": {
            "stroke_events": [
                {
                    "time": 1.2,
                    "stroke_type": "forehand",
                    "confidence": 0.89,
                    "court_position": [0.3, 0.7],
                    "technique_score": 8.5
                },
                {
                    "time": 3.8,
                    "stroke_type": "backhand",
                    "confidence": 0.82,
                    "court_position": [0.7, 0.6],
                    "technique_score": 7.8
                }
            ]
        }
    }

# Mount static files (with no-cache headers)
class NoCacheStaticFiles(StaticFiles):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        if hasattr(response, 'headers'):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response

# Mount frontend static files
app.mount("/", NoCacheStaticFiles(directory=str(FRONTEND_DIR), html=True), name="static")

def open_browser_delayed(url: str, delay: int = 3):
    """Open browser after server starts"""
    time.sleep(delay)
    print(f"🚀 Opening browser: {url}")
    webbrowser.open(url)

def main():
    """Start the complete local development server"""
    port = 8000
    host = "localhost"
    
    print("🎾 TennisViz Complete Local Development Server")
    print("=" * 60)
    print(f"📁 Frontend: {FRONTEND_DIR}")
    print(f"📁 Backend: {BACKEND_DIR}")
    print(f"🌐 Server: http://{host}:{port}")
    print(f"📱 App URL: http://{host}:{port}/tennisviz-app.html")
    print("=" * 60)
    print("✨ Features:")
    print("  • Frontend serving with no-cache headers")
    print("  • Backend API for video uploads")
    print("  • Mock analysis results")
    print("  • Auto-opens browser")
    print("  • CORS enabled for local development")
    print("=" * 60)
    
    # Start browser in background thread
    browser_thread = threading.Thread(
        target=open_browser_delayed,
        args=(f"http://{host}:{port}/tennisviz-app.html",)
    )
    browser_thread.daemon = True
    browser_thread.start()
    
    print(f"🚀 Starting server on http://{host}:{port}")
    print("💡 Press Ctrl+C to stop")
    print("🔄 Upload videos to test the complete flow!")
    
    try:
        # Start the server
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
