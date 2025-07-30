import cv2
import os
import logging
import traceback
from typing import Tuple
import json
from .classify_strokes import classify_strokes, group_strokes
from .professional_tennis_analyzer import analyze_video_professional

logger = logging.getLogger(__name__)

def extract_frames(video_path: str, output_dir: str, max_frames: int = 150) -> Tuple[int, float]:
    """Extract frames from video with robust error handling."""
    logger.info(f"Starting frame extraction from {video_path}")
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    # Create output directory
    try:
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Output directory created: {output_dir}")
    except Exception as e:
        logger.error(f"Failed to create output directory: {str(e)}")
        raise RuntimeError(f"Cannot create output directory: {str(e)}")
    
    cap = None
    saved = 0
    fps = 0.0
    
    try:
        # Initialize video capture
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            logger.error(f"Could not open video: {video_path}")
            raise RuntimeError(f"Failed to open video file: {video_path}")
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        logger.info(f"Video properties: FPS={fps:.2f}, Total frames={total_frames}, Duration={duration:.2f}s")
        
        if fps <= 0 or fps > 120:  # Sanity check
            logger.warning(f"Unusual FPS detected: {fps}, using default 30")
            fps = 30.0
        
        # Calculate frame skip to respect max_frames limit
        frame_skip = max(1, total_frames // max_frames) if total_frames > max_frames else 1
        logger.info(f"Frame skip: {frame_skip} (to limit to {max_frames} frames)")
        
        frame_count = 0
        while cap.isOpened() and saved < max_frames:
            ret, frame = cap.read()
            if not ret:
                logger.info("End of video reached")
                break
            
            # Skip frames if necessary
            if frame_count % frame_skip == 0:
                try:
                    frame_path = os.path.join(output_dir, f"frame_{saved:04d}.jpg")
                    
                    # Validate frame
                    if frame is None or frame.size == 0:
                        logger.warning(f"Invalid frame at position {frame_count}")
                        frame_count += 1
                        continue
                    
                    # Resize frame if too large (to save processing time)
                    height, width = frame.shape[:2]
                    if width > 1280 or height > 720:
                        scale = min(1280/width, 720/height)
                        new_width = int(width * scale)
                        new_height = int(height * scale)
                        frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
                        logger.info(f"Resized frame from {width}x{height} to {new_width}x{new_height}")
                    
                    # Save frame
                    success = cv2.imwrite(frame_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    if not success:
                        logger.warning(f"Failed to save frame {saved}")
                        continue
                    
                    saved += 1
                    
                    # Log progress
                    if saved % 20 == 0:
                        logger.info(f"Extracted {saved} frames")
                        
                except Exception as e:
                    logger.warning(f"Error saving frame {saved}: {str(e)}")
                    continue
            
            frame_count += 1
        
        logger.info(f"Frame extraction complete: {saved} frames saved")
        
        if saved == 0:
            raise RuntimeError("No frames could be extracted from the video")
        
        return saved, fps
        
    except Exception as e:
        logger.error(f"Error in extract_frames: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
    finally:
        # Clean up resources
        if cap is not None:
            try:
                cap.release()
                logger.info("Video capture resources released")
            except Exception as e:
                logger.warning(f"Error releasing video capture: {str(e)}")

def process_video_analysis(video_path: str, output_dir: str) -> dict:
    """Process video using advanced YOLO + motion analysis"""
    
    try:
        logger.info(f"Starting professional tennis analysis for: {video_path}")
        
        # Use professional-grade analysis (TennisViz-style)
        results = analyze_video_professional(video_path)
        
        # Add additional metadata
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        
        # Enhance timeline with additional data
        enhanced_timeline = []
        for stroke in results['timeline']:
            enhanced_stroke = {
                'id': stroke['id'],
                'stroke': stroke['stroke'],
                'start_sec': stroke['start_sec'],
                'end_sec': stroke['end_sec'],
                'duration': stroke['duration'],
                'confidence': stroke['confidence'],
                'technique': stroke.get('technique', 'Advanced stroke analysis'),
                'analysis_method': 'Professional Context Analysis'
            }
            enhanced_timeline.append(enhanced_stroke)
        
        logger.info(f"YOLO analysis complete. Found {len(enhanced_timeline)} strokes")
        
        return {
            "timeline": enhanced_timeline,
            "fps": fps,
            "total_frames": total_frames,
            "analysis_method": "Professional Context Analysis",
            "summary": results.get('summary', {}),
            "video_info": results.get('video_info', {})
        }
        
    except Exception as e:
        logger.error(f"Professional analysis failed, falling back to MediaPipe: {e}")
        
        # Fallback to MediaPipe if YOLO fails
        return process_video_analysis_mediapipe(video_path, output_dir)

def process_video_analysis_mediapipe(video_path: str, output_dir: str) -> dict:
    """Fallback MediaPipe processing"""
    import mediapipe as mp
    
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = 0
    keypoints_data = {}
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        results = pose.process(rgb_frame)
        
        frame_name = f"frame_{frame_count:04d}.jpg"
        
        if results.pose_landmarks:
            # Extract keypoints
            landmarks = []
            for landmark in results.pose_landmarks.landmark:
                landmarks.append({
                    "x": landmark.x,
                    "y": landmark.y,
                    "z": landmark.z,
                    "visibility": landmark.visibility
                })
            keypoints_data[frame_name] = landmarks
        else:
            keypoints_data[frame_name] = []
        
        frame_count += 1
    
    cap.release()
    pose.close()
    
    # Save keypoints
    keypoints_path = os.path.join(output_dir, "keypoints.json")
    with open(keypoints_path, "w") as f:
        json.dump(keypoints_data, f)
    
    # Classify strokes
    strokes = classify_strokes(keypoints_path)
    
    # Group strokes into timeline
    timeline = group_strokes(strokes, fps)
    
    return {
        "timeline": timeline,
        "fps": fps,
        "total_frames": frame_count,
        "keypoints_file": keypoints_path,
        "analysis_method": "MediaPipe (Fallback)"
    }


