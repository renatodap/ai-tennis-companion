import cv2
import os
import logging
import traceback
from typing import Tuple

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


