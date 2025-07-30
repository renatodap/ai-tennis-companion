"""
🎾 TENNISVIZ FASTAPI BACKEND
Enhanced API endpoints for elite tennis analytics
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
import asyncio
import logging
import time
import os
from pathlib import Path
from typing import Optional, Dict, Any
import tempfile
import shutil

# Import our TennisViz analytics modules
from tennisviz_analyzer import TennisVizAnalyzer, SessionType, CameraView, AnalysisMode
from analytics.advanced_analytics import AdvancedAnalyticsEngine
from analytics.serve_analyzer import ServeAnalyzer, TossAnalyzer
from analytics.ai_coach import AICoach

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="TennisViz - Elite Tennis Analytics",
    description="Professional tennis analysis with AI-powered insights",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware for PWA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for PWA
frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Initialize analytics components
tennis_analyzer = TennisVizAnalyzer()
advanced_analytics = AdvancedAnalyticsEngine()
serve_analyzer = ServeAnalyzer()
toss_analyzer = TossAnalyzer()
ai_coach = AICoach()

# Global state for tracking analyses
active_analyses = {}

@app.get("/")
async def root():
    """Serve the main TennisViz PWA application"""
    return FileResponse(str(frontend_path / "tennisviz-app.html"))

@app.get("/index.html")
async def serve_index():
    """Redirect old index.html to TennisViz PWA"""
    return FileResponse(str(frontend_path / "tennisviz-app.html"))

@app.get("/tennisviz-app.html")
async def serve_app():
    """Serve the TennisViz PWA"""
    return FileResponse(str(frontend_path / "tennisviz-app.html"))

@app.get("/timeline_viewer.html")
async def redirect_timeline():
    """Redirect old timeline viewer to TennisViz PWA"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/", status_code=302)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "components": {
            "tennis_analyzer": "ready",
            "advanced_analytics": "ready",
            "serve_analyzer": "ready",
            "ai_coach": "ready"
        }
    }

@app.post("/api/analyze")
async def analyze_video_legacy(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    config: str = Form("{}")
):
    """
    🎾 Legacy analysis endpoint for compatibility
    Redirects to main TennisViz analysis with default settings
    """
    # Parse config if provided
    import json
    try:
        config_data = json.loads(config) if config else {}
    except:
        config_data = {}
    
    # Use default settings for legacy calls
    session_type = config_data.get('session_type', 'practice')
    camera_view = config_data.get('camera_view', 'side_view')
    analysis_mode = config_data.get('analysis_mode', 'technique')
    
    # Call main analysis function
    return await analyze_tennis_video(
        background_tasks=background_tasks,
        video=file,
        session_type=session_type,
        camera_view=camera_view,
        analysis_mode=analysis_mode
    )

@app.post("/api/analyze-tennisviz")
async def analyze_tennis_video(
    background_tasks: BackgroundTasks,
    video: UploadFile = File(...),
    session_type: str = Form("practice"),
    camera_view: str = Form("side_view"),
    analysis_mode: str = Form("technique")
):
    """
    🎾 Main TennisViz analysis endpoint
    Processes tennis videos with professional-grade analytics
    """
    
    # Generate analysis ID
    analysis_id = f"analysis_{int(time.time())}"
    
    # Validate inputs
    try:
        session_type_enum = SessionType(session_type)
        camera_view_enum = CameraView(camera_view)
        analysis_mode_enum = AnalysisMode(analysis_mode)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {e}")
    
    # Validate file
    if not video.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="File must be a video")
    
    # Check file size (max 500MB)
    max_size = 500 * 1024 * 1024
    if video.size and video.size > max_size:
        raise HTTPException(status_code=413, detail="File too large. Maximum 500MB allowed.")
    
    logger.info(f"🎾 Starting analysis {analysis_id}: {session_type} ({camera_view}, {analysis_mode})")
    
    # Track analysis
    active_analyses[analysis_id] = {
        "status": "processing",
        "start_time": time.time(),
        "session_type": session_type,
        "camera_view": camera_view,
        "analysis_mode": analysis_mode
    }
    
    try:
        # Save uploaded video temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            temp_path = temp_file.name
            shutil.copyfileobj(video.file, temp_file)
        
        # Process video with TennisViz analyzer
        logger.info(f"🎾 Processing video: {video.filename}")
        
        results = await tennis_analyzer.analyze_session(
            video_path=temp_path,
            session_type=session_type_enum,
            camera_view=camera_view_enum,
            analysis_mode=analysis_mode_enum
        )
        
        # Enhance with advanced analytics
        if results.get('timeline'):
            logger.info("📊 Generating advanced analytics...")
            
            # Generate comprehensive analytics
            advanced_results = await advanced_analytics.generate_comprehensive_analytics(
                results['timeline'], 
                results.get('court_info', {})
            )
            
            # Merge advanced analytics
            results['analytics'].update(advanced_results)
            
            # Add serve-specific analysis if applicable
            if session_type_enum == SessionType.SERVE:
                logger.info("🎾 Generating serve analysis...")
                serve_results = await serve_analyzer.analyze_serves(results['timeline'])
                toss_results = await toss_analyzer.analyze_toss_mechanics(
                    results['timeline'], 
                    []  # Would pass pose data in full implementation
                )
                
                results['analytics']['serve_analysis'] = serve_results
                results['analytics']['toss_analysis'] = toss_results
            
            # Generate AI insights
            logger.info("🧠 Generating AI coaching insights...")
            ai_insights = await ai_coach.generate_insights(
                results['timeline'],
                results['analytics'],
                results['session_metadata']
            )
            
            results['ai_insights'] = ai_insights
        
        # Update analysis status
        active_analyses[analysis_id].update({
            "status": "completed",
            "end_time": time.time(),
            "results": results
        })
        
        # Clean up temporary file
        background_tasks.add_task(cleanup_temp_file, temp_path)
        
        logger.info(f"✅ Analysis {analysis_id} completed successfully")
        
        return JSONResponse(content={
            "analysis_id": analysis_id,
            "status": "success",
            **results
        })
        
    except Exception as e:
        # Update analysis status
        active_analyses[analysis_id].update({
            "status": "failed",
            "error": str(e),
            "end_time": time.time()
        })
        
        logger.error(f"❌ Analysis {analysis_id} failed: {str(e)}")
        
        # Clean up on error
        if 'temp_path' in locals():
            background_tasks.add_task(cleanup_temp_file, temp_path)
        
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/analysis/{analysis_id}")
async def get_analysis_status(analysis_id: str):
    """Get analysis status and results"""
    
    if analysis_id not in active_analyses:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis = active_analyses[analysis_id]
    
    return {
        "analysis_id": analysis_id,
        "status": analysis["status"],
        "start_time": analysis["start_time"],
        "end_time": analysis.get("end_time"),
        "processing_time": analysis.get("end_time", time.time()) - analysis["start_time"],
        "session_config": {
            "session_type": analysis["session_type"],
            "camera_view": analysis["camera_view"],
            "analysis_mode": analysis["analysis_mode"]
        },
        "results": analysis.get("results"),
        "error": analysis.get("error")
    }

@app.get("/api/analyses")
async def list_analyses():
    """List all analyses"""
    
    analyses_list = []
    for analysis_id, analysis in active_analyses.items():
        analyses_list.append({
            "analysis_id": analysis_id,
            "status": analysis["status"],
            "start_time": analysis["start_time"],
            "session_type": analysis["session_type"],
            "camera_view": analysis["camera_view"],
            "analysis_mode": analysis["analysis_mode"]
        })
    
    return {
        "analyses": sorted(analyses_list, key=lambda x: x["start_time"], reverse=True),
        "total": len(analyses_list)
    }

@app.delete("/api/analysis/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """Delete analysis results"""
    
    if analysis_id not in active_analyses:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    del active_analyses[analysis_id]
    
    return {"message": f"Analysis {analysis_id} deleted successfully"}

@app.post("/api/feedback")
async def submit_feedback(
    analysis_id: str = Form(...),
    rating: int = Form(...),
    feedback: str = Form(""),
    stroke_corrections: str = Form("")
):
    """Submit user feedback for analysis improvement"""
    
    if analysis_id not in active_analyses:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Store feedback (in production, save to database)
    feedback_data = {
        "analysis_id": analysis_id,
        "rating": rating,
        "feedback": feedback,
        "stroke_corrections": stroke_corrections,
        "timestamp": time.time()
    }
    
    logger.info(f"📝 Received feedback for {analysis_id}: {rating}/5 stars")
    
    return {
        "message": "Feedback submitted successfully",
        "feedback_id": f"feedback_{int(time.time())}"
    }

@app.get("/api/stats")
async def get_system_stats():
    """Get system statistics"""
    
    total_analyses = len(active_analyses)
    completed_analyses = sum(1 for a in active_analyses.values() if a["status"] == "completed")
    failed_analyses = sum(1 for a in active_analyses.values() if a["status"] == "failed")
    
    # Calculate average processing time
    processing_times = [
        a.get("end_time", time.time()) - a["start_time"] 
        for a in active_analyses.values() 
        if a["status"] in ["completed", "failed"]
    ]
    
    avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
    
    return {
        "total_analyses": total_analyses,
        "completed_analyses": completed_analyses,
        "failed_analyses": failed_analyses,
        "success_rate": (completed_analyses / total_analyses * 100) if total_analyses > 0 else 0,
        "average_processing_time": avg_processing_time,
        "system_uptime": time.time() - start_time,
        "version": "1.0.0"
    }

# Utility functions
async def cleanup_temp_file(file_path: str):
    """Clean up temporary files"""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
            logger.info(f"🧹 Cleaned up temporary file: {file_path}")
    except Exception as e:
        logger.error(f"Failed to clean up {file_path}: {e}")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": time.time()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": time.time()
        }
    )

# Startup event
start_time = time.time()

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("🎾 TennisViz API starting up...")
    logger.info("✅ TennisViz API ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🎾 TennisViz API shutting down...")
    
    # Clean up any remaining temporary files
    for analysis in active_analyses.values():
        if "temp_path" in analysis:
            await cleanup_temp_file(analysis["temp_path"])
    
    logger.info("✅ TennisViz API shutdown complete")

if __name__ == "__main__":
    uvicorn.run(
        "tennisviz_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
