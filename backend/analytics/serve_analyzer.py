"""
🎾 SERVE ANALYSIS MODULE
Phase 3: Serve placement, toss consistency, timing analysis
"""

import numpy as np
import pandas as pd
import cv2
import matplotlib.pyplot as plt
from scipy import signal
from typing import Dict, List, Tuple, Optional
import logging
import asyncio
from dataclasses import dataclass
import json
import math

logger = logging.getLogger(__name__)

@dataclass
class ServeEvent:
    """Detailed serve event analysis"""
    serve_id: str
    start_time: float
    contact_time: float
    end_time: float
    toss_height: float
    toss_timing: float
    serve_speed: float
    placement_zone: str  # T, Body, Wide
    serve_type: str  # First, Second
    outcome: str  # Ace, Service Winner, In Play, Fault, Double Fault
    ball_trajectory: List[Tuple[float, float]]
    technique_score: float

class ServeAnalyzer:
    """🎾 Advanced serve analysis system"""
    
    def __init__(self):
        self.service_zones = {
            'T': {'x_range': (0.45, 0.55), 'y_range': (0.0, 0.3)},
            'Body': {'x_range': (0.35, 0.65), 'y_range': (0.0, 0.3)},
            'Wide': {'x_range': (0.1, 0.4), 'y_range': (0.0, 0.3)}
        }
        
        self.toss_analysis_window = 1.5  # seconds before contact
        self.serve_speed_threshold = 0.3  # minimum speed for serve detection
    
    async def analyze_serves(self, stroke_events: List[Dict]) -> Dict:
        """Comprehensive serve analysis"""
        logger.info("🎾 Analyzing serve performance...")
        
        # Filter serve events
        serves = [s for s in stroke_events if s.get('stroke_type') == 'serve']
        
        if not serves:
            return {'serve_analysis': 'No serves detected'}
        
        # Analyze serve placement
        placement_analysis = await self._analyze_serve_placement(serves)
        
        # Analyze toss consistency
        toss_analysis = await self._analyze_toss_consistency(serves)
        
        # Analyze serve timing
        timing_analysis = await self._analyze_serve_timing(serves)
        
        # Generate serve insights
        serve_insights = self._generate_serve_insights(serves, placement_analysis, toss_analysis)
        
        return {
            'total_serves': len(serves),
            'placement_analysis': placement_analysis,
            'toss_analysis': toss_analysis,
            'timing_analysis': timing_analysis,
            'serve_insights': serve_insights,
            'serve_statistics': self._calculate_serve_statistics(serves)
        }
    
    async def _analyze_serve_placement(self, serves: List[Dict]) -> Dict:
        """Analyze serve placement patterns"""
        logger.info("🎯 Analyzing serve placement...")
        
        placement_data = {
            'T': 0,
            'Body': 0,
            'Wide': 0,
            'Unknown': 0
        }
        
        serve_locations = []
        
        for serve in serves:
            # Extract serve placement (simplified - would use ball tracking in production)
            placement = self._estimate_serve_placement(serve)
            placement_data[placement] += 1
            
            serve_locations.append({
                'serve_id': serve.get('stroke_id', ''),
                'placement': placement,
                'speed': serve.get('swing_speed', 0),
                'outcome': serve.get('outcome', 'unknown')
            })
        
        total_serves = len(serves)
        placement_percentages = {
            zone: (count / total_serves * 100) if total_serves > 0 else 0
            for zone, count in placement_data.items()
        }
        
        return {
            'placement_distribution': placement_data,
            'placement_percentages': placement_percentages,
            'serve_locations': serve_locations,
            'placement_consistency': self._calculate_placement_consistency(serve_locations)
        }
    
    def _estimate_serve_placement(self, serve: Dict) -> str:
        """Estimate serve placement zone"""
        # Simplified placement estimation
        # In production, this would use ball trajectory analysis
        
        swing_speed = serve.get('swing_speed', 0)
        racket_angle = serve.get('racket_angle', 0)
        
        # Simple heuristic based on racket angle
        if abs(racket_angle) < 0.3:
            return 'T'
        elif racket_angle > 0.3:
            return 'Wide'
        elif racket_angle < -0.3:
            return 'Body'
        else:
            return 'Unknown'
    
    def _calculate_placement_consistency(self, serve_locations: List[Dict]) -> Dict:
        """Calculate serve placement consistency metrics"""
        if not serve_locations:
            return {}
        
        # Group by placement zone
        placement_groups = {}
        for serve in serve_locations:
            zone = serve['placement']
            if zone not in placement_groups:
                placement_groups[zone] = []
            placement_groups[zone].append(serve)
        
        consistency_scores = {}
        for zone, serves in placement_groups.items():
            if len(serves) > 1:
                speeds = [s['speed'] for s in serves]
                speed_consistency = 1.0 / (1.0 + np.std(speeds)) if np.std(speeds) > 0 else 1.0
                consistency_scores[zone] = float(speed_consistency)
            else:
                consistency_scores[zone] = 1.0
        
        return {
            'zone_consistency': consistency_scores,
            'overall_consistency': float(np.mean(list(consistency_scores.values()))) if consistency_scores else 0.0
        }
    
    async def _analyze_toss_consistency(self, serves: List[Dict]) -> Dict:
        """Analyze toss height and timing consistency"""
        logger.info("🏐 Analyzing toss consistency...")
        
        toss_data = []
        
        for serve in serves:
            # Estimate toss characteristics (simplified)
            toss_height = self._estimate_toss_height(serve)
            toss_timing = self._estimate_toss_timing(serve)
            
            toss_data.append({
                'serve_id': serve.get('stroke_id', ''),
                'toss_height': toss_height,
                'toss_timing': toss_timing,
                'serve_speed': serve.get('swing_speed', 0)
            })
        
        if not toss_data:
            return {}
        
        # Calculate consistency metrics
        heights = [t['toss_height'] for t in toss_data]
        timings = [t['toss_timing'] for t in toss_data]
        
        return {
            'toss_data': toss_data,
            'height_consistency': {
                'mean': float(np.mean(heights)),
                'std': float(np.std(heights)),
                'consistency_score': float(1.0 / (1.0 + np.std(heights))) if np.std(heights) > 0 else 1.0
            },
            'timing_consistency': {
                'mean': float(np.mean(timings)),
                'std': float(np.std(timings)),
                'consistency_score': float(1.0 / (1.0 + np.std(timings))) if np.std(timings) > 0 else 1.0
            },
            'optimal_toss_height': float(np.percentile(heights, 75)),  # 75th percentile as optimal
            'toss_recommendations': self._generate_toss_recommendations(toss_data)
        }
    
    def _estimate_toss_height(self, serve: Dict) -> float:
        """Estimate toss height from serve characteristics"""
        # Simplified estimation based on swing speed and duration
        swing_speed = serve.get('swing_speed', 0)
        duration = serve.get('duration', 1.0)
        
        # Higher speed and longer duration suggest higher toss
        estimated_height = swing_speed * duration * 2.0
        return min(3.0, max(0.5, estimated_height))  # Clamp between 0.5 and 3.0
    
    def _estimate_toss_timing(self, serve: Dict) -> float:
        """Estimate toss timing (time from toss to contact)"""
        # Simplified estimation
        duration = serve.get('duration', 1.0)
        
        # Assume toss happens at 30% of serve duration
        toss_timing = duration * 0.7
        return max(0.3, min(2.0, toss_timing))  # Clamp between 0.3 and 2.0 seconds
    
    def _generate_toss_recommendations(self, toss_data: List[Dict]) -> List[str]:
        """Generate toss improvement recommendations"""
        recommendations = []
        
        if not toss_data:
            return recommendations
        
        heights = [t['toss_height'] for t in toss_data]
        timings = [t['toss_timing'] for t in toss_data]
        
        # Height consistency
        height_std = np.std(heights)
        if height_std > 0.3:
            recommendations.append(f"Work on toss height consistency (variation: {height_std:.2f})")
        
        # Timing consistency
        timing_std = np.std(timings)
        if timing_std > 0.2:
            recommendations.append(f"Improve toss timing consistency (variation: {timing_std:.2f}s)")
        
        # Optimal height
        mean_height = np.mean(heights)
        if mean_height < 1.5:
            recommendations.append("Consider increasing toss height for more power")
        elif mean_height > 2.5:
            recommendations.append("Consider lowering toss height for better control")
        
        return recommendations
    
    async def _analyze_serve_timing(self, serves: List[Dict]) -> Dict:
        """Analyze serve rhythm and timing patterns"""
        logger.info("⏱️ Analyzing serve timing...")
        
        if len(serves) < 2:
            return {}
        
        # Calculate time between serves
        serve_intervals = []
        for i in range(1, len(serves)):
            interval = serves[i]['start_time'] - serves[i-1]['end_time']
            serve_intervals.append(interval)
        
        # Analyze rhythm patterns
        rhythm_analysis = self._analyze_serve_rhythm(serve_intervals)
        
        return {
            'serve_intervals': serve_intervals,
            'rhythm_analysis': rhythm_analysis,
            'average_interval': float(np.mean(serve_intervals)),
            'rhythm_consistency': float(1.0 / (1.0 + np.std(serve_intervals))) if np.std(serve_intervals) > 0 else 1.0
        }
    
    def _analyze_serve_rhythm(self, intervals: List[float]) -> Dict:
        """Analyze serve rhythm patterns"""
        if not intervals:
            return {}
        
        # Categorize intervals
        quick_serves = sum(1 for i in intervals if i < 10)  # Less than 10 seconds
        normal_serves = sum(1 for i in intervals if 10 <= i <= 25)  # 10-25 seconds
        slow_serves = sum(1 for i in intervals if i > 25)  # More than 25 seconds
        
        total = len(intervals)
        
        return {
            'quick_serves': quick_serves,
            'normal_serves': normal_serves,
            'slow_serves': slow_serves,
            'rhythm_distribution': {
                'quick': (quick_serves / total * 100) if total > 0 else 0,
                'normal': (normal_serves / total * 100) if total > 0 else 0,
                'slow': (slow_serves / total * 100) if total > 0 else 0
            },
            'preferred_rhythm': 'quick' if quick_serves > max(normal_serves, slow_serves) else 
                               'normal' if normal_serves > slow_serves else 'slow'
        }
    
    def _generate_serve_insights(self, serves: List[Dict], placement_analysis: Dict, toss_analysis: Dict) -> List[str]:
        """Generate actionable serve insights"""
        insights = []
        
        if not serves:
            return insights
        
        # Placement insights
        placement_dist = placement_analysis.get('placement_percentages', {})
        dominant_zone = max(placement_dist.items(), key=lambda x: x[1])[0] if placement_dist else 'Unknown'
        
        if placement_dist.get(dominant_zone, 0) > 60:
            insights.append(f"Strong preference for {dominant_zone} serves ({placement_dist[dominant_zone]:.0f}%)")
        
        # Consistency insights
        placement_consistency = placement_analysis.get('placement_consistency', {}).get('overall_consistency', 0)
        if placement_consistency < 0.7:
            insights.append("Work on serve placement consistency")
        
        # Toss insights
        toss_consistency = toss_analysis.get('height_consistency', {}).get('consistency_score', 0)
        if toss_consistency < 0.8:
            insights.append("Focus on toss height consistency for better serves")
        
        # Speed analysis
        speeds = [s.get('swing_speed', 0) for s in serves]
        avg_speed = np.mean(speeds)
        speed_consistency = 1.0 / (1.0 + np.std(speeds)) if np.std(speeds) > 0 else 1.0
        
        if speed_consistency < 0.7:
            insights.append("Work on serve speed consistency")
        
        if avg_speed < 0.2:
            insights.append("Consider increasing serve power")
        
        return insights
    
    def _calculate_serve_statistics(self, serves: List[Dict]) -> Dict:
        """Calculate comprehensive serve statistics"""
        if not serves:
            return {}
        
        # Basic statistics
        total_serves = len(serves)
        speeds = [s.get('swing_speed', 0) for s in serves]
        durations = [s.get('duration', 0) for s in serves]
        
        # Outcome analysis
        outcomes = [s.get('outcome', 'unknown') for s in serves]
        outcome_counts = pd.Series(outcomes).value_counts()
        
        # First vs Second serve analysis (simplified)
        first_serves = serves[::2]  # Assume every other serve is first serve
        second_serves = serves[1::2]  # Assume every other serve is second serve
        
        return {
            'total_serves': total_serves,
            'speed_statistics': {
                'mean': float(np.mean(speeds)),
                'max': float(np.max(speeds)),
                'min': float(np.min(speeds)),
                'std': float(np.std(speeds))
            },
            'duration_statistics': {
                'mean': float(np.mean(durations)),
                'std': float(np.std(durations))
            },
            'outcome_distribution': outcome_counts.to_dict(),
            'first_serve_stats': {
                'count': len(first_serves),
                'avg_speed': float(np.mean([s.get('swing_speed', 0) for s in first_serves])) if first_serves else 0
            },
            'second_serve_stats': {
                'count': len(second_serves),
                'avg_speed': float(np.mean([s.get('swing_speed', 0) for s in second_serves])) if second_serves else 0
            }
        }


class TossAnalyzer:
    """🏐 Specialized toss analysis"""
    
    def __init__(self):
        self.toss_detection_threshold = 0.1
        self.optimal_toss_height_range = (1.8, 2.2)  # meters
    
    async def analyze_toss_mechanics(self, serve_data: List[Dict], pose_data: List[Dict]) -> Dict:
        """Detailed toss mechanics analysis"""
        logger.info("🏐 Analyzing toss mechanics...")
        
        toss_events = []
        
        for serve in serve_data:
            if serve.get('stroke_type') != 'serve':
                continue
            
            # Extract pose data for serve duration
            serve_poses = self._extract_serve_poses(serve, pose_data)
            
            if serve_poses:
                toss_analysis = self._analyze_individual_toss(serve_poses, serve)
                toss_events.append(toss_analysis)
        
        if not toss_events:
            return {}
        
        return {
            'toss_events': toss_events,
            'consistency_metrics': self._calculate_toss_consistency(toss_events),
            'technique_recommendations': self._generate_toss_recommendations(toss_events)
        }
    
    def _extract_serve_poses(self, serve: Dict, pose_data: List[Dict]) -> List[Dict]:
        """Extract pose data for serve duration"""
        start_time = serve.get('start_time', 0)
        end_time = serve.get('end_time', 0)
        
        serve_poses = []
        for pose in pose_data:
            if start_time <= pose.get('timestamp', 0) <= end_time:
                serve_poses.append(pose)
        
        return serve_poses
    
    def _analyze_individual_toss(self, pose_sequence: List[Dict], serve: Dict) -> Dict:
        """Analyze individual toss mechanics"""
        if not pose_sequence:
            return {}
        
        # Extract hand positions over time
        hand_positions = []
        for pose in pose_sequence:
            if pose.get('landmarks') is not None:
                landmarks = pose['landmarks']
                if len(landmarks) > 15:  # Left wrist index
                    hand_pos = landmarks[15]  # Left hand for toss
                    hand_positions.append({
                        'timestamp': pose['timestamp'],
                        'x': hand_pos[0],
                        'y': hand_pos[1],
                        'z': hand_pos[2] if len(hand_pos) > 2 else 0
                    })
        
        if len(hand_positions) < 3:
            return {}
        
        # Find toss peak
        toss_peak = self._find_toss_peak(hand_positions)
        
        # Calculate toss characteristics
        toss_height = self._calculate_toss_height(hand_positions, toss_peak)
        toss_timing = self._calculate_toss_timing(hand_positions, toss_peak, serve)
        
        return {
            'serve_id': serve.get('stroke_id', ''),
            'toss_peak_time': toss_peak.get('timestamp', 0) if toss_peak else 0,
            'toss_height': toss_height,
            'toss_timing': toss_timing,
            'hand_trajectory': hand_positions,
            'technique_score': self._score_toss_technique(toss_height, toss_timing)
        }
    
    def _find_toss_peak(self, hand_positions: List[Dict]) -> Optional[Dict]:
        """Find the peak of the toss"""
        if not hand_positions:
            return None
        
        # Find highest y position (lowest value since y increases downward)
        min_y = min(pos['y'] for pos in hand_positions)
        
        for pos in hand_positions:
            if pos['y'] == min_y:
                return pos
        
        return None
    
    def _calculate_toss_height(self, hand_positions: List[Dict], toss_peak: Optional[Dict]) -> float:
        """Calculate toss height"""
        if not hand_positions or not toss_peak:
            return 0.0
        
        # Find starting position (first position)
        start_pos = hand_positions[0]
        
        # Calculate height difference
        height_diff = start_pos['y'] - toss_peak['y']  # y decreases upward
        
        # Convert to approximate meters (rough estimation)
        estimated_height = height_diff * 3.0  # Scaling factor
        
        return max(0.0, estimated_height)
    
    def _calculate_toss_timing(self, hand_positions: List[Dict], toss_peak: Optional[Dict], serve: Dict) -> float:
        """Calculate time from toss peak to contact"""
        if not toss_peak:
            return 0.0
        
        contact_time = serve.get('contact_time', serve.get('end_time', 0))
        toss_peak_time = toss_peak['timestamp']
        
        return max(0.0, contact_time - toss_peak_time)
    
    def _score_toss_technique(self, height: float, timing: float) -> float:
        """Score toss technique (0-1)"""
        height_score = 1.0
        timing_score = 1.0
        
        # Height scoring
        if self.optimal_toss_height_range[0] <= height <= self.optimal_toss_height_range[1]:
            height_score = 1.0
        else:
            height_deviation = min(
                abs(height - self.optimal_toss_height_range[0]),
                abs(height - self.optimal_toss_height_range[1])
            )
            height_score = max(0.0, 1.0 - height_deviation / 2.0)
        
        # Timing scoring (optimal range 0.8-1.2 seconds)
        if 0.8 <= timing <= 1.2:
            timing_score = 1.0
        else:
            timing_deviation = min(abs(timing - 0.8), abs(timing - 1.2))
            timing_score = max(0.0, 1.0 - timing_deviation / 1.0)
        
        return (height_score + timing_score) / 2.0
    
    def _calculate_toss_consistency(self, toss_events: List[Dict]) -> Dict:
        """Calculate toss consistency metrics"""
        if not toss_events:
            return {}
        
        heights = [t.get('toss_height', 0) for t in toss_events]
        timings = [t.get('toss_timing', 0) for t in toss_events]
        scores = [t.get('technique_score', 0) for t in toss_events]
        
        return {
            'height_consistency': float(1.0 / (1.0 + np.std(heights))) if np.std(heights) > 0 else 1.0,
            'timing_consistency': float(1.0 / (1.0 + np.std(timings))) if np.std(timings) > 0 else 1.0,
            'overall_technique_score': float(np.mean(scores)),
            'consistency_rating': self._rate_consistency(heights, timings)
        }
    
    def _rate_consistency(self, heights: List[float], timings: List[float]) -> str:
        """Rate overall toss consistency"""
        height_std = np.std(heights) if len(heights) > 1 else 0
        timing_std = np.std(timings) if len(timings) > 1 else 0
        
        if height_std < 0.2 and timing_std < 0.1:
            return "Excellent"
        elif height_std < 0.4 and timing_std < 0.2:
            return "Good"
        elif height_std < 0.6 and timing_std < 0.3:
            return "Fair"
        else:
            return "Needs Improvement"
    
    def _generate_toss_recommendations(self, toss_events: List[Dict]) -> List[str]:
        """Generate toss improvement recommendations"""
        recommendations = []
        
        if not toss_events:
            return recommendations
        
        heights = [t.get('toss_height', 0) for t in toss_events]
        timings = [t.get('toss_timing', 0) for t in toss_events]
        scores = [t.get('technique_score', 0) for t in toss_events]
        
        # Height recommendations
        avg_height = np.mean(heights)
        height_std = np.std(heights)
        
        if height_std > 0.3:
            recommendations.append("Focus on consistent toss height - practice with target")
        
        if avg_height < 1.5:
            recommendations.append("Increase toss height for more power and time")
        elif avg_height > 2.5:
            recommendations.append("Lower toss height for better control")
        
        # Timing recommendations
        avg_timing = np.mean(timings)
        timing_std = np.std(timings)
        
        if timing_std > 0.2:
            recommendations.append("Work on toss timing consistency")
        
        if avg_timing < 0.6:
            recommendations.append("Allow more time between toss and contact")
        elif avg_timing > 1.5:
            recommendations.append("Reduce delay between toss and contact")
        
        # Overall technique
        avg_score = np.mean(scores)
        if avg_score < 0.6:
            recommendations.append("Overall toss technique needs improvement")
        elif avg_score > 0.8:
            recommendations.append("Excellent toss technique - maintain consistency")
        
        return recommendations
