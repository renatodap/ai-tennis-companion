"""
Technique Analysis Module
Focuses on form, posture, and swing mechanics analysis
"""
import json
import logging
import numpy as np
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class TechniqueAnalyzer:
    """Analyzes tennis technique from pose keypoints"""
    
    def __init__(self):
        # MediaPipe pose landmark indices
        self.POSE_LANDMARKS = {
            'left_shoulder': 11,
            'right_shoulder': 12,
            'left_elbow': 13,
            'right_elbow': 14,
            'left_wrist': 15,
            'right_wrist': 16,
            'left_hip': 23,
            'right_hip': 24,
            'left_knee': 25,
            'right_knee': 26,
            'left_ankle': 27,
            'right_ankle': 28
        }
    
    def analyze(self, keypoints_data: Dict, video_config: Dict, fps: float) -> Dict[str, Any]:
        """
        Main technique analysis function
        
        Args:
            keypoints_data: Extracted pose keypoints
            video_config: Configuration (type, view, mode)
            fps: Video frame rate
            
        Returns:
            Analysis results with technique insights
        """
        logger.info("Starting technique analysis...")
        
        # Extract valid frames with keypoints
        valid_frames = self._extract_valid_frames(keypoints_data)
        
        if not valid_frames:
            return self._empty_analysis()
        
        # Detect strokes with improved algorithm
        strokes = self._detect_strokes_advanced(valid_frames, fps)
        
        # Analyze technique for each stroke
        technique_analysis = []
        for stroke in strokes:
            analysis = self._analyze_stroke_technique(stroke, valid_frames, video_config)
            technique_analysis.append(analysis)
        
        # Generate summary insights
        summary = self._generate_technique_summary(technique_analysis, video_config)
        
        return {
            'strokes': technique_analysis,
            'summary': summary,
            'total_strokes': len(technique_analysis),
            'analysis_type': 'technique',
            'camera_view': video_config.get('view', 'unknown')
        }
    
    def _extract_valid_frames(self, keypoints_data: Dict) -> List[Dict]:
        """Extract frames with valid pose data"""
        valid_frames = []
        
        for frame_name, landmarks in keypoints_data.items():
            if landmarks and len(landmarks) >= 33:  # MediaPipe has 33 landmarks
                frame_num = int(frame_name.split('_')[1].split('.')[0])
                valid_frames.append({
                    'frame': frame_name,
                    'frame_num': frame_num,
                    'landmarks': landmarks
                })
        
        # Sort by frame number
        valid_frames.sort(key=lambda x: x['frame_num'])
        return valid_frames
    
    def _detect_strokes_advanced(self, frames: List[Dict], fps: float) -> List[Dict]:
        """Advanced stroke detection using motion analysis"""
        if len(frames) < 5:
            return []
        
        strokes = []
        
        # Calculate wrist velocities and accelerations
        wrist_motion = self._calculate_wrist_motion(frames)
        
        # Detect stroke events based on motion patterns
        stroke_events = self._find_stroke_events(wrist_motion, fps)
        
        # Classify stroke types
        for event in stroke_events:
            stroke_type = self._classify_stroke_type(frames, event)
            
            stroke = {
                'start_frame': event['start_frame'],
                'end_frame': event['end_frame'],
                'peak_frame': event['peak_frame'],
                'start_sec': event['start_frame'] / fps,
                'end_sec': event['end_frame'] / fps,
                'peak_sec': event['peak_frame'] / fps,
                'stroke': stroke_type,
                'confidence': event['confidence']
            }
            strokes.append(stroke)
        
        return strokes
    
    def _calculate_wrist_motion(self, frames: List[Dict]) -> List[Dict]:
        """Calculate wrist motion metrics"""
        motion_data = []
        
        for i, frame in enumerate(frames):
            landmarks = frame['landmarks']
            
            # Get wrist positions
            left_wrist = landmarks[self.POSE_LANDMARKS['left_wrist']]
            right_wrist = landmarks[self.POSE_LANDMARKS['right_wrist']]
            
            # Calculate combined wrist motion (dominant hand detection could be added)
            avg_wrist_x = (left_wrist['x'] + right_wrist['x']) / 2
            avg_wrist_y = (left_wrist['y'] + right_wrist['y']) / 2
            
            motion_frame = {
                'frame_num': frame['frame_num'],
                'wrist_x': avg_wrist_x,
                'wrist_y': avg_wrist_y,
                'left_wrist': left_wrist,
                'right_wrist': right_wrist
            }
            
            # Calculate velocity if we have previous frame
            if i > 0:
                prev = motion_data[i-1]
                dt = 1.0  # frame time difference
                motion_frame['velocity_x'] = (avg_wrist_x - prev['wrist_x']) / dt
                motion_frame['velocity_y'] = (avg_wrist_y - prev['wrist_y']) / dt
                motion_frame['speed'] = np.sqrt(motion_frame['velocity_x']**2 + motion_frame['velocity_y']**2)
            else:
                motion_frame['velocity_x'] = 0
                motion_frame['velocity_y'] = 0
                motion_frame['speed'] = 0
            
            # Calculate acceleration if we have enough frames
            if i > 1:
                prev = motion_data[i-1]
                motion_frame['acceleration'] = (motion_frame['speed'] - prev['speed']) / dt
            else:
                motion_frame['acceleration'] = 0
            
            motion_data.append(motion_frame)
        
        return motion_data
    
    def _find_stroke_events(self, motion_data: List[Dict], fps: float) -> List[Dict]:
        """Find stroke events based on motion patterns"""
        events = []
        
        if len(motion_data) < 10:
            return events
        
        # Find peaks in wrist speed (potential stroke moments)
        speeds = [frame['speed'] for frame in motion_data]
        
        # Simple peak detection
        for i in range(2, len(speeds) - 2):
            if (speeds[i] > speeds[i-1] and speeds[i] > speeds[i+1] and 
                speeds[i] > speeds[i-2] and speeds[i] > speeds[i+2]):
                
                # Check if this is a significant peak
                if speeds[i] > 0.05:  # Threshold for minimum stroke speed
                    
                    # Find stroke boundaries
                    start_idx = max(0, i - 10)  # Look back up to 10 frames
                    end_idx = min(len(speeds), i + 10)  # Look forward up to 10 frames
                    
                    # Refine boundaries based on speed threshold
                    speed_threshold = speeds[i] * 0.3
                    
                    for j in range(i, start_idx, -1):
                        if speeds[j] < speed_threshold:
                            start_idx = j
                            break
                    
                    for j in range(i, end_idx):
                        if speeds[j] < speed_threshold:
                            end_idx = j
                            break
                    
                    event = {
                        'start_frame': motion_data[start_idx]['frame_num'],
                        'end_frame': motion_data[end_idx]['frame_num'],
                        'peak_frame': motion_data[i]['frame_num'],
                        'peak_speed': speeds[i],
                        'confidence': min(1.0, speeds[i] / 0.2)  # Normalize confidence
                    }
                    events.append(event)
        
        # Remove overlapping events (keep the one with higher peak speed)
        events = self._remove_overlapping_events(events)
        
        return events
    
    def _remove_overlapping_events(self, events: List[Dict]) -> List[Dict]:
        """Remove overlapping stroke events"""
        if not events:
            return events
        
        # Sort by peak speed (descending)
        events.sort(key=lambda x: x['peak_speed'], reverse=True)
        
        filtered_events = []
        for event in events:
            # Check if this event overlaps with any already accepted event
            overlaps = False
            for accepted in filtered_events:
                if (event['start_frame'] <= accepted['end_frame'] and 
                    event['end_frame'] >= accepted['start_frame']):
                    overlaps = True
                    break
            
            if not overlaps:
                filtered_events.append(event)
        
        # Sort by time
        filtered_events.sort(key=lambda x: x['start_frame'])
        return filtered_events
    
    def _classify_stroke_type(self, frames: List[Dict], event: Dict) -> str:
        """Classify the type of stroke based on pose analysis"""
        # Find the frame closest to the peak
        peak_frame_num = event['peak_frame']
        peak_frame = None
        
        for frame in frames:
            if frame['frame_num'] == peak_frame_num:
                peak_frame = frame
                break
        
        if not peak_frame:
            return 'unknown'
        
        landmarks = peak_frame['landmarks']
        
        try:
            # Get key landmarks
            left_wrist = landmarks[self.POSE_LANDMARKS['left_wrist']]
            right_wrist = landmarks[self.POSE_LANDMARKS['right_wrist']]
            left_shoulder = landmarks[self.POSE_LANDMARKS['left_shoulder']]
            right_shoulder = landmarks[self.POSE_LANDMARKS['right_shoulder']]
            left_elbow = landmarks[self.POSE_LANDMARKS['left_elbow']]
            right_elbow = landmarks[self.POSE_LANDMARKS['right_elbow']]
            
            # Calculate metrics for classification
            avg_shoulder_y = (left_shoulder['y'] + right_shoulder['y']) / 2
            avg_wrist_y = (left_wrist['y'] + right_wrist['y']) / 2
            wrist_separation = abs(left_wrist['x'] - right_wrist['x'])
            
            # Improved classification logic
            wrist_above_shoulder = avg_wrist_y < avg_shoulder_y - 0.08
            hands_far_apart = wrist_separation > 0.2
            
            # Check for serve (wrists well above shoulders)
            if wrist_above_shoulder:
                return 'serve'
            
            # Check for two-handed vs one-handed strokes
            elif hands_far_apart:
                # One-handed stroke - determine forehand vs backhand
                # This is simplified - in reality you'd need to determine dominant hand
                if right_wrist['x'] > left_wrist['x']:
                    return 'forehand'
                else:
                    return 'backhand'
            else:
                # Two-handed stroke or close-together hands
                return 'backhand'  # Often two-handed backhands
                
        except (KeyError, IndexError, TypeError):
            return 'unknown'
    
    def _analyze_stroke_technique(self, stroke: Dict, frames: List[Dict], config: Dict) -> Dict[str, Any]:
        """Analyze technique for a specific stroke"""
        
        # Find frames for this stroke
        stroke_frames = [f for f in frames 
                        if stroke['start_frame'] <= f['frame_num'] <= stroke['end_frame']]
        
        if not stroke_frames:
            return self._empty_stroke_analysis(stroke)
        
        # Get peak frame for detailed analysis
        peak_frame = next((f for f in stroke_frames if f['frame_num'] == stroke['peak_frame']), 
                         stroke_frames[len(stroke_frames)//2])
        
        # Analyze based on camera view
        if config.get('view') == 'side':
            technique_metrics = self._analyze_side_view_technique(peak_frame, stroke)
        else:  # back view
            technique_metrics = self._analyze_back_view_technique(peak_frame, stroke)
        
        return {
            'stroke_type': stroke['stroke'],
            'start_sec': stroke['start_sec'],
            'end_sec': stroke['end_sec'],
            'peak_sec': stroke['peak_sec'],
            'confidence': stroke['confidence'],
            'technique': technique_metrics,
            'feedback': self._generate_stroke_feedback(technique_metrics, stroke['stroke'])
        }
    
    def _analyze_side_view_technique(self, frame: Dict, stroke: Dict) -> Dict[str, Any]:
        """Analyze technique from side view"""
        landmarks = frame['landmarks']
        
        try:
            # Key landmarks for side view analysis
            left_shoulder = landmarks[self.POSE_LANDMARKS['left_shoulder']]
            right_shoulder = landmarks[self.POSE_LANDMARKS['right_shoulder']]
            left_elbow = landmarks[self.POSE_LANDMARKS['left_elbow']]
            right_elbow = landmarks[self.POSE_LANDMARKS['right_elbow']]
            left_wrist = landmarks[self.POSE_LANDMARKS['left_wrist']]
            right_wrist = landmarks[self.POSE_LANDMARKS['right_wrist']]
            left_hip = landmarks[self.POSE_LANDMARKS['left_hip']]
            right_hip = landmarks[self.POSE_LANDMARKS['right_hip']]
            
            # Calculate angles and positions
            # Simplified analysis - in reality you'd use more sophisticated biomechanics
            
            # Shoulder rotation (approximate)
            shoulder_angle = abs(left_shoulder['y'] - right_shoulder['y']) * 100
            
            # Elbow position relative to shoulder
            avg_shoulder_y = (left_shoulder['y'] + right_shoulder['y']) / 2
            avg_elbow_y = (left_elbow['y'] + right_elbow['y']) / 2
            elbow_height = avg_shoulder_y - avg_elbow_y
            
            # Hip rotation
            hip_rotation = abs(left_hip['y'] - right_hip['y']) * 100
            
            return {
                'shoulder_rotation': round(shoulder_angle, 2),
                'elbow_height': round(elbow_height, 3),
                'hip_rotation': round(hip_rotation, 2),
                'posture_score': self._calculate_posture_score(shoulder_angle, elbow_height),
                'view_type': 'side'
            }
            
        except (KeyError, IndexError, TypeError):
            return {'error': 'Could not analyze technique', 'view_type': 'side'}
    
    def _analyze_back_view_technique(self, frame: Dict, stroke: Dict) -> Dict[str, Any]:
        """Analyze technique from back view"""
        landmarks = frame['landmarks']
        
        try:
            # Key landmarks for back view analysis
            left_wrist = landmarks[self.POSE_LANDMARKS['left_wrist']]
            right_wrist = landmarks[self.POSE_LANDMARKS['right_wrist']]
            left_shoulder = landmarks[self.POSE_LANDMARKS['left_shoulder']]
            right_shoulder = landmarks[self.POSE_LANDMARKS['right_shoulder']]
            
            # Calculate metrics
            wrist_separation = abs(left_wrist['x'] - right_wrist['x'])
            shoulder_width = abs(left_shoulder['x'] - right_shoulder['x'])
            
            # Stroke width relative to shoulder width
            relative_width = wrist_separation / shoulder_width if shoulder_width > 0 else 0
            
            # Balance (how centered the stroke is)
            center_x = (left_shoulder['x'] + right_shoulder['x']) / 2
            stroke_center = (left_wrist['x'] + right_wrist['x']) / 2
            balance_offset = abs(stroke_center - center_x)
            
            return {
                'stroke_width': round(relative_width, 2),
                'balance_offset': round(balance_offset, 3),
                'wrist_separation': round(wrist_separation, 3),
                'balance_score': self._calculate_balance_score(balance_offset),
                'view_type': 'back'
            }
            
        except (KeyError, IndexError, TypeError):
            return {'error': 'Could not analyze technique', 'view_type': 'back'}
    
    def _calculate_posture_score(self, shoulder_angle: float, elbow_height: float) -> int:
        """Calculate a posture score from 1-10"""
        # Simplified scoring - ideal values would be sport-specific
        score = 10
        
        # Penalize extreme shoulder angles
        if shoulder_angle > 15:
            score -= 2
        
        # Penalize poor elbow position
        if elbow_height < -0.1 or elbow_height > 0.1:
            score -= 2
        
        return max(1, score)
    
    def _calculate_balance_score(self, balance_offset: float) -> int:
        """Calculate a balance score from 1-10"""
        score = 10
        
        # Penalize poor balance
        if balance_offset > 0.1:
            score -= 3
        elif balance_offset > 0.05:
            score -= 1
        
        return max(1, score)
    
    def _generate_stroke_feedback(self, technique: Dict, stroke_type: str) -> List[str]:
        """Generate feedback based on technique analysis"""
        feedback = []
        
        if 'error' in technique:
            feedback.append("Could not analyze technique for this stroke")
            return feedback
        
        if technique.get('view_type') == 'side':
            # Side view feedback
            posture_score = technique.get('posture_score', 5)
            if posture_score < 6:
                feedback.append("Work on maintaining better posture during the stroke")
            
            elbow_height = technique.get('elbow_height', 0)
            if elbow_height < -0.05:
                feedback.append("Try to keep your elbow higher during the stroke")
            
        elif technique.get('view_type') == 'back':
            # Back view feedback
            balance_score = technique.get('balance_score', 5)
            if balance_score < 7:
                feedback.append("Focus on staying balanced and centered")
            
            stroke_width = technique.get('stroke_width', 1)
            if stroke_type == 'forehand' and stroke_width > 1.5:
                feedback.append("Try to keep your forehand more compact")
        
        if not feedback:
            feedback.append("Good technique! Keep practicing to maintain consistency")
        
        return feedback
    
    def _generate_technique_summary(self, analyses: List[Dict], config: Dict) -> Dict[str, Any]:
        """Generate overall technique summary"""
        if not analyses:
            return {'message': 'No strokes detected for technique analysis'}
        
        # Count stroke types
        stroke_counts = {}
        total_feedback = []
        
        for analysis in analyses:
            stroke_type = analysis['stroke_type']
            stroke_counts[stroke_type] = stroke_counts.get(stroke_type, 0) + 1
            total_feedback.extend(analysis.get('feedback', []))
        
        # Find most common feedback
        feedback_counts = {}
        for feedback in total_feedback:
            feedback_counts[feedback] = feedback_counts.get(feedback, 0) + 1
        
        top_feedback = sorted(feedback_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'total_strokes': len(analyses),
            'stroke_breakdown': stroke_counts,
            'top_feedback': [f[0] for f in top_feedback],
            'camera_view': config.get('view', 'unknown'),
            'analysis_focus': 'technique'
        }
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis result"""
        return {
            'strokes': [],
            'summary': {'message': 'No valid pose data found for analysis'},
            'total_strokes': 0,
            'analysis_type': 'technique'
        }
    
    def _empty_stroke_analysis(self, stroke: Dict) -> Dict[str, Any]:
        """Return empty stroke analysis"""
        return {
            'stroke_type': stroke.get('stroke', 'unknown'),
            'start_sec': stroke.get('start_sec', 0),
            'end_sec': stroke.get('end_sec', 0),
            'confidence': stroke.get('confidence', 0),
            'technique': {'error': 'No data available'},
            'feedback': ['Could not analyze this stroke']
        }
