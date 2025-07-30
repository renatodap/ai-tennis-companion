"""
🧠 AI COACHING SYSTEM
Phase 4: AI insights, pattern detection, coaching suggestions
"""

import openai
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import logging
import asyncio
from dataclasses import dataclass
import os
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class CoachingInsight:
    """AI-generated coaching insight"""
    category: str  # technique, tactics, mental, physical
    priority: str  # high, medium, low
    insight: str
    recommendation: str
    confidence: float

class AICoach:
    """🧠 AI-powered tennis coaching system"""
    
    def __init__(self):
        # Initialize OpenAI client (API key should be in environment)
        self.client = openai.AsyncOpenAI(
            api_key=os.getenv('OPENAI_API_KEY', 'your-api-key-here')
        )
        
        self.pattern_detector = PatternDetector()
        self.performance_analyzer = PerformanceAnalyzer()
        
    async def generate_insights(self, stroke_events: List[Dict], analytics: Dict, session_metadata: Dict) -> Dict:
        """Generate comprehensive AI coaching insights"""
        logger.info("🧠 Generating AI coaching insights...")
        
        try:
            # Analyze patterns
            patterns = await self.pattern_detector.detect_patterns(stroke_events, analytics)
            
            # Analyze performance trends
            performance = await self.performance_analyzer.analyze_performance(stroke_events, analytics)
            
            # Generate AI summary
            ai_summary = await self._generate_ai_summary(stroke_events, analytics, session_metadata)
            
            # Generate specific coaching recommendations
            coaching_recommendations = await self._generate_coaching_recommendations(patterns, performance)
            
            # Create match comparison (if applicable)
            match_comparison = await self._generate_match_comparison(analytics, session_metadata)
            
            return {
                'ai_summary': ai_summary,
                'patterns': patterns,
                'performance_analysis': performance,
                'coaching_recommendations': coaching_recommendations,
                'match_comparison': match_comparison,
                'key_insights': self._extract_key_insights(patterns, performance)
            }
            
        except Exception as e:
            logger.error(f"AI coaching failed: {e}")
            return {
                'ai_summary': "AI analysis temporarily unavailable",
                'patterns': {},
                'performance_analysis': {},
                'coaching_recommendations': [],
                'match_comparison': {},
                'key_insights': []
            }
    
    async def _generate_ai_summary(self, stroke_events: List[Dict], analytics: Dict, session_metadata: Dict) -> str:
        """Generate AI-powered match summary"""
        
        # Prepare data for AI analysis
        summary_data = {
            'session_type': session_metadata.get('session_type', 'practice'),
            'total_strokes': len(stroke_events),
            'stroke_distribution': analytics.get('stroke_distribution', {}),
            'rally_stats': analytics.get('rally_analysis', {}).get('rally_stats', {}),
            'pressure_performance': analytics.get('rally_analysis', {}).get('pressure_analysis', {}),
            'serve_stats': analytics.get('serve_analysis', {})
        }
        
        prompt = self._create_summary_prompt(summary_data)
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert tennis coach analyzing a player's performance. Provide concise, actionable insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._generate_fallback_summary(summary_data)
    
    def _create_summary_prompt(self, data: Dict) -> str:
        """Create prompt for AI summary generation"""
        return f"""
        Analyze this tennis session data and provide a concise summary with key insights:
        
        Session Type: {data['session_type']}
        Total Strokes: {data['total_strokes']}
        Stroke Distribution: {data['stroke_distribution']}
        Rally Statistics: {data['rally_stats']}
        Pressure Performance: {data['pressure_performance']}
        
        Focus on:
        1. Overall performance assessment
        2. Key strengths and weaknesses
        3. Specific areas for improvement
        4. Notable patterns or trends
        
        Keep it under 200 words and make it actionable for a tennis player.
        """
    
    def _generate_fallback_summary(self, data: Dict) -> str:
        """Generate fallback summary when AI is unavailable"""
        total_strokes = data.get('total_strokes', 0)
        session_type = data.get('session_type', 'practice')
        
        summary = f"Completed {session_type} session with {total_strokes} strokes analyzed. "
        
        # Add stroke distribution insight
        stroke_dist = data.get('stroke_distribution', {})
        if stroke_dist:
            dominant_stroke = max(stroke_dist.items(), key=lambda x: x[1])[0]
            summary += f"Primary stroke type: {dominant_stroke}. "
        
        # Add rally insight
        rally_stats = data.get('rally_stats', {})
        avg_rally = rally_stats.get('average_length', 0)
        if avg_rally > 0:
            summary += f"Average rally length: {avg_rally:.1f} shots. "
        
        summary += "Continue practicing to improve consistency and technique."
        
        return summary
    
    async def _generate_coaching_recommendations(self, patterns: Dict, performance: Dict) -> List[CoachingInsight]:
        """Generate specific coaching recommendations"""
        recommendations = []
        
        # Technique recommendations
        technique_issues = patterns.get('technique_patterns', {}).get('issues', [])
        for issue in technique_issues:
            recommendations.append(CoachingInsight(
                category="technique",
                priority="high",
                insight=issue,
                recommendation=self._get_technique_recommendation(issue),
                confidence=0.8
            ))
        
        # Tactical recommendations
        tactical_patterns = patterns.get('tactical_patterns', {})
        if tactical_patterns.get('predictability_score', 0) > 0.7:
            recommendations.append(CoachingInsight(
                category="tactics",
                priority="medium",
                insight="Shot patterns are predictable",
                recommendation="Vary shot selection and court positioning to become less predictable",
                confidence=0.9
            ))
        
        # Mental/pressure recommendations
        pressure_performance = performance.get('pressure_performance', 0)
        if pressure_performance < 0.5:
            recommendations.append(CoachingInsight(
                category="mental",
                priority="high",
                insight="Performance drops under pressure",
                recommendation="Practice pressure situations and develop mental resilience techniques",
                confidence=0.85
            ))
        
        return recommendations
    
    def _get_technique_recommendation(self, issue: str) -> str:
        """Get technique recommendation for specific issue"""
        recommendations = {
            "inconsistent_swing_speed": "Focus on smooth, controlled swings. Practice with metronome for rhythm.",
            "poor_follow_through": "Extend follow-through across body. Practice shadow swings.",
            "inconsistent_contact_point": "Work on footwork and positioning. Use target practice drills.",
            "low_toss_consistency": "Practice toss with consistent release point and height.",
            "erratic_shot_placement": "Improve court awareness and target practice."
        }
        
        return recommendations.get(issue, "Work with coach on specific technique refinement.")
    
    async def _generate_match_comparison(self, analytics: Dict, session_metadata: Dict) -> Dict:
        """Generate comparison with previous sessions"""
        # Placeholder for match history comparison
        # In production, this would compare with stored historical data
        
        return {
            'comparison_available': False,
            'trend_analysis': "No historical data available for comparison",
            'improvement_areas': [],
            'performance_trend': "neutral"
        }
    
    def _extract_key_insights(self, patterns: Dict, performance: Dict) -> List[str]:
        """Extract top 3-5 key insights"""
        insights = []
        
        # Pattern insights
        if patterns.get('dominant_pattern'):
            insights.append(f"Dominant pattern: {patterns['dominant_pattern']}")
        
        # Performance insights
        consistency_score = performance.get('consistency_score', 0)
        if consistency_score > 0.8:
            insights.append("High consistency in stroke execution")
        elif consistency_score < 0.6:
            insights.append("Focus needed on stroke consistency")
        
        # Pressure insights
        pressure_perf = performance.get('pressure_performance', 0)
        if pressure_perf > 0.7:
            insights.append("Strong performance under pressure")
        elif pressure_perf < 0.5:
            insights.append("Pressure situations need work")
        
        return insights[:5]  # Return top 5 insights


class PatternDetector:
    """🔍 Advanced pattern detection engine"""
    
    def __init__(self):
        self.pattern_threshold = 0.6
        self.sequence_length = 3
    
    async def detect_patterns(self, stroke_events: List[Dict], analytics: Dict) -> Dict:
        """Detect playing patterns and tendencies"""
        logger.info("🔍 Detecting playing patterns...")
        
        if not stroke_events:
            return {}
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(stroke_events)
        
        # Detect shot sequence patterns
        sequence_patterns = self._detect_sequence_patterns(df)
        
        # Detect situational patterns
        situational_patterns = self._detect_situational_patterns(df)
        
        # Detect technique patterns
        technique_patterns = self._detect_technique_patterns(df)
        
        # Calculate predictability score
        predictability = self._calculate_predictability(df)
        
        return {
            'sequence_patterns': sequence_patterns,
            'situational_patterns': situational_patterns,
            'technique_patterns': technique_patterns,
            'predictability_score': predictability,
            'dominant_pattern': self._identify_dominant_pattern(sequence_patterns)
        }
    
    def _detect_sequence_patterns(self, df: pd.DataFrame) -> Dict:
        """Detect shot sequence patterns"""
        if len(df) < self.sequence_length:
            return {}
        
        # Create sequences of stroke types
        sequences = []
        for i in range(len(df) - self.sequence_length + 1):
            sequence = tuple(df.iloc[i:i+self.sequence_length]['stroke_type'].tolist())
            sequences.append(sequence)
        
        # Count sequence frequencies
        sequence_counts = pd.Series(sequences).value_counts()
        total_sequences = len(sequences)
        
        # Find common patterns (>10% frequency)
        common_patterns = {}
        for sequence, count in sequence_counts.items():
            frequency = count / total_sequences
            if frequency > 0.1:
                common_patterns[' -> '.join(sequence)] = {
                    'frequency': float(frequency),
                    'count': int(count)
                }
        
        return common_patterns
    
    def _detect_situational_patterns(self, df: pd.DataFrame) -> Dict:
        """Detect patterns based on situation"""
        patterns = {}
        
        # Pressure situation patterns
        if 'pressure_index' in df.columns:
            high_pressure = df[df['pressure_index'] > 0.7]
            if len(high_pressure) > 0:
                pressure_strokes = high_pressure['stroke_type'].value_counts()
                patterns['under_pressure'] = pressure_strokes.to_dict()
        
        # Rally position patterns
        if 'rally_position' in df.columns:
            early_rally = df[df['rally_position'] <= 3]
            late_rally = df[df['rally_position'] > 5]
            
            if len(early_rally) > 0:
                patterns['early_rally'] = early_rally['stroke_type'].value_counts().to_dict()
            
            if len(late_rally) > 0:
                patterns['late_rally'] = late_rally['stroke_type'].value_counts().to_dict()
        
        # Court zone patterns
        if 'court_zone' in df.columns:
            zone_patterns = df.groupby('court_zone')['stroke_type'].value_counts()
            patterns['by_court_zone'] = zone_patterns.to_dict()
        
        return patterns
    
    def _detect_technique_patterns(self, df: pd.DataFrame) -> Dict:
        """Detect technique-related patterns"""
        patterns = {'issues': [], 'strengths': []}
        
        # Swing speed consistency
        if 'swing_speed' in df.columns:
            speed_std = df['swing_speed'].std()
            if speed_std > 0.1:
                patterns['issues'].append("inconsistent_swing_speed")
            else:
                patterns['strengths'].append("consistent_swing_speed")
        
        # Shot placement consistency
        if 'shot_direction' in df.columns:
            direction_entropy = self._calculate_entropy(df['shot_direction'])
            if direction_entropy < 0.5:
                patterns['issues'].append("predictable_shot_placement")
            else:
                patterns['strengths'].append("varied_shot_placement")
        
        return patterns
    
    def _calculate_entropy(self, series: pd.Series) -> float:
        """Calculate entropy of a categorical series"""
        value_counts = series.value_counts()
        probabilities = value_counts / len(series)
        entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)
        return entropy
    
    def _calculate_predictability(self, df: pd.DataFrame) -> float:
        """Calculate overall predictability score"""
        if len(df) < 5:
            return 0.5
        
        # Calculate based on stroke type repetition
        stroke_entropy = self._calculate_entropy(df['stroke_type'])
        max_entropy = np.log2(len(df['stroke_type'].unique()))
        
        # Normalize to 0-1 scale (higher = more predictable)
        predictability = 1.0 - (stroke_entropy / max_entropy) if max_entropy > 0 else 0.5
        
        return float(predictability)
    
    def _identify_dominant_pattern(self, sequence_patterns: Dict) -> Optional[str]:
        """Identify the most dominant pattern"""
        if not sequence_patterns:
            return None
        
        # Find pattern with highest frequency
        dominant = max(sequence_patterns.items(), key=lambda x: x[1]['frequency'])
        
        return dominant[0] if dominant[1]['frequency'] > 0.2 else None


class PerformanceAnalyzer:
    """📈 Performance trend analysis"""
    
    async def analyze_performance(self, stroke_events: List[Dict], analytics: Dict) -> Dict:
        """Analyze performance metrics and trends"""
        logger.info("📈 Analyzing performance trends...")
        
        if not stroke_events:
            return {}
        
        df = pd.DataFrame(stroke_events)
        
        # Calculate consistency metrics
        consistency = self._calculate_consistency_metrics(df)
        
        # Analyze pressure performance
        pressure_performance = self._analyze_pressure_performance(df)
        
        # Calculate improvement metrics
        improvement_metrics = self._calculate_improvement_metrics(df)
        
        # Identify performance peaks and valleys
        performance_trends = self._identify_performance_trends(df)
        
        return {
            'consistency_score': consistency,
            'pressure_performance': pressure_performance,
            'improvement_metrics': improvement_metrics,
            'performance_trends': performance_trends,
            'overall_rating': self._calculate_overall_rating(consistency, pressure_performance)
        }
    
    def _calculate_consistency_metrics(self, df: pd.DataFrame) -> float:
        """Calculate overall consistency score"""
        consistency_factors = []
        
        # Swing speed consistency
        if 'swing_speed' in df.columns and len(df) > 1:
            speed_consistency = 1.0 / (1.0 + df['swing_speed'].std())
            consistency_factors.append(speed_consistency)
        
        # Stroke type distribution consistency
        stroke_distribution = df['stroke_type'].value_counts()
        stroke_entropy = self._calculate_entropy(stroke_distribution)
        max_entropy = np.log2(len(stroke_distribution))
        stroke_consistency = stroke_entropy / max_entropy if max_entropy > 0 else 0
        consistency_factors.append(stroke_consistency)
        
        # Overall consistency
        return float(np.mean(consistency_factors)) if consistency_factors else 0.5
    
    def _analyze_pressure_performance(self, df: pd.DataFrame) -> float:
        """Analyze performance under pressure"""
        if 'pressure_index' not in df.columns or 'outcome' not in df.columns:
            return 0.5
        
        high_pressure = df[df['pressure_index'] > 0.7]
        
        if len(high_pressure) == 0:
            return 0.5
        
        # Calculate success rate under pressure
        successful_outcomes = ['winner', 'in_play']
        pressure_success = high_pressure[high_pressure['outcome'].isin(successful_outcomes)]
        
        return float(len(pressure_success) / len(high_pressure))
    
    def _calculate_improvement_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate improvement metrics over session"""
        if len(df) < 10:
            return {'trend': 'insufficient_data'}
        
        # Split session into first and second half
        mid_point = len(df) // 2
        first_half = df.iloc[:mid_point]
        second_half = df.iloc[mid_point:]
        
        # Compare consistency between halves
        first_consistency = self._calculate_consistency_metrics(first_half)
        second_consistency = self._calculate_consistency_metrics(second_half)
        
        improvement = second_consistency - first_consistency
        
        return {
            'consistency_trend': 'improving' if improvement > 0.05 else 'declining' if improvement < -0.05 else 'stable',
            'improvement_score': float(improvement),
            'first_half_performance': float(first_consistency),
            'second_half_performance': float(second_consistency)
        }
    
    def _identify_performance_trends(self, df: pd.DataFrame) -> Dict:
        """Identify performance trends throughout session"""
        if len(df) < 5:
            return {}
        
        # Create time-based performance windows
        window_size = max(5, len(df) // 10)
        windows = []
        
        for i in range(0, len(df) - window_size + 1, window_size):
            window = df.iloc[i:i+window_size]
            window_performance = self._calculate_consistency_metrics(window)
            windows.append({
                'start_time': float(window.iloc[0]['start_time']),
                'performance': window_performance
            })
        
        return {
            'performance_windows': windows,
            'trend_direction': self._calculate_trend_direction(windows)
        }
    
    def _calculate_trend_direction(self, windows: List[Dict]) -> str:
        """Calculate overall trend direction"""
        if len(windows) < 2:
            return 'stable'
        
        performances = [w['performance'] for w in windows]
        
        # Simple linear trend
        x = np.arange(len(performances))
        slope = np.polyfit(x, performances, 1)[0]
        
        if slope > 0.02:
            return 'improving'
        elif slope < -0.02:
            return 'declining'
        else:
            return 'stable'
    
    def _calculate_entropy(self, series) -> float:
        """Calculate entropy for consistency measurement"""
        if hasattr(series, 'values'):
            values = series.values
        else:
            values = series
        
        probabilities = values / np.sum(values)
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        return entropy
    
    def _calculate_overall_rating(self, consistency: float, pressure_performance: float) -> str:
        """Calculate overall performance rating"""
        overall_score = (consistency + pressure_performance) / 2
        
        if overall_score >= 0.8:
            return "Excellent"
        elif overall_score >= 0.7:
            return "Good"
        elif overall_score >= 0.6:
            return "Fair"
        else:
            return "Needs Improvement"
