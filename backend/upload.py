from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import os
from datetime import datetime
from backend.process_video import extract_frames
from backend.utils.keypoints import extract_keypoints_from_frames
from backend.classify_strokes import classify_strokes, group_strokes
import shutil
import json

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
async def analyze_video(file: UploadFile = File(...)):
    # 1) Build paths
    filename    = f"{datetime.now():%Y%m%d-%H%M%S}_{file.filename}"
    video_path  = os.path.join(UPLOAD_DIR, filename)
    frames_dir  = os.path.join(UPLOAD_DIR, "frames")
    keypoint_json = os.path.join(UPLOAD_DIR, "keypoints.json")

    # 2) Save the uploaded file to disk
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 3) Run your pipeline
    num_frames, fps = extract_frames(video_path, frames_dir)
    extract_keypoints_from_frames(frames_dir, keypoint_json)
    strokes  = classify_strokes(keypoint_json)
    timeline = group_strokes(strokes, fps)

    # 4) Write out the new timeline for the frontend
    os.makedirs("frontend", exist_ok=True)
    timeline_output = "frontend/timeline.json"
    with open(timeline_output, "w") as f:
        json.dump(timeline, f, indent=2)

    # 5) Copy the video into frontend so it’s always at a known URL
    shutil.copy(video_path, "frontend/sample_video.mp4")

    # 6) Sync the frames folder *after* extraction
    dst_frames = "frontend/frames"
    if os.path.isdir(dst_frames):
        shutil.rmtree(dst_frames)
    shutil.copytree(frames_dir, dst_frames)

    # 7) Return the result
    return JSONResponse(content={"timeline": timeline, "fps": fps})
