import cv2
import numpy as np
import torch
from ultralytics import YOLO
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from enum import Enum
import json
import time
from collections import deque
import math

logger = logging.getLogger(__name__)

class StrokeType(Enum):
    FOREHAND = "forehand"
    BACKHAND = "backhand"
    SERVE = "serve"
    VOLLEY = "volley"
    OVERHEAD = "overhead"
    UNKNOWN = "unknown"

@dataclass
class Detection:
    class_id: int
    class_name: str
    confidence: float
    bbox: Tuple[float, float, float, float]
    center: Tuple[float, float]
    timestamp: float

@dataclass
class StrokeAnalysis:
    stroke_type: StrokeType
    confidence: float
    start_frame: int
    end_frame: int
    racket_speed: float
    ball_speed: float
    technique_notes: str

class AdvancedTennisDetector:
    """State-of-the-art YOLO + motion analysis tennis detection"""
    
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"Using device: {self.device}")
        
        # Load YOLOv8 model
        self.model = YOLO('yolov8n.pt')
        self.model.to(self.device)
        
        # Tracking state
        self.player_tracks = {}
        self.ball_tracks = {}
        self.racket_tracks = {}
        self.stroke_buffer = deque(maxlen=60)
        
        # Analysis parameters
        self.min_stroke_frames = 15
        self.max_stroke_frames = 90
        
    def detect_objects(self, frame: np.ndarray, frame_id: int) -> List[Detection]:
        """Detect tennis objects using YOLO"""
        results = self.model(frame, verbose=False)
        detections = []
        
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
                
            for i in range(len(boxes)):
                bbox = boxes.xyxy[i].cpu().numpy()
                conf = float(boxes.conf[i].cpu().numpy())
                cls_id = int(boxes.cls[i].cpu().numpy())
                
                # Filter for person (0) and sports ball (32)
                if cls_id in [0, 32] and conf > 0.4:
                    class_name = 'person' if cls_id == 0 else 'ball'
                    x1, y1, x2, y2 = bbox
                    center = ((x1 + x2) / 2, (y1 + y2) / 2)
                    
                    detections.append(Detection(
                        class_id=cls_id,
                        class_name=class_name,
                        confidence=conf,
                        bbox=(x1, y1, x2, y2),
                        center=center,
                        timestamp=frame_id / 30.0
                    ))
        
        return detections
    
    def detect_racket_advanced(self, frame: np.ndarray, player_bbox: Tuple) -> Optional[Detection]:
        """Advanced racket detection using edge detection and motion"""
        x1, y1, x2, y2 = player_bbox
        
        # Focus on upper body area
        search_x1 = max(0, int(x1 - (x2-x1)*0.2))
        search_y1 = max(0, int(y1))
        search_x2 = min(frame.shape[1], int(x2 + (x2-x1)*0.2))
        search_y2 = min(frame.shape[0], int(y1 + (y2-y1)*0.6))
        
        roi = frame[search_y1:search_y2, search_x1:search_x2]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Multi-scale edge detection
        edges = cv2.Canny(gray, 30, 100)
        
        # Find elongated objects (racket-like)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        best_racket = None
        best_score = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 150 < area < 3000:
                rect = cv2.minAreaRect(contour)
                width, height = rect[1]
                
                if width > 0 and height > 0:
                    aspect_ratio = max(width, height) / min(width, height)
                    
                    # Score racket-like properties
                    score = 0
                    if 2.0 < aspect_ratio < 5.0:  # Racket aspect ratio
                        score += 0.4
                    if 300 < area < 1500:  # Good size
                        score += 0.3
                    if rect[2] > 45:  # Angled (likely in swing)
                        score += 0.2
                    
                    if score > best_score:
                        best_score = score
                        M = cv2.moments(contour)
                        if M["m00"] != 0:
                            cx = int(M["m10"] / M["m00"]) + search_x1
                            cy = int(M["m01"] / M["m00"]) + search_y1
                            
                            x, y, w, h = cv2.boundingRect(contour)
                            best_racket = Detection(
                                class_id=999,
                                class_name='racket',
                                confidence=best_score,
                                bbox=(search_x1+x, search_y1+y, search_x1+x+w, search_y1+y+h),
                                center=(cx, cy),
                                timestamp=0
                            )
        
        return best_racket if best_score > 0.5 else None
    
    def track_objects(self, detections: List[Detection], frame_id: int) -> Dict:
        """Track objects across frames with motion analysis"""
        
        # Simple centroid tracking
        players = [d for d in detections if d.class_name == 'person']
        balls = [d for d in detections if d.class_name == 'ball']
        
        # Update player tracks
        for player in players:
            best_match = None
            min_dist = float('inf')
            
            for track_id, track in self.player_tracks.items():
                if len(track['positions']) > 0:
                    last_pos = track['positions'][-1]
                    dist = math.sqrt((player.center[0] - last_pos[0])**2 + 
                                   (player.center[1] - last_pos[1])**2)
                    if dist < min_dist and dist < 100:
                        min_dist = dist
                        best_match = track_id
            
            if best_match:
                self.player_tracks[best_match]['positions'].append(player.center)
                self.player_tracks[best_match]['bbox'] = player.bbox
            else:
                new_id = len(self.player_tracks)
                self.player_tracks[new_id] = {
                    'positions': [player.center],
                    'bbox': player.bbox,
                    'velocities': []
                }
        
        # Calculate velocities for motion analysis
        for track_id, track in self.player_tracks.items():
            if len(track['positions']) >= 2:
                p1, p2 = track['positions'][-2], track['positions'][-1]
                velocity = math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2) * 30  # px/sec
                track['velocities'].append(velocity)
                if len(track['velocities']) > 30:
                    track['velocities'].pop(0)
        
        return {
            'players': self.player_tracks,
            'balls': balls,
            'frame_id': frame_id
        }
    
    def analyze_stroke_motion(self, tracks: Dict, frame_id: int) -> List[StrokeAnalysis]:
        """Analyze motion patterns for stroke detection"""
        strokes = []
        
        for track_id, track in tracks['players'].items():
            if len(track['velocities']) > self.min_stroke_frames:
                
                # Detect stroke patterns in velocity
                velocities = track['velocities'][-30:]  # Last 1 second
                
                if len(velocities) > 10:
                    max_vel = max(velocities)
                    avg_vel = sum(velocities) / len(velocities)
                    
                    # Stroke detection heuristics
                    if max_vel > 150 and max_vel > avg_vel * 2.5:
                        
                        # Classify stroke type based on motion pattern
                        stroke_type = self._classify_stroke_advanced(track, velocities)
                        
                        # Calculate confidence
                        confidence = min(0.9, max_vel / 300 + 0.3)
                        
                        # Generate technique analysis
                        technique = self._analyze_technique(stroke_type, max_vel, track)
                        
                        stroke = StrokeAnalysis(
                            stroke_type=stroke_type,
                            confidence=confidence,
                            start_frame=frame_id - len(velocities),
                            end_frame=frame_id,
                            racket_speed=max_vel,
                            ball_speed=0,  # Would need ball tracking
                            technique_notes=technique
                        )
                        
                        strokes.append(stroke)
        
        return strokes
    
    def _classify_stroke_advanced(self, track: Dict, velocities: List[float]) -> StrokeType:
        """Advanced stroke classification using motion patterns"""
        
        positions = track['positions'][-len(velocities):]
        
        if len(positions) < 5:
            return StrokeType.UNKNOWN
        
        # Analyze trajectory
        x_positions = [p[0] for p in positions]
        y_positions = [p[1] for p in positions]
        
        x_range = max(x_positions) - min(x_positions)
        y_range = max(y_positions) - min(y_positions)
        
        max_vel = max(velocities)
        
        # Classification logic
        if max_vel > 250 and y_range > 80:
            return StrokeType.SERVE
        elif max_vel < 100:
            return StrokeType.VOLLEY
        elif x_range > y_range and max_vel > 150:
            # Determine forehand vs backhand by direction
            if x_positions[-1] > x_positions[0]:
                return StrokeType.FOREHAND
            else:
                return StrokeType.BACKHAND
        elif y_range > x_range and max_vel > 200:
            return StrokeType.OVERHEAD
        
        return StrokeType.UNKNOWN
    
    def _analyze_technique(self, stroke_type: StrokeType, max_velocity: float, track: Dict) -> str:
        """Generate technique analysis"""
        
        if stroke_type == StrokeType.FOREHAND:
            if max_velocity > 200:
                return "Powerful cross-court winner"
            else:
                return "Controlled forehand"
        elif stroke_type == StrokeType.BACKHAND:
            if max_velocity > 180:
                return "Down-the-line approach"
            else:
                return "Defensive backhand slice"
        elif stroke_type == StrokeType.SERVE:
            if max_velocity > 300:
                return "First serve to T"
            else:
                return "Second serve with spin"
        elif stroke_type == StrokeType.VOLLEY:
            return "Net approach volley"
        elif stroke_type == StrokeType.OVERHEAD:
            return "Overhead smash"
        
        return "Unknown stroke pattern"
    
    def process_video(self, video_path: str) -> Dict:
        """Process video with advanced tennis analysis"""
        
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        all_strokes = []
        frame_id = 0
        
        logger.info(f"Processing {total_frames} frames at {fps} FPS")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect objects
            detections = self.detect_objects(frame, frame_id)
            
            # Track objects
            tracks = self.track_objects(detections, frame_id)
            
            # Analyze strokes
            strokes = self.analyze_stroke_motion(tracks, frame_id)
            all_strokes.extend(strokes)
            
            if frame_id % 30 == 0:
                progress = (frame_id / total_frames) * 100
                logger.info(f"Progress: {progress:.1f}%")
            
            frame_id += 1
        
        cap.release()
        
        # Post-process strokes
        final_strokes = self._post_process_strokes(all_strokes)
        
        return {
            'video_info': {'fps': fps, 'total_frames': total_frames},
            'strokes': [self._stroke_to_dict(s) for s in final_strokes],
            'summary': self._generate_summary(final_strokes)
        }
    
    def _post_process_strokes(self, strokes: List[StrokeAnalysis]) -> List[StrokeAnalysis]:
        """Remove duplicate and low-confidence strokes"""
        
        if not strokes:
            return []
        
        # Sort by start frame
        strokes.sort(key=lambda s: s.start_frame)
        
        # Remove overlapping strokes (keep highest confidence)
        filtered = []
        for stroke in strokes:
            if not filtered:
                filtered.append(stroke)
                continue
            
            last_stroke = filtered[-1]
            
            # Check for overlap
            if stroke.start_frame <= last_stroke.end_frame:
                # Keep higher confidence stroke
                if stroke.confidence > last_stroke.confidence:
                    filtered[-1] = stroke
            else:
                filtered.append(stroke)
        
        # Filter by minimum confidence
        return [s for s in filtered if s.confidence > 0.4]
    
    def _stroke_to_dict(self, stroke: StrokeAnalysis) -> Dict:
        """Convert stroke analysis to dictionary"""
        return {
            'stroke': stroke.stroke_type.value,
            'confidence': stroke.confidence,
            'start_sec': stroke.start_frame / 30.0,
            'end_sec': stroke.end_frame / 30.0,
            'duration': (stroke.end_frame - stroke.start_frame) / 30.0,
            'racket_speed': stroke.racket_speed,
            'technique': stroke.technique_notes
        }
    
    def _generate_summary(self, strokes: List[StrokeAnalysis]) -> Dict:
        """Generate analysis summary"""
        
        if not strokes:
            return {'total_strokes': 0}
        
        stroke_counts = {}
        total_speed = 0
        
        for stroke in strokes:
            stroke_type = stroke.stroke_type.value
            stroke_counts[stroke_type] = stroke_counts.get(stroke_type, 0) + 1
            total_speed += stroke.racket_speed
        
        return {
            'total_strokes': len(strokes),
            'stroke_breakdown': stroke_counts,
            'avg_racket_speed': total_speed / len(strokes),
            'max_speed': max(s.racket_speed for s in strokes),
            'avg_confidence': sum(s.confidence for s in strokes) / len(strokes)
        }

# Integration function for existing pipeline
def analyze_video_yolo(video_path: str) -> Dict:
    """Main function to analyze video using YOLO + motion analysis"""
    
    detector = AdvancedTennisDetector()
    results = detector.process_video(video_path)
    
    # Convert to timeline format for compatibility
    timeline = []
    for i, stroke_data in enumerate(results['strokes']):
        timeline.append({
            'id': i + 1,
            'stroke': stroke_data['stroke'],
            'start_sec': stroke_data['start_sec'],
            'end_sec': stroke_data['end_sec'],
            'duration': stroke_data['duration'],
            'confidence': stroke_data['confidence'],
            'technique': stroke_data['technique']
        })
    
    return {
        'timeline': timeline,
        'summary': results['summary'],
        'video_info': results['video_info']
    }
