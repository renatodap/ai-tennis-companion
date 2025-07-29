from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
import os
import asyncio
import logging
from datetime import datetime
from backend.process_video import extract_frames
from backend.utils.keypoints import extract_keypoints_from_frames
from backend.classify_strokes import classify_strokes, group_strokes
import shutil
import json
import traceback
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_DIR = "backend/test_data"

os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    filename = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}_{file.filename}"
    path = os.path.join(UPLOAD_DIR, filename)

    with open(path, "wb") as f:
        f.write(await file.read())

    # For now: just return dummy classification result
    dummy_output = [
        {"stroke": "serve", "start": "00:00:01.00", "end": "00:00:02.00"},
        {"stroke": "forehand", "start": "00:00:03.00", "end": "00:00:03.50"},
    ]

    return JSONResponse(content={"status": "uploaded", "file": filename, "output": dummy_output})

@router.post("/analyze")
async def analyze_video(file: UploadFile = File(...), config: str = Form(...)):
    logger.info(f"Starting video analysis for file: {file.filename}")
    
    # Parse configuration
    try:
        video_config = json.loads(config)
        logger.info(f"Video configuration: {video_config}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid configuration data")
    
    # Validate file size (50MB limit for production)
    if file.size and file.size > 50 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB.")
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a video file.")
    
    try:
        # 1) Build paths with better error handling
        filename = f"{datetime.now():%Y%m%d-%H%M%S}_{file.filename}"
        video_path = os.path.join(UPLOAD_DIR, filename)
        frames_dir = os.path.join(UPLOAD_DIR, "frames")
        keypoint_json = os.path.join(UPLOAD_DIR, "keypoints.json")
        
        logger.info(f"Processing paths: video={video_path}, frames={frames_dir}")

        # 2) Save the uploaded file to disk with timeout
        try:
            content = await asyncio.wait_for(file.read(), timeout=30.0)
            with open(video_path, "wb") as buffer:
                buffer.write(content)
            logger.info(f"Video saved successfully: {len(content)} bytes")
        except asyncio.TimeoutError:
            raise HTTPException(status_code=408, detail="File upload timeout")
        except Exception as e:
            logger.error(f"Error saving video: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to save video file")

        # 3) Run pipeline with timeout and error handling
        try:
            # Frame extraction with timeout
            logger.info("Starting frame extraction...")
            num_frames, fps = await asyncio.wait_for(
                asyncio.to_thread(extract_frames, video_path, frames_dir), 
                timeout=60.0
            )
            
            if num_frames == 0:
                raise HTTPException(status_code=400, detail="Could not extract frames from video")
            
            logger.info(f"Extracted {num_frames} frames at {fps} FPS")
            
            # Keypoint extraction with timeout
            logger.info("Starting keypoint extraction...")
            await asyncio.wait_for(
                asyncio.to_thread(extract_keypoints_from_frames, frames_dir, keypoint_json),
                timeout=120.0
            )
            
            # Check if keypoints were extracted
            if not os.path.exists(keypoint_json):
                raise HTTPException(status_code=500, detail="Failed to extract keypoints")
            
            logger.info("Keypoints extracted successfully")
            
            # Stroke classification
            logger.info("Starting stroke classification...")
            strokes = await asyncio.wait_for(
                asyncio.to_thread(classify_strokes, keypoint_json),
                timeout=30.0
            )
            
            timeline = group_strokes(strokes, fps)
            logger.info(f"Classification complete: {len(timeline)} strokes detected")
            
        except asyncio.TimeoutError:
            logger.error("Processing timeout occurred")
            raise HTTPException(status_code=408, detail="Video processing timeout. Try a shorter video.")
        except Exception as e:
            logger.error(f"Processing error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Video processing failed: {str(e)}")

        # 4) Write out the new timeline for the frontend
        try:
            os.makedirs("frontend", exist_ok=True)
            timeline_output = "frontend/timeline.json"
            with open(timeline_output, "w") as f:
                json.dump(timeline, f, indent=2)
            logger.info("Timeline saved successfully")
        except Exception as e:
            logger.error(f"Error saving timeline: {str(e)}")
            # Continue without failing - timeline can be returned in response

        # 5) Copy the video into frontend (optional, don't fail if it doesn't work)
        try:
            shutil.copy(video_path, "frontend/sample_video.mp4")
            logger.info("Video copied to frontend")
        except Exception as e:
            logger.warning(f"Could not copy video to frontend: {str(e)}")

        # 6) Sync the frames folder (optional)
        try:
            dst_frames = "frontend/frames"
            if os.path.isdir(dst_frames):
                shutil.rmtree(dst_frames)
            shutil.copytree(frames_dir, dst_frames)
            logger.info("Frames synced to frontend")
        except Exception as e:
            logger.warning(f"Could not sync frames: {str(e)}")

        # 7) Cleanup temporary files
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
            if os.path.exists(keypoint_json):
                os.remove(keypoint_json)
            if os.path.isdir(frames_dir):
                shutil.rmtree(frames_dir)
            logger.info("Temporary files cleaned up")
        except Exception as e:
            logger.warning(f"Cleanup warning: {str(e)}")

        # 8) Return the result
        logger.info("Analysis completed successfully")
        return JSONResponse(content={
            "timeline": timeline, 
            "fps": fps,
            "total_strokes": len(timeline),
            "status": "success"
        })
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analyze_video: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during video analysis")
