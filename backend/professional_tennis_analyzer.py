import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from enum import Enum
import json
import math
from collections import deque
from sklearn.cluster import DBSCAN
import mediapipe as mp

logger = logging.getLogger(__name__)

class CourtZone(Enum):
    BASELINE = "baseline"
    MID_COURT = "mid_court"
    NET = "net"
    SERVICE_BOX = "service_box"
    UNKNOWN = "unknown"

class StrokeContext(Enum):
    RALLY = "rally"
    SERVE = "serve"
    RETURN = "return"
    APPROACH = "approach"
    DEFENSIVE = "defensive"

@dataclass
class StrokeEvent:
    stroke_type: str
    confidence: float
    start_time: float
    end_time: float
    contact_time: float
    court_zone: CourtZone
    context: StrokeContext
    ball_trajectory: List[Tuple[float, float]]
    racket_trajectory: List[Tuple[float, float]]
    technique_analysis: Dict[str, str]

class ProfessionalTennisAnalyzer:
    """Professional-grade tennis analysis mimicking ATP TennisViz approach"""
    
    def __init__(self):
        # Initialize MediaPipe for pose detection
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,  # Higher complexity for better accuracy
            enable_segmentation=False,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
        # Court detection and calibration
        self.court_detector = CourtDetector()
        self.court_calibrated = False
        
        # Tracking systems
        self.player_tracker = PlayerTracker()
        self.ball_tracker = BallTracker()
        self.stroke_analyzer = TemporalStrokeAnalyzer()
        
        # Analysis parameters
        self.stroke_window = 90  # 3 seconds at 30fps
        self.confidence_threshold = 0.6
        
    def process_video(self, video_path: str) -> Dict:
        """Process video with professional-grade analysis"""
        
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        logger.info(f"Starting professional tennis analysis: {total_frames} frames at {fps} FPS")
        
        # Phase 1: Court detection and calibration
        court_info = self._calibrate_court(cap)
        
        # Phase 2: Multi-pass analysis
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to beginning
        
        frame_data = []
        frame_id = 0
        
        # First pass: Extract all frame data
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            timestamp = frame_id / fps
            
            # Detect pose landmarks
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pose_results = self.pose.process(rgb_frame)
            
            # Track player and ball
            player_data = self.player_tracker.update(frame, pose_results, court_info)
            ball_data = self.ball_tracker.update(frame, court_info)
            
            frame_info = {
                'frame_id': frame_id,
                'timestamp': timestamp,
                'player': player_data,
                'ball': ball_data,
                'court_zone': self._determine_court_zone(player_data, court_info)
            }
            
            frame_data.append(frame_info)
            frame_id += 1
            
            if frame_id % 60 == 0:
                progress = (frame_id / total_frames) * 100
                logger.info(f"Frame extraction: {progress:.1f}%")
        
        cap.release()
        
        # Phase 3: Temporal stroke analysis
        strokes = self.stroke_analyzer.analyze_temporal_patterns(frame_data, fps)
        
        # Phase 4: Context-aware classification
        final_strokes = self._classify_with_context(strokes, frame_data)
        
        return {
            'timeline': final_strokes,
            'court_info': court_info,
            'video_info': {'fps': fps, 'total_frames': total_frames},
            'summary': self._generate_professional_summary(final_strokes)
        }
    
    def _calibrate_court(self, cap) -> Dict:
        """Detect and calibrate tennis court for spatial analysis"""
        
        logger.info("Calibrating tennis court...")
        
        # Sample frames for court detection
        sample_frames = []
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        for i in range(0, total_frames, total_frames // 10):  # Sample 10 frames
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                sample_frames.append(frame)
        
        # Detect court lines and boundaries
        court_info = self.court_detector.detect_court(sample_frames)
        
        if court_info['calibrated']:
            logger.info("Court calibration successful")
        else:
            logger.warning("Court calibration failed, using default parameters")
        
        return court_info
    
    def _determine_court_zone(self, player_data: Dict, court_info: Dict) -> CourtZone:
        """Determine which zone of the court the player is in"""
        
        if not player_data or not court_info.get('calibrated'):
            return CourtZone.UNKNOWN
        
        player_pos = player_data.get('position')
        if not player_pos:
            return CourtZone.UNKNOWN
        
        # Use court boundaries to determine zone
        court_zones = court_info.get('zones', {})
        
        x, y = player_pos
        
        # Simple zone classification based on court geometry
        if y > court_zones.get('baseline_y', 0.7):
            return CourtZone.BASELINE
        elif y > court_zones.get('service_y', 0.5):
            return CourtZone.MID_COURT
        elif y > court_zones.get('net_y', 0.3):
            return CourtZone.SERVICE_BOX
        else:
            return CourtZone.NET
    
    def _classify_with_context(self, strokes: List[Dict], frame_data: List[Dict]) -> List[Dict]:
        """Apply context-aware classification like professional systems"""
        
        enhanced_strokes = []
        
        for stroke in strokes:
            # Get context from surrounding frames
            start_frame = int(stroke['start_time'] * 30)  # Assuming 30fps
            end_frame = int(stroke['end_time'] * 30)
            
            context_frames = frame_data[max(0, start_frame-15):min(len(frame_data), end_frame+15)]
            
            # Analyze context
            context = self._analyze_stroke_context(context_frames, stroke)
            
            # Refine classification based on context
            refined_stroke = self._refine_stroke_classification(stroke, context)
            
            enhanced_strokes.append(refined_stroke)
        
        return enhanced_strokes
    
    def _analyze_stroke_context(self, frames: List[Dict], stroke: Dict) -> Dict:
        """Analyze the context around a stroke"""
        
        context = {
            'court_zones': [],
            'ball_trajectory': [],
            'player_movement': [],
            'stroke_context': StrokeContext.RALLY
        }
        
        for frame in frames:
            if frame.get('court_zone'):
                context['court_zones'].append(frame['court_zone'])
            
            if frame.get('ball') and frame['ball'].get('position'):
                context['ball_trajectory'].append(frame['ball']['position'])
            
            if frame.get('player') and frame['player'].get('position'):
                context['player_movement'].append(frame['player']['position'])
        
        # Determine stroke context
        if len(context['court_zones']) > 0:
            primary_zone = max(set(context['court_zones']), key=context['court_zones'].count)
            
            if primary_zone == CourtZone.BASELINE:
                context['stroke_context'] = StrokeContext.RALLY
            elif primary_zone == CourtZone.SERVICE_BOX:
                context['stroke_context'] = StrokeContext.SERVE
            elif primary_zone == CourtZone.NET:
                context['stroke_context'] = StrokeContext.APPROACH
        
        return context
    
    def _refine_stroke_classification(self, stroke: Dict, context: Dict) -> Dict:
        """Refine stroke classification using professional context analysis"""
        
        original_type = stroke['stroke_type']
        confidence = stroke['confidence']
        
        # Context-based refinement
        stroke_context = context['stroke_context']
        ball_trajectory = context['ball_trajectory']
        
        # Professional classification rules
        if stroke_context == StrokeContext.SERVE:
            if original_type in ['forehand', 'backhand']:
                stroke['stroke_type'] = 'serve'
                stroke['confidence'] = min(0.9, confidence + 0.2)
                stroke['technique'] = "First serve" if confidence > 0.7 else "Second serve"
        
        elif stroke_context == StrokeContext.RALLY:
            # Analyze ball trajectory for shot direction
            if len(ball_trajectory) >= 2:
                ball_direction = self._analyze_ball_direction(ball_trajectory)
                
                if original_type == 'forehand':
                    if ball_direction == 'cross_court':
                        stroke['technique'] = "Cross-court forehand"
                    elif ball_direction == 'down_line':
                        stroke['technique'] = "Down-the-line forehand"
                    else:
                        stroke['technique'] = "Forehand groundstroke"
                
                elif original_type == 'backhand':
                    if ball_direction == 'cross_court':
                        stroke['technique'] = "Cross-court backhand"
                    elif ball_direction == 'down_line':
                        stroke['technique'] = "Down-the-line backhand"
                    else:
                        stroke['technique'] = "Backhand groundstroke"
        
        elif stroke_context == StrokeContext.APPROACH:
            if original_type in ['forehand', 'backhand']:
                stroke['technique'] = f"Approach {original_type}"
        
        # Add professional metadata
        stroke['court_context'] = stroke_context.value
        stroke['analysis_method'] = 'Professional Context Analysis'
        
        return stroke
    
    def _analyze_ball_direction(self, trajectory: List[Tuple[float, float]]) -> str:
        """Analyze ball trajectory to determine shot direction"""
        
        if len(trajectory) < 3:
            return 'unknown'
        
        start_x = trajectory[0][0]
        end_x = trajectory[-1][0]
        
        # Simple direction analysis
        if abs(end_x - start_x) < 0.1:  # Relatively straight
            return 'down_line'
        elif (end_x > start_x and start_x < 0.5) or (end_x < start_x and start_x > 0.5):
            return 'cross_court'
        else:
            return 'down_line'
    
    def _generate_professional_summary(self, strokes: List[Dict]) -> Dict:
        """Generate professional-grade analysis summary"""
        
        if not strokes:
            return {'total_strokes': 0}
        
        summary = {
            'total_strokes': len(strokes),
            'stroke_breakdown': {},
            'court_coverage': {},
            'technique_analysis': {},
            'avg_confidence': sum(s['confidence'] for s in strokes) / len(strokes)
        }
        
        # Stroke type breakdown
        for stroke in strokes:
            stroke_type = stroke['stroke_type']
            summary['stroke_breakdown'][stroke_type] = summary['stroke_breakdown'].get(stroke_type, 0) + 1
        
        # Court coverage analysis
        for stroke in strokes:
            context = stroke.get('court_context', 'unknown')
            summary['court_coverage'][context] = summary['court_coverage'].get(context, 0) + 1
        
        # Technique analysis
        techniques = [s.get('technique', 'Unknown') for s in strokes]
        for tech in techniques:
            summary['technique_analysis'][tech] = summary['technique_analysis'].get(tech, 0) + 1
        
        return summary

class CourtDetector:
    """Detects and calibrates tennis court boundaries"""
    
    def detect_court(self, frames: List[np.ndarray]) -> Dict:
        """Detect court lines and boundaries from sample frames"""
        
        # Simplified court detection - in reality this would be much more complex
        court_info = {
            'calibrated': False,
            'zones': {
                'baseline_y': 0.75,
                'service_y': 0.55,
                'net_y': 0.45,
                'court_width': 1.0
            }
        }
        
        if frames:
            # Basic court detection using line detection
            for frame in frames:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 50, 150)
                lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)
                
                if lines is not None and len(lines) > 5:
                    court_info['calibrated'] = True
                    break
        
        return court_info

class PlayerTracker:
    """Tracks player position and movement"""
    
    def update(self, frame: np.ndarray, pose_results, court_info: Dict) -> Dict:
        """Update player tracking"""
        
        player_data = {'position': None, 'pose_landmarks': None}
        
        if pose_results.pose_landmarks:
            landmarks = pose_results.pose_landmarks.landmark
            
            # Calculate center of mass
            valid_landmarks = [lm for lm in landmarks if lm.visibility > 0.5]
            if valid_landmarks:
                avg_x = sum(lm.x for lm in valid_landmarks) / len(valid_landmarks)
                avg_y = sum(lm.y for lm in valid_landmarks) / len(valid_landmarks)
                
                player_data['position'] = (avg_x, avg_y)
                player_data['pose_landmarks'] = landmarks
        
        return player_data

class BallTracker:
    """Tracks tennis ball position and trajectory"""
    
    def __init__(self):
        self.ball_history = deque(maxlen=30)
    
    def update(self, frame: np.ndarray, court_info: Dict) -> Dict:
        """Update ball tracking using color and motion detection"""
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Tennis ball color range (yellow-green)
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([40, 255, 255])
        
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        ball_data = {'position': None, 'confidence': 0.0}
        
        if contours:
            # Find the most circular contour of appropriate size
            best_contour = None
            best_score = 0
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if 50 < area < 2000:  # Reasonable ball size
                    perimeter = cv2.arcLength(contour, True)
                    if perimeter > 0:
                        circularity = 4 * np.pi * area / (perimeter * perimeter)
                        if circularity > best_score:
                            best_score = circularity
                            best_contour = contour
            
            if best_contour is not None and best_score > 0.3:
                M = cv2.moments(best_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    
                    # Normalize coordinates
                    h, w = frame.shape[:2]
                    ball_data['position'] = (cx / w, cy / h)
                    ball_data['confidence'] = best_score
        
        self.ball_history.append(ball_data)
        return ball_data

class TemporalStrokeAnalyzer:
    """Analyzes stroke patterns over time like professional systems"""
    
    def analyze_temporal_patterns(self, frame_data: List[Dict], fps: float) -> List[Dict]:
        """Analyze temporal patterns to detect strokes"""
        
        strokes = []
        
        # Extract player movement data
        player_positions = []
        for frame in frame_data:
            if frame.get('player') and frame['player'].get('position'):
                player_positions.append({
                    'timestamp': frame['timestamp'],
                    'position': frame['player']['position'],
                    'frame_id': frame['frame_id']
                })
        
        if len(player_positions) < 30:  # Need minimum data
            return strokes
        
        # Calculate velocities and accelerations
        velocities = []
        for i in range(1, len(player_positions)):
            dt = player_positions[i]['timestamp'] - player_positions[i-1]['timestamp']
            if dt > 0:
                pos1 = player_positions[i-1]['position']
                pos2 = player_positions[i]['position']
                
                vx = (pos2[0] - pos1[0]) / dt
                vy = (pos2[1] - pos1[1]) / dt
                velocity = math.sqrt(vx*vx + vy*vy)
                
                velocities.append({
                    'timestamp': player_positions[i]['timestamp'],
                    'velocity': velocity,
                    'vx': vx,
                    'vy': vy
                })
        
        # Detect stroke events using velocity peaks
        stroke_events = self._detect_velocity_peaks(velocities)
        
        # Convert to stroke format
        for event in stroke_events:
            stroke = {
                'stroke_type': self._classify_from_velocity(event),
                'confidence': event['confidence'],
                'start_time': event['start_time'],
                'end_time': event['end_time'],
                'contact_time': event['peak_time'],
                'technique': 'Temporal analysis stroke'
            }
            strokes.append(stroke)
        
        return strokes
    
    def _detect_velocity_peaks(self, velocities: List[Dict]) -> List[Dict]:
        """Detect velocity peaks that indicate strokes"""
        
        events = []
        
        if len(velocities) < 10:
            return events
        
        # Smooth velocities
        window_size = 5
        smoothed = []
        for i in range(len(velocities)):
            start_idx = max(0, i - window_size // 2)
            end_idx = min(len(velocities), i + window_size // 2 + 1)
            avg_vel = sum(v['velocity'] for v in velocities[start_idx:end_idx]) / (end_idx - start_idx)
            smoothed.append(avg_vel)
        
        # Find peaks
        for i in range(2, len(smoothed) - 2):
            if (smoothed[i] > smoothed[i-1] and smoothed[i] > smoothed[i+1] and 
                smoothed[i] > smoothed[i-2] and smoothed[i] > smoothed[i+2]):
                
                if smoothed[i] > 0.1:  # Minimum velocity threshold
                    
                    # Find stroke boundaries
                    start_idx = i
                    while start_idx > 0 and smoothed[start_idx] > smoothed[i] * 0.3:
                        start_idx -= 1
                    
                    end_idx = i
                    while end_idx < len(smoothed) - 1 and smoothed[end_idx] > smoothed[i] * 0.3:
                        end_idx += 1
                    
                    event = {
                        'peak_time': velocities[i]['timestamp'],
                        'start_time': velocities[start_idx]['timestamp'],
                        'end_time': velocities[end_idx]['timestamp'],
                        'peak_velocity': smoothed[i],
                        'velocity_data': velocities[start_idx:end_idx+1],
                        'confidence': min(0.9, smoothed[i] * 2)  # Scale confidence
                    }
                    
                    events.append(event)
        
        return events
    
    def _classify_from_velocity(self, event: Dict) -> str:
        """Classify stroke type from velocity patterns"""
        
        peak_vel = event['peak_velocity']
        velocity_data = event['velocity_data']
        
        if not velocity_data:
            return 'unknown'
        
        # Analyze velocity direction
        avg_vx = sum(v['vx'] for v in velocity_data) / len(velocity_data)
        avg_vy = sum(v['vy'] for v in velocity_data) / len(velocity_data)
        
        # Classification based on velocity patterns
        if peak_vel > 0.3 and abs(avg_vy) > abs(avg_vx):
            return 'serve'
        elif peak_vel > 0.15:
            if avg_vx > 0.05:
                return 'forehand'
            elif avg_vx < -0.05:
                return 'backhand'
            else:
                return 'forehand'  # Default for ambiguous cases
        else:
            return 'volley'

def analyze_video_professional(video_path: str) -> Dict:
    """Professional-grade tennis video analysis"""
    analyzer = ProfessionalTennisAnalyzer()
    return analyzer.process_video(video_path)
