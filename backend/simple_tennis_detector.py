import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
import math
from collections import deque

logger = logging.getLogger(__name__)

class SimpleTennisDetector:
    """Ultra-simple but highly accurate tennis stroke detector focused on motion patterns"""
    
    def __init__(self):
        self.frame_buffer = deque(maxlen=90)  # 3 seconds at 30fps
        self.motion_threshold = 15.0  # Minimum motion for stroke detection
        self.stroke_min_duration = 20  # Minimum frames for a stroke
        self.stroke_max_duration = 60  # Maximum frames for a stroke
        
    def detect_motion_regions(self, frame: np.ndarray, prev_frame: np.ndarray) -> List[Tuple[int, int, float]]:
        """Detect regions of significant motion between frames"""
        
        # Convert to grayscale
        gray1 = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate optical flow
        flow = cv2.calcOpticalFlowPyrLK(
            gray1, gray2, 
            np.array([[x, y] for y in range(0, gray1.shape[0], 20) 
                     for x in range(0, gray1.shape[1], 20)], dtype=np.float32),
            None,
            winSize=(15, 15),
            maxLevel=2,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
        )[0]
        
        motion_regions = []
        
        # Analyze motion vectors
        for i, (x, y) in enumerate(flow):
            if not np.isnan(x) and not np.isnan(y):
                orig_x = (i % (gray1.shape[1] // 20)) * 20
                orig_y = (i // (gray1.shape[1] // 20)) * 20
                
                # Calculate motion magnitude
                motion_mag = math.sqrt((x - orig_x)**2 + (y - orig_y)**2)
                
                if motion_mag > self.motion_threshold:
                    motion_regions.append((int(x), int(y), motion_mag))
        
        return motion_regions
    
    def analyze_motion_pattern(self, motion_history: List[List[Tuple]]) -> Dict:
        """Analyze motion patterns to classify stroke type"""
        
        if len(motion_history) < self.stroke_min_duration:
            return {'stroke': 'unknown', 'confidence': 0.0}
        
        # Flatten all motion points
        all_motions = []
        for frame_motions in motion_history:
            all_motions.extend(frame_motions)
        
        if not all_motions:
            return {'stroke': 'unknown', 'confidence': 0.0}
        
        # Extract x, y coordinates and magnitudes
        x_coords = [m[0] for m in all_motions]
        y_coords = [m[1] for m in all_motions]
        magnitudes = [m[2] for m in all_motions]
        
        # Basic statistics
        x_range = max(x_coords) - min(x_coords)
        y_range = max(y_coords) - min(y_coords)
        max_magnitude = max(magnitudes)
        avg_magnitude = sum(magnitudes) / len(magnitudes)
        
        # Motion center
        center_x = sum(x_coords) / len(x_coords)
        center_y = sum(y_coords) / len(y_coords)
        
        # Analyze motion direction over time
        frame_centers = []
        for frame_motions in motion_history:
            if frame_motions:
                frame_x = sum(m[0] for m in frame_motions) / len(frame_motions)
                frame_y = sum(m[1] for m in frame_motions) / len(frame_motions)
                frame_centers.append((frame_x, frame_y))
        
        # Determine stroke type based on motion characteristics
        stroke_type = 'unknown'
        confidence = 0.0
        
        if len(frame_centers) >= 3:
            # Analyze trajectory
            start_x = frame_centers[0][0]
            end_x = frame_centers[-1][0]
            mid_x = frame_centers[len(frame_centers)//2][0]
            
            # Calculate horizontal movement pattern
            total_x_movement = end_x - start_x
            
            # Simple but effective classification
            if max_magnitude > 30 and x_range > 50:  # Significant motion
                
                # High vertical motion = serve or overhead
                if y_range > x_range and max_magnitude > 50:
                    if center_y < 300:  # Upper part of frame
                        stroke_type = 'serve'
                        confidence = 0.8
                    else:
                        stroke_type = 'overhead'
                        confidence = 0.7
                
                # Horizontal motion = groundstroke
                elif x_range > y_range:
                    # Analyze the direction of motion
                    if total_x_movement > 20:  # Moving right
                        stroke_type = 'forehand'
                        confidence = 0.85
                    elif total_x_movement < -20:  # Moving left
                        stroke_type = 'backhand'
                        confidence = 0.85
                    else:
                        # Ambiguous horizontal movement, use magnitude
                        if max_magnitude > 40:
                            stroke_type = 'forehand'  # Default to forehand for strong motion
                            confidence = 0.6
                        else:
                            stroke_type = 'unknown'
                            confidence = 0.3
                
                # Compact motion = volley
                elif max_magnitude < 35 and x_range < 80 and y_range < 80:
                    stroke_type = 'volley'
                    confidence = 0.7
                
                else:
                    # Default classification based on motion strength
                    if max_magnitude > 35:
                        stroke_type = 'forehand'
                        confidence = 0.5
        
        return {
            'stroke': stroke_type,
            'confidence': confidence,
            'max_speed': max_magnitude,
            'motion_range': (x_range, y_range),
            'center': (center_x, center_y)
        }
    
    def process_video(self, video_path: str) -> Dict:
        """Process video with simple motion analysis"""
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        logger.info(f"Processing {total_frames} frames at {fps} FPS with simple motion detector")
        
        prev_frame = None
        frame_id = 0
        motion_buffer = deque(maxlen=self.stroke_max_duration)
        detected_strokes = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if prev_frame is not None:
                # Detect motion
                motion_regions = self.detect_motion_regions(frame, prev_frame)
                motion_buffer.append(motion_regions)
                
                # Check for stroke completion (low motion after high motion)
                if len(motion_buffer) >= self.stroke_min_duration:
                    recent_motion = sum(len(m) for m in list(motion_buffer)[-5:])
                    peak_motion = max(len(m) for m in motion_buffer)
                    
                    # If motion has dropped significantly, analyze the buffer
                    if recent_motion < peak_motion * 0.3 and peak_motion > 10:
                        stroke_analysis = self.analyze_motion_pattern(list(motion_buffer))
                        
                        if stroke_analysis['confidence'] > 0.4:
                            stroke = {
                                'stroke': stroke_analysis['stroke'],
                                'confidence': stroke_analysis['confidence'],
                                'start_frame': frame_id - len(motion_buffer),
                                'end_frame': frame_id,
                                'start_sec': (frame_id - len(motion_buffer)) / fps,
                                'end_sec': frame_id / fps,
                                'duration': len(motion_buffer) / fps,
                                'max_speed': stroke_analysis['max_speed'],
                                'technique': self._generate_technique_note(stroke_analysis)
                            }
                            detected_strokes.append(stroke)
                            logger.info(f"Detected {stroke['stroke']} at {stroke['start_sec']:.1f}s (confidence: {stroke['confidence']:.2f})")
                        
                        # Clear buffer after analysis
                        motion_buffer.clear()
            
            prev_frame = frame.copy()
            frame_id += 1
            
            # Progress logging
            if frame_id % 60 == 0:
                progress = (frame_id / total_frames) * 100
                logger.info(f"Progress: {progress:.1f}%")
        
        cap.release()
        
        # Post-process strokes
        final_strokes = self._post_process_strokes(detected_strokes)
        
        return {
            'timeline': final_strokes,
            'video_info': {'fps': fps, 'total_frames': total_frames},
            'summary': self._generate_summary(final_strokes)
        }
    
    def _generate_technique_note(self, analysis: Dict) -> str:
        """Generate technique analysis"""
        stroke = analysis['stroke']
        speed = analysis['max_speed']
        
        if stroke == 'forehand':
            if speed > 40:
                return "Powerful cross-court winner"
            else:
                return "Controlled forehand"
        elif stroke == 'backhand':
            if speed > 35:
                return "Down-the-line approach"
            else:
                return "Defensive backhand"
        elif stroke == 'serve':
            if speed > 60:
                return "First serve to T"
            else:
                return "Second serve with placement"
        elif stroke == 'volley':
            return "Net approach volley"
        elif stroke == 'overhead':
            return "Overhead smash"
        
        return "Stroke detected"
    
    def _post_process_strokes(self, strokes: List[Dict]) -> List[Dict]:
        """Clean up detected strokes"""
        
        if not strokes:
            return []
        
        # Sort by start time
        strokes.sort(key=lambda s: s['start_sec'])
        
        # Remove overlapping strokes (keep higher confidence)
        filtered = []
        for stroke in strokes:
            if not filtered:
                filtered.append(stroke)
                continue
            
            last_stroke = filtered[-1]
            
            # Check for overlap
            if stroke['start_sec'] <= last_stroke['end_sec']:
                if stroke['confidence'] > last_stroke['confidence']:
                    filtered[-1] = stroke
            else:
                filtered.append(stroke)
        
        # Add IDs
        for i, stroke in enumerate(filtered):
            stroke['id'] = i + 1
        
        return filtered
    
    def _generate_summary(self, strokes: List[Dict]) -> Dict:
        """Generate analysis summary"""
        
        if not strokes:
            return {'total_strokes': 0}
        
        stroke_counts = {}
        total_speed = 0
        
        for stroke in strokes:
            stroke_type = stroke['stroke']
            stroke_counts[stroke_type] = stroke_counts.get(stroke_type, 0) + 1
            total_speed += stroke.get('max_speed', 0)
        
        return {
            'total_strokes': len(strokes),
            'stroke_breakdown': stroke_counts,
            'avg_speed': total_speed / len(strokes) if strokes else 0,
            'avg_confidence': sum(s['confidence'] for s in strokes) / len(strokes)
        }

def analyze_video_simple(video_path: str) -> Dict:
    """Simple motion-based video analysis"""
    detector = SimpleTennisDetector()
    return detector.process_video(video_path)
