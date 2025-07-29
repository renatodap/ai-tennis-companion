import json
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class StrokeType(Enum):
    FOREHAND = "forehand"
    BACKHAND = "backhand"
    SERVE = "serve"
    VOLLEY = "volley"
    OVERHEAD = "overhead"
    UNKNOWN = "unknown"

@dataclass
class StrokeAnalysis:
    stroke_type: StrokeType
    confidence: float
    frame: str
    features: Dict[str, float]
    
class TennisStrokeDetector:
    """Bulletproof MediaPipe-based tennis stroke detection system"""
    
    # MediaPipe pose landmark indices
    POSE_LANDMARKS = {
        'nose': 0,
        'left_eye_inner': 1, 'left_eye': 2, 'left_eye_outer': 3,
        'right_eye_inner': 4, 'right_eye': 5, 'right_eye_outer': 6,
        'left_ear': 7, 'right_ear': 8,
        'mouth_left': 9, 'mouth_right': 10,
        'left_shoulder': 11, 'right_shoulder': 12,
        'left_elbow': 13, 'right_elbow': 14,
        'left_wrist': 15, 'right_wrist': 16,
        'left_pinky': 17, 'right_pinky': 18,
        'left_index': 19, 'right_index': 20,
        'left_thumb': 21, 'right_thumb': 22,
        'left_hip': 23, 'right_hip': 24,
        'left_knee': 25, 'right_knee': 26,
        'left_ankle': 27, 'right_ankle': 28,
        'left_heel': 29, 'right_heel': 30,
        'left_foot_index': 31, 'right_foot_index': 32
    }
    
    def __init__(self):
        self.confidence_threshold = 0.3
        self.min_visibility = 0.5
        
    def extract_landmarks(self, landmarks: List[Dict]) -> Dict[str, Dict[str, float]]:
        """Extract and validate MediaPipe landmarks"""
        extracted = {}
        
        for name, idx in self.POSE_LANDMARKS.items():
            try:
                if idx < len(landmarks) and landmarks[idx]:
                    landmark = landmarks[idx]
                    # Ensure landmark has required fields
                    if all(key in landmark for key in ['x', 'y']):
                        visibility = landmark.get('visibility', 1.0)
                        if visibility >= self.min_visibility:
                            extracted[name] = {
                                'x': float(landmark['x']),
                                'y': float(landmark['y']),
                                'z': float(landmark.get('z', 0.0)),
                                'visibility': float(visibility)
                            }
            except (IndexError, TypeError, KeyError, ValueError) as e:
                logger.debug(f"Failed to extract landmark {name}: {e}")
                continue
                
        return extracted
    
    def calculate_angle(self, p1: Dict, p2: Dict, p3: Dict) -> Optional[float]:
        """Calculate angle between three points"""
        try:
            # Vector from p2 to p1
            v1 = np.array([p1['x'] - p2['x'], p1['y'] - p2['y']])
            # Vector from p2 to p3
            v2 = np.array([p3['x'] - p2['x'], p3['y'] - p2['y']])
            
            # Calculate angle
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            cos_angle = np.clip(cos_angle, -1.0, 1.0)  # Handle numerical errors
            angle = np.arccos(cos_angle)
            return np.degrees(angle)
        except (ZeroDivisionError, ValueError, KeyError):
            return None
    
    def calculate_distance(self, p1: Dict, p2: Dict) -> Optional[float]:
        """Calculate Euclidean distance between two points"""
        try:
            return np.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)
        except (KeyError, TypeError):
            return None
    
    def extract_stroke_features(self, landmarks: Dict[str, Dict]) -> Dict[str, float]:
        """Extract comprehensive stroke features from landmarks"""
        features = {}
        
        # Required landmarks for analysis
        required = ['left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow', 
                   'left_wrist', 'right_wrist', 'left_hip', 'right_hip']
        
        if not all(landmark in landmarks for landmark in required):
            return features
        
        try:
            # Basic positions
            ls, rs = landmarks['left_shoulder'], landmarks['right_shoulder']
            le, re = landmarks['left_elbow'], landmarks['right_elbow']
            lw, rw = landmarks['left_wrist'], landmarks['right_wrist']
            lh, rh = landmarks['left_hip'], landmarks['right_hip']
            
            # Body center and dimensions
            body_center_x = (ls['x'] + rs['x']) / 2
            body_center_y = (ls['y'] + rs['y']) / 2
            shoulder_width = abs(rs['x'] - ls['x'])
            body_height = abs((ls['y'] + rs['y']) / 2 - (lh['y'] + rh['y']) / 2)
            
            # Wrist positions relative to body
            features['left_wrist_rel_x'] = (lw['x'] - body_center_x) / shoulder_width if shoulder_width > 0 else 0
            features['right_wrist_rel_x'] = (rw['x'] - body_center_x) / shoulder_width if shoulder_width > 0 else 0
            features['left_wrist_rel_y'] = (lw['y'] - body_center_y) / body_height if body_height > 0 else 0
            features['right_wrist_rel_y'] = (rw['y'] - body_center_y) / body_height if body_height > 0 else 0
            
            # Wrist separation
            wrist_distance = self.calculate_distance(lw, rw)
            features['wrist_separation'] = wrist_distance / shoulder_width if wrist_distance and shoulder_width > 0 else 0
            
            # Arm angles
            left_arm_angle = self.calculate_angle(ls, le, lw)
            right_arm_angle = self.calculate_angle(rs, re, rw)
            features['left_arm_angle'] = left_arm_angle if left_arm_angle else 0
            features['right_arm_angle'] = right_arm_angle if right_arm_angle else 0
            
            # Shoulder angles
            left_shoulder_angle = self.calculate_angle(lh, ls, le)
            right_shoulder_angle = self.calculate_angle(rh, rs, re)
            features['left_shoulder_angle'] = left_shoulder_angle if left_shoulder_angle else 0
            features['right_shoulder_angle'] = right_shoulder_angle if right_shoulder_angle else 0
            
            # Height analysis
            avg_shoulder_y = (ls['y'] + rs['y']) / 2
            avg_wrist_y = (lw['y'] + rw['y']) / 2
            features['wrists_above_shoulders'] = 1.0 if avg_wrist_y < avg_shoulder_y else 0.0
            features['wrist_height_diff'] = (avg_shoulder_y - avg_wrist_y) / body_height if body_height > 0 else 0
            
            # Asymmetry analysis
            features['wrist_height_asymmetry'] = abs(lw['y'] - rw['y']) / body_height if body_height > 0 else 0
            features['arm_angle_diff'] = abs(left_arm_angle - right_arm_angle) if left_arm_angle and right_arm_angle else 0
            
            # Cross-body analysis
            features['left_wrist_crosses_center'] = 1.0 if lw['x'] > body_center_x else 0.0
            features['right_wrist_crosses_center'] = 1.0 if rw['x'] < body_center_x else 0.0
            
            # Extension analysis
            left_arm_extension = self.calculate_distance(ls, lw)
            right_arm_extension = self.calculate_distance(rs, rw)
            max_arm_reach = shoulder_width * 1.5  # Approximate max reach
            features['left_arm_extension'] = left_arm_extension / max_arm_reach if left_arm_extension and max_arm_reach > 0 else 0
            features['right_arm_extension'] = right_arm_extension / max_arm_reach if right_arm_extension and max_arm_reach > 0 else 0
            
        except Exception as e:
            logger.warning(f"Error extracting stroke features: {e}")
            
        return features
    
    def classify_stroke(self, features: Dict[str, float]) -> Tuple[StrokeType, float]:
        """Classify stroke type based on extracted features with confidence scoring"""
        
        if not features:
            return StrokeType.UNKNOWN, 0.0
        
        confidence_scores = {stroke: 0.0 for stroke in StrokeType}
        
        # Serve detection (highest priority)
        if features.get('wrists_above_shoulders', 0) > 0.5:
            serve_confidence = 0.7
            
            # Additional serve indicators
            if features.get('wrist_height_diff', 0) > 0.1:
                serve_confidence += 0.15
            if features.get('right_arm_extension', 0) > 0.7:  # Assuming right-handed
                serve_confidence += 0.1
            if features.get('right_shoulder_angle', 0) > 120:
                serve_confidence += 0.05
                
            confidence_scores[StrokeType.SERVE] = min(serve_confidence, 0.95)
        
        # Overhead detection
        if (features.get('wrists_above_shoulders', 0) > 0.5 and 
            features.get('wrist_height_diff', 0) > 0.05 and
            features.get('wrist_separation', 0) < 0.8):
            
            overhead_confidence = 0.6
            if features.get('right_arm_angle', 0) > 140:
                overhead_confidence += 0.2
            if features.get('wrist_height_asymmetry', 0) > 0.1:
                overhead_confidence += 0.1
                
            confidence_scores[StrokeType.OVERHEAD] = min(overhead_confidence, 0.9)
        
        # Volley detection (close to net, compact swing)
        if (features.get('wrist_separation', 0) < 1.0 and
            features.get('left_arm_extension', 0) < 0.6 and
            features.get('right_arm_extension', 0) < 0.6):
            
            volley_confidence = 0.5
            if features.get('wrist_height_diff', 0) < 0.05:  # Level with shoulders
                volley_confidence += 0.2
            if features.get('arm_angle_diff', 0) < 30:  # Similar arm positions
                volley_confidence += 0.1
                
            confidence_scores[StrokeType.VOLLEY] = min(volley_confidence, 0.8)
        
        # Forehand vs Backhand detection
        wrist_sep = features.get('wrist_separation', 0)
        left_crosses = features.get('left_wrist_crosses_center', 0)
        right_crosses = features.get('right_wrist_crosses_center', 0)
        
        if wrist_sep > 1.2:  # Wide separation indicates groundstroke
            # Forehand indicators (assuming right-handed player)
            if (features.get('right_wrist_rel_x', 0) > 0.3 and
                features.get('left_wrist_rel_x', 0) < 0.1):
                
                forehand_confidence = 0.6
                if features.get('right_arm_extension', 0) > 0.7:
                    forehand_confidence += 0.2
                if features.get('right_arm_angle', 0) > 120:
                    forehand_confidence += 0.1
                if not right_crosses:
                    forehand_confidence += 0.1
                    
                confidence_scores[StrokeType.FOREHAND] = min(forehand_confidence, 0.9)
            
            # Backhand indicators
            elif (features.get('left_wrist_rel_x', 0) > 0.2 and
                  features.get('right_wrist_rel_x', 0) > 0.1):
                
                backhand_confidence = 0.6
                if features.get('wrist_separation', 0) > 1.5:  # Two-handed backhand
                    backhand_confidence += 0.2
                if features.get('left_arm_extension', 0) > 0.6:
                    backhand_confidence += 0.1
                if left_crosses:
                    backhand_confidence += 0.1
                    
                confidence_scores[StrokeType.BACKHAND] = min(backhand_confidence, 0.9)
        
        # Find best classification
        best_stroke = max(confidence_scores.items(), key=lambda x: x[1])
        
        if best_stroke[1] < self.confidence_threshold:
            return StrokeType.UNKNOWN, best_stroke[1]
        
        return best_stroke[0], best_stroke[1]
    
    def analyze_frame(self, landmarks: List[Dict], frame_name: str) -> StrokeAnalysis:
        """Analyze a single frame for stroke detection"""
        
        # Extract and validate landmarks
        extracted_landmarks = self.extract_landmarks(landmarks)
        
        if len(extracted_landmarks) < 8:  # Need minimum landmarks for analysis
            return StrokeAnalysis(
                stroke_type=StrokeType.UNKNOWN,
                confidence=0.0,
                frame=frame_name,
                features={}
            )
        
        # Extract stroke features
        features = self.extract_stroke_features(extracted_landmarks)
        
        # Classify stroke
        stroke_type, confidence = self.classify_stroke(features)
        
        return StrokeAnalysis(
            stroke_type=stroke_type,
            confidence=confidence,
            frame=frame_name,
            features=features
        )

def classify_strokes(keypoint_json_path: str) -> List[Dict]:
    """Main function to classify strokes from keypoint data"""
    
    try:
        with open(keypoint_json_path, "r") as f:
            keypoints = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading keypoints file: {e}")
        return []
    
    detector = TennisStrokeDetector()
    stroke_analyses = []
    frame_names = sorted(keypoints.keys())
    
    logger.info(f"Analyzing {len(frame_names)} frames for stroke detection")
    
    for frame_name in frame_names:
        landmarks = keypoints.get(frame_name, [])
        
        if not landmarks:
            analysis = StrokeAnalysis(
                stroke_type=StrokeType.UNKNOWN,
                confidence=0.0,
                frame=frame_name,
                features={}
            )
        else:
            analysis = detector.analyze_frame(landmarks, frame_name)
        
        stroke_analyses.append(analysis)
    
    # Convert to legacy format for compatibility
    strokes = []
    for analysis in stroke_analyses:
        strokes.append({
            "frame": analysis.frame,
            "stroke": analysis.stroke_type.value,
            "confidence": analysis.confidence,
            "features": analysis.features
        })
    
    logger.info(f"Stroke detection complete. Found {len([s for s in strokes if s['stroke'] != 'unknown'])} valid strokes")
    return strokes

def frame_to_seconds(frame_filename: str, fps: float) -> float:
    """Convert frame filename to timestamp in seconds"""
    try:
        # Extract frame number from filename (assumes format: frame_XXXX.jpg)
        frame_num = int(frame_filename.split("_")[1].split(".")[0])
        return round(frame_num / fps, 2)
    except (IndexError, ValueError):
        logger.warning(f"Could not parse frame number from filename: {frame_filename}")
        return 0.0

def group_strokes(strokes: List[Dict], fps: float, min_duration: float = 0.1) -> List[Dict]:
    """Group consecutive similar strokes with improved logic"""
    
    if not strokes:
        return []
    
    timeline = []
    current_group = None
    
    for stroke_data in strokes:
        stroke_type = stroke_data["stroke"]
        confidence = stroke_data.get("confidence", 0.0)
        frame = stroke_data["frame"]
        
        # Skip low-confidence unknown strokes
        if stroke_type == "unknown" and confidence < 0.1:
            if current_group and current_group["stroke"] != "unknown":
                # End current group
                current_group["end"] = stroke_data.get("previous_frame", frame)
                current_group["end_sec"] = frame_to_seconds(current_group["end"], fps)
                
                # Check minimum duration
                duration = current_group["end_sec"] - current_group["start_sec"]
                if duration >= min_duration:
                    timeline.append(current_group)
                
                current_group = None
            continue
        
        # Start new group or continue existing
        if current_group is None or current_group["stroke"] != stroke_type:
            # End previous group
            if current_group:
                current_group["end"] = stroke_data.get("previous_frame", frame)
                current_group["end_sec"] = frame_to_seconds(current_group["end"], fps)
                
                duration = current_group["end_sec"] - current_group["start_sec"]
                if duration >= min_duration:
                    timeline.append(current_group)
            
            # Start new group
            current_group = {
                "stroke": stroke_type,
                "start": frame,
                "start_sec": frame_to_seconds(frame, fps),
                "confidence": confidence,
                "max_confidence": confidence
            }
        else:
            # Continue current group, update confidence
            current_group["max_confidence"] = max(current_group["max_confidence"], confidence)
            current_group["confidence"] = (current_group["confidence"] + confidence) / 2  # Running average
        
        # Store previous frame for next iteration
        stroke_data["previous_frame"] = frame
    
    # Handle final group
    if current_group:
        current_group["end"] = current_group.get("end", strokes[-1]["frame"])
        current_group["end_sec"] = frame_to_seconds(current_group["end"], fps)
        
        duration = current_group["end_sec"] - current_group["start_sec"]
        if duration >= min_duration:
            timeline.append(current_group)
    
    # Sort by start time and add metadata
    timeline.sort(key=lambda x: x["start_sec"])
    
    for i, stroke in enumerate(timeline):
        stroke["id"] = i + 1
        stroke["duration"] = round(stroke["end_sec"] - stroke["start_sec"], 2)
    
    logger.info(f"Grouped into {len(timeline)} stroke sequences")
    return timeline
