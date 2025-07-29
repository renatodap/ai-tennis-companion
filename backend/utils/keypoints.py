import mediapipe as mp
import cv2
import os
import json
import logging
import traceback
from typing import Optional

mp_pose = mp.solutions.pose
logger = logging.getLogger(__name__)

def extract_keypoints_from_frames(frame_dir: str, output_path: str) -> str:
    """Extract keypoints from frames with robust error handling."""
    logger.info(f"Starting keypoint extraction from {frame_dir}")
    
    if not os.path.exists(frame_dir):
        raise FileNotFoundError(f"Frame directory not found: {frame_dir}")
    
    # Get list of frame files
    frame_files = [f for f in sorted(os.listdir(frame_dir)) if f.endswith(".jpg")]
    if not frame_files:
        raise ValueError(f"No .jpg files found in {frame_dir}")
    
    logger.info(f"Found {len(frame_files)} frame files to process")
    
    pose = None
    keypoints_data = {}
    processed_count = 0
    error_count = 0
    
    try:
        # Initialize MediaPipe Pose with error handling
        try:
            pose = mp_pose.Pose(
                static_image_mode=True,
                model_complexity=1,  # Use lighter model for better performance
                enable_segmentation=False,
                min_detection_confidence=0.5
            )
            logger.info("MediaPipe Pose initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MediaPipe Pose: {str(e)}")
            raise RuntimeError(f"MediaPipe initialization failed: {str(e)}")
        
        # Process each frame with individual error handling
        for i, file in enumerate(frame_files):
            try:
                frame_path = os.path.join(frame_dir, file)
                
                # Read image with error handling
                image = cv2.imread(frame_path)
                if image is None:
                    logger.warning(f"Could not read image: {frame_path}")
                    keypoints_data[file] = None
                    error_count += 1
                    continue
                
                # Convert color space and process
                try:
                    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    results = pose.process(rgb_image)
                    
                    if results.pose_landmarks:
                        keypoints_data[file] = [
                            {
                                "x": float(lm.x),
                                "y": float(lm.y),
                                "z": float(lm.z),
                                "visibility": float(lm.visibility)
                            }
                            for lm in results.pose_landmarks.landmark
                        ]
                        processed_count += 1
                    else:
                        keypoints_data[file] = None
                        
                except Exception as e:
                    logger.warning(f"Error processing frame {file}: {str(e)}")
                    keypoints_data[file] = None
                    error_count += 1
                
                # Log progress every 10 frames
                if (i + 1) % 10 == 0:
                    logger.info(f"Processed {i + 1}/{len(frame_files)} frames")
                    
            except Exception as e:
                logger.error(f"Unexpected error processing frame {file}: {str(e)}")
                keypoints_data[file] = None
                error_count += 1
                continue
        
        logger.info(f"Keypoint extraction complete: {processed_count} successful, {error_count} errors")
        
        # Validate that we got some results
        if processed_count == 0:
            raise RuntimeError("No keypoints could be extracted from any frame")
        
        # Save results with error handling
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(keypoints_data, f, indent=2)
            logger.info(f"Keypoints saved to {output_path}")
        except Exception as e:
            logger.error(f"Error saving keypoints: {str(e)}")
            raise RuntimeError(f"Failed to save keypoints: {str(e)}")
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error in extract_keypoints_from_frames: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
    finally:
        # Clean up MediaPipe resources
        if pose is not None:
            try:
                pose.close()
                logger.info("MediaPipe Pose resources cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up MediaPipe resources: {str(e)}")
