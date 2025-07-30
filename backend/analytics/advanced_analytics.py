"""
🎾 ADVANCED ANALYTICS MODULES
Phase 2: Rally Analysis, Pressure Index, Heatmaps, Shot Direction
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.cluster import KMeans
import cv2
from typing import Dict, List, Tuple, Optional
import logging
import asyncio
from dataclasses import dataclass
import json
import io
import base64

logger = logging.getLogger(__name__)

@dataclass
class RallyEvent:
    """Rally event with comprehensive stats"""
    rally_id: str
    start_time: float
    end_time: float
    duration: float
    stroke_count: int
    strokes: List[Dict]
    winner: str  # player, opponent, error
    pressure_score: float
    momentum_shift: float

class RallyAnalyzer:
    """📊 Rally analysis and pressure detection"""
    
    def __init__(self):
        self.rally_gap_threshold = 3.0  # seconds between rallies
        self.pressure_factors = {
            'rally_length': 0.3,
            'error_rate': 0.4,
            'shot_difficulty': 0.3
        }
    
    async def analyze_rallies(self, stroke_events: List[Dict]) -> Dict:
        """Analyze rally patterns and generate insights"""
        logger.info("📊 Analyzing rally patterns...")
        
        if not stroke_events:
            return {'rallies': [], 'rally_stats': {}, 'momentum_chart': []}
        
        # Segment strokes into rallies
        rallies = self._segment_rallies(stroke_events)
        
        # Calculate rally statistics
        rally_stats = self._calculate_rally_stats(rallies)
        
        # Generate momentum chart
        momentum_chart = self._generate_momentum_chart(rallies)
        
        # Analyze pressure moments
        pressure_analysis = self._analyze_pressure_moments(rallies)
        
        return {
            'rallies': [self._rally_to_dict(r) for r in rallies],
            'rally_stats': rally_stats,
            'momentum_chart': momentum_chart,
            'pressure_analysis': pressure_analysis
        }
    
    def _segment_rallies(self, stroke_events: List[Dict]) -> List[RallyEvent]:
        """Segment strokes into rally events"""
        rallies = []
        current_strokes = []
        rally_id = 0
        
        for i, stroke in enumerate(stroke_events):
            # Start new rally on serve or after gap
            if (stroke['stroke_type'] == 'serve' or 
                (current_strokes and 
                 stroke['start_time'] - current_strokes[-1]['end_time'] > self.rally_gap_threshold)):
                
                if current_strokes:
                    rally = self._create_rally_event(rally_id, current_strokes)
                    rallies.append(rally)
                    rally_id += 1
                
                current_strokes = [stroke]
            else:
                current_strokes.append(stroke)
        
        # Add final rally
        if current_strokes:
            rally = self._create_rally_event(rally_id, current_strokes)
            rallies.append(rally)
        
        return rallies
    
    def _create_rally_event(self, rally_id: int, strokes: List[Dict]) -> RallyEvent:
        """Create rally event from stroke sequence"""
        start_time = strokes[0]['start_time']
        end_time = strokes[-1]['end_time']
        duration = end_time - start_time
        
        # Determine winner based on last stroke outcome
        last_stroke = strokes[-1]
        winner = self._determine_rally_winner(last_stroke)
        
        # Calculate pressure score
        pressure_score = self._calculate_rally_pressure(strokes)
        
        return RallyEvent(
            rally_id=f"rally_{rally_id:03d}",
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            stroke_count=len(strokes),
            strokes=strokes,
            winner=winner,
            pressure_score=pressure_score,
            momentum_shift=0.0  # Will be calculated later
        )
    
    def _determine_rally_winner(self, last_stroke: Dict) -> str:
        """Determine rally winner from last stroke"""
        outcome = last_stroke.get('outcome', 'in_play')
        
        if outcome == 'winner':
            return 'player'
        elif outcome == 'error':
            return 'opponent'
        else:
            return 'unknown'
    
    def _calculate_rally_pressure(self, strokes: List[Dict]) -> float:
        """Calculate pressure index for rally"""
        if not strokes:
            return 0.0
        
        # Length factor
        length_factor = min(1.0, len(strokes) / 10.0)
        
        # Error rate factor
        errors = sum(1 for s in strokes if s.get('outcome') == 'error')
        error_factor = errors / len(strokes)
        
        # Shot difficulty factor (based on swing speed variance)
        speeds = [s.get('swing_speed', 0) for s in strokes]
        difficulty_factor = np.std(speeds) if len(speeds) > 1 else 0
        
        pressure = (self.pressure_factors['rally_length'] * length_factor +
                   self.pressure_factors['error_rate'] * error_factor +
                   self.pressure_factors['shot_difficulty'] * difficulty_factor)
        
        return min(1.0, pressure)
    
    def _calculate_rally_stats(self, rallies: List[RallyEvent]) -> Dict:
        """Calculate comprehensive rally statistics"""
        if not rallies:
            return {}
        
        lengths = [r.stroke_count for r in rallies]
        durations = [r.duration for r in rallies]
        pressures = [r.pressure_score for r in rallies]
        
        return {
            'total_rallies': len(rallies),
            'average_length': float(np.mean(lengths)),
            'median_length': float(np.median(lengths)),
            'longest_rally': int(max(lengths)),
            'shortest_rally': int(min(lengths)),
            'average_duration': float(np.mean(durations)),
            'total_playing_time': float(sum(durations)),
            'average_pressure': float(np.mean(pressures)),
            'high_pressure_rallies': int(sum(1 for p in pressures if p > 0.7)),
            'rally_length_distribution': np.histogram(lengths, bins=5)[0].tolist(),
            'pressure_distribution': np.histogram(pressures, bins=5)[0].tolist()
        }
    
    def _generate_momentum_chart(self, rallies: List[RallyEvent]) -> List[Dict]:
        """Generate momentum chart data"""
        momentum_chart = []
        running_momentum = 0.0
        
        for rally in rallies:
            # Calculate momentum shift
            if rally.winner == 'player':
                momentum_shift = rally.pressure_score * 0.5
            elif rally.winner == 'opponent':
                momentum_shift = -rally.pressure_score * 0.5
            else:
                momentum_shift = 0.0
            
            running_momentum += momentum_shift
            running_momentum = max(-1.0, min(1.0, running_momentum))  # Clamp to [-1, 1]
            
            rally.momentum_shift = momentum_shift
            
            momentum_chart.append({
                'time': rally.end_time,
                'momentum': running_momentum,
                'rally_id': rally.rally_id,
                'pressure': rally.pressure_score
            })
        
        return momentum_chart
    
    def _analyze_pressure_moments(self, rallies: List[RallyEvent]) -> Dict:
        """Analyze high-pressure moments"""
        high_pressure_rallies = [r for r in rallies if r.pressure_score > 0.7]
        
        if not high_pressure_rallies:
            return {'high_pressure_moments': 0, 'pressure_performance': {}}
        
        # Performance under pressure
        pressure_wins = sum(1 for r in high_pressure_rallies if r.winner == 'player')
        pressure_performance = pressure_wins / len(high_pressure_rallies)
        
        return {
            'high_pressure_moments': len(high_pressure_rallies),
            'pressure_performance': pressure_performance,
            'average_pressure_rally_length': float(np.mean([r.stroke_count for r in high_pressure_rallies])),
            'pressure_rally_outcomes': {
                'wins': pressure_wins,
                'losses': len(high_pressure_rallies) - pressure_wins
            }
        }
    
    def _rally_to_dict(self, rally: RallyEvent) -> Dict:
        """Convert rally event to dictionary"""
        return {
            'rally_id': rally.rally_id,
            'start_time': rally.start_time,
            'end_time': rally.end_time,
            'duration': rally.duration,
            'stroke_count': rally.stroke_count,
            'winner': rally.winner,
            'pressure_score': rally.pressure_score,
            'momentum_shift': rally.momentum_shift
        }


class HeatmapGenerator:
    """🔥 Player position heatmap generator"""
    
    def __init__(self, court_width: int = 400, court_height: int = 600):
        self.court_width = court_width
        self.court_height = court_height
        self.grid_size = 20
    
    async def generate_position_heatmap(self, stroke_events: List[Dict], court_info: Dict) -> Dict:
        """Generate player position heatmap"""
        logger.info("🔥 Generating position heatmap...")
        
        if not stroke_events:
            return {'heatmap_data': [], 'heatmap_image': None}
        
        # Extract player positions
        positions = []
        for stroke in stroke_events:
            pos = stroke.get('player_position', (0.5, 0.8))
            positions.append(pos)
        
        # Create heatmap grid
        heatmap_data = self._create_heatmap_grid(positions)
        
        # Generate heatmap visualization
        heatmap_image = self._generate_heatmap_image(heatmap_data)
        
        return {
            'heatmap_data': heatmap_data,
            'heatmap_image': heatmap_image,
            'total_positions': len(positions),
            'court_coverage': self._calculate_court_coverage(positions)
        }
    
    def _create_heatmap_grid(self, positions: List[Tuple[float, float]]) -> List[List[int]]:
        """Create heatmap grid from positions"""
        grid = np.zeros((self.grid_size, self.grid_size))
        
        for x, y in positions:
            # Convert normalized coordinates to grid indices
            grid_x = int(x * (self.grid_size - 1))
            grid_y = int(y * (self.grid_size - 1))
            
            # Clamp to grid bounds
            grid_x = max(0, min(self.grid_size - 1, grid_x))
            grid_y = max(0, min(self.grid_size - 1, grid_y))
            
            grid[grid_y, grid_x] += 1
        
        return grid.tolist()
    
    def _generate_heatmap_image(self, heatmap_data: List[List[int]]) -> str:
        """Generate heatmap visualization as base64 image"""
        try:
            # Create matplotlib figure
            plt.figure(figsize=(8, 10))
            
            # Create heatmap
            sns.heatmap(
                heatmap_data,
                cmap='YlOrRd',
                cbar_kws={'label': 'Position Frequency'},
                xticklabels=False,
                yticklabels=False
            )
            
            plt.title('Player Position Heatmap')
            plt.xlabel('Court Width')
            plt.ylabel('Court Length')
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            logger.error(f"Failed to generate heatmap image: {e}")
            return None
    
    def _calculate_court_coverage(self, positions: List[Tuple[float, float]]) -> float:
        """Calculate percentage of court coverage"""
        if not positions:
            return 0.0
        
        # Create binary grid
        grid = np.zeros((self.grid_size, self.grid_size))
        
        for x, y in positions:
            grid_x = int(x * (self.grid_size - 1))
            grid_y = int(y * (self.grid_size - 1))
            grid_x = max(0, min(self.grid_size - 1, grid_x))
            grid_y = max(0, min(self.grid_size - 1, grid_y))
            grid[grid_y, grid_x] = 1
        
        coverage = np.sum(grid) / (self.grid_size * self.grid_size)
        return float(coverage)


class ShotDirectionAnalyzer:
    """🎯 Shot direction and depth estimation"""
    
    def __init__(self):
        self.direction_zones = {
            'crosscourt': {'angle_range': (-45, 45)},
            'down_line': {'angle_range': (45, 135)},
            'inside_out': {'angle_range': (-135, -45)}
        }
    
    async def analyze_shot_patterns(self, stroke_events: List[Dict], court_info: Dict) -> Dict:
        """Analyze shot direction and depth patterns"""
        logger.info("🎯 Analyzing shot patterns...")
        
        if not stroke_events:
            return {}
        
        # Analyze shot directions
        direction_analysis = self._analyze_shot_directions(stroke_events)
        
        # Analyze shot depths
        depth_analysis = self._analyze_shot_depths(stroke_events)
        
        # Analyze patterns by stroke type
        stroke_patterns = self._analyze_patterns_by_stroke(stroke_events)
        
        return {
            'direction_analysis': direction_analysis,
            'depth_analysis': depth_analysis,
            'stroke_patterns': stroke_patterns,
            'tactical_insights': self._generate_tactical_insights(stroke_events)
        }
    
    def _analyze_shot_directions(self, stroke_events: List[Dict]) -> Dict:
        """Analyze shot direction patterns"""
        directions = [stroke.get('shot_direction', 'crosscourt') for stroke in stroke_events]
        direction_counts = pd.Series(directions).value_counts()
        
        return {
            'distribution': direction_counts.to_dict(),
            'most_common': direction_counts.index[0] if len(direction_counts) > 0 else 'unknown',
            'diversity_score': len(direction_counts) / len(set(directions)) if directions else 0
        }
    
    def _analyze_shot_depths(self, stroke_events: List[Dict]) -> Dict:
        """Analyze shot depth patterns"""
        depths = [stroke.get('shot_depth', 'deep') for stroke in stroke_events]
        depth_counts = pd.Series(depths).value_counts()
        
        return {
            'distribution': depth_counts.to_dict(),
            'deep_shot_percentage': depth_counts.get('deep', 0) / len(depths) if depths else 0,
            'short_shot_percentage': depth_counts.get('short', 0) / len(depths) if depths else 0
        }
    
    def _analyze_patterns_by_stroke(self, stroke_events: List[Dict]) -> Dict:
        """Analyze patterns by stroke type"""
        df = pd.DataFrame(stroke_events)
        
        if df.empty:
            return {}
        
        patterns = {}
        
        for stroke_type in df['stroke_type'].unique():
            stroke_data = df[df['stroke_type'] == stroke_type]
            
            patterns[stroke_type] = {
                'count': len(stroke_data),
                'direction_preference': stroke_data['shot_direction'].mode().iloc[0] if not stroke_data.empty else 'unknown',
                'depth_preference': stroke_data.get('shot_depth', pd.Series(['deep'])).mode().iloc[0],
                'average_speed': float(stroke_data['swing_speed'].mean()) if 'swing_speed' in stroke_data.columns else 0
            }
        
        return patterns
    
    def _generate_tactical_insights(self, stroke_events: List[Dict]) -> List[str]:
        """Generate tactical insights from shot patterns"""
        insights = []
        
        if not stroke_events:
            return insights
        
        df = pd.DataFrame(stroke_events)
        
        # Direction tendencies
        direction_counts = df['shot_direction'].value_counts()
        if len(direction_counts) > 0:
            most_common = direction_counts.index[0]
            percentage = direction_counts.iloc[0] / len(df) * 100
            
            if percentage > 60:
                insights.append(f"Strong preference for {most_common} shots ({percentage:.0f}%)")
        
        # Stroke type analysis
        stroke_counts = df['stroke_type'].value_counts()
        if len(stroke_counts) > 0:
            dominant_stroke = stroke_counts.index[0]
            stroke_percentage = stroke_counts.iloc[0] / len(df) * 100
            
            if stroke_percentage > 50:
                insights.append(f"Relies heavily on {dominant_stroke} ({stroke_percentage:.0f}%)")
        
        # Pressure performance
        if 'pressure_index' in df.columns:
            high_pressure = df[df['pressure_index'] > 0.7]
            if len(high_pressure) > 0:
                pressure_errors = high_pressure[high_pressure['outcome'] == 'error']
                error_rate = len(pressure_errors) / len(high_pressure) * 100
                
                if error_rate > 40:
                    insights.append(f"Higher error rate under pressure ({error_rate:.0f}%)")
                elif error_rate < 20:
                    insights.append(f"Performs well under pressure ({error_rate:.0f}% errors)")
        
        return insights


# Main analytics orchestrator
class AdvancedAnalyticsEngine:
    """🎾 Advanced analytics orchestrator"""
    
    def __init__(self):
        self.rally_analyzer = RallyAnalyzer()
        self.heatmap_generator = HeatmapGenerator()
        self.shot_analyzer = ShotDirectionAnalyzer()
    
    async def generate_comprehensive_analytics(self, stroke_events: List[Dict], court_info: Dict) -> Dict:
        """Generate comprehensive analytics suite"""
        logger.info("🎾 Generating comprehensive analytics...")
        
        # Run all analytics in parallel
        rally_task = self.rally_analyzer.analyze_rallies(stroke_events)
        heatmap_task = self.heatmap_generator.generate_position_heatmap(stroke_events, court_info)
        shot_task = self.shot_analyzer.analyze_shot_patterns(stroke_events, court_info)
        
        rally_analysis, heatmap_analysis, shot_analysis = await asyncio.gather(
            rally_task, heatmap_task, shot_task
        )
        
        return {
            'rally_analysis': rally_analysis,
            'heatmap_analysis': heatmap_analysis,
            'shot_analysis': shot_analysis,
            'summary': self._generate_analytics_summary(rally_analysis, shot_analysis)
        }
    
    def _generate_analytics_summary(self, rally_analysis: Dict, shot_analysis: Dict) -> Dict:
        """Generate high-level analytics summary"""
        summary = {
            'total_rallies': rally_analysis.get('rally_stats', {}).get('total_rallies', 0),
            'average_rally_length': rally_analysis.get('rally_stats', {}).get('average_length', 0),
            'pressure_performance': rally_analysis.get('pressure_analysis', {}).get('pressure_performance', 0),
            'dominant_shot_direction': shot_analysis.get('direction_analysis', {}).get('most_common', 'unknown'),
            'tactical_insights': shot_analysis.get('tactical_insights', [])
        }
        
        return summary
