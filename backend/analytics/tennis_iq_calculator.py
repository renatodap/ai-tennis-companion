"""
🎾 Tennis IQ Calculator - The Most Advanced Tennis Scoring System Ever Built

This module calculates a comprehensive Tennis IQ score that captures:
- Technical skill (stroke mechanics, consistency)
- Tactical intelligence (shot selection, court positioning)
- Mental toughness (pressure performance, clutch factor)
- Physical attributes (power, speed, endurance)
- Match intelligence (pattern recognition, adaptation)

The Tennis IQ score ranges from 0-1000, with professional benchmarks:
- 900-1000: ATP/WTA Top 10 level
- 800-899: Professional tour level
- 700-799: College/Academy elite
- 600-699: Advanced club player
- 500-599: Intermediate club player
- 400-499: Recreational regular
- 300-399: Beginner with basics
- 200-299: Learning fundamentals
- 100-199: New to tennis
- 0-99: Just picked up a racket
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import math


class TennisLevel(Enum):
    """Professional tennis level classifications"""
    LEGEND = ("Legend", 950, 1000, "🏆")
    ATP_TOP_10 = ("ATP Top 10", 900, 949, "🥇")
    PROFESSIONAL = ("Professional", 800, 899, "🎾")
    ELITE_ACADEMY = ("Elite Academy", 700, 799, "⭐")
    ADVANCED_CLUB = ("Advanced Club", 600, 699, "🔥")
    INTERMEDIATE = ("Intermediate", 500, 599, "💪")
    RECREATIONAL = ("Recreational", 400, 499, "🎯")
    BEGINNER_PLUS = ("Learning", 300, 399, "📈")
    BEGINNER = ("Beginner", 200, 299, "🌱")
    NEWCOMER = ("Newcomer", 100, 199, "🎾")
    JUST_STARTED = ("Just Started", 0, 99, "🏁")


@dataclass
class TennisIQComponents:
    """Individual components that make up Tennis IQ"""
    technical_skill: float = 0.0
    tactical_intelligence: float = 0.0
    mental_toughness: float = 0.0
    physical_attributes: float = 0.0
    match_intelligence: float = 0.0
    
    @property
    def total_score(self) -> float:
        return (self.technical_skill + self.tactical_intelligence + 
                self.mental_toughness + self.physical_attributes + 
                self.match_intelligence)
    
    @property
    def level(self) -> TennisLevel:
        score = self.total_score
        for level in TennisLevel:
            if level.value[1] <= score <= level.value[2]:
                return level
        return TennisLevel.JUST_STARTED


@dataclass
class TennisIQInsights:
    """Insights and recommendations based on Tennis IQ analysis"""
    strengths: List[str]
    weaknesses: List[str]
    improvement_areas: List[str]
    next_level_requirements: List[str]
    comparison_to_pros: Dict[str, Any]
    achievement_unlocked: str = ""
    motivational_message: str = ""


class TennisIQCalculator:
    """The most sophisticated tennis analysis system ever created."""
    
    def __init__(self):
        self.pro_benchmarks = {
            'federer': {'technical': 195, 'tactical': 190, 'mental': 200, 'physical': 180, 'match': 195},
            'nadal': {'technical': 185, 'tactical': 195, 'mental': 200, 'physical': 200, 'match': 190},
            'djokovic': {'technical': 190, 'tactical': 200, 'mental': 200, 'physical': 185, 'match': 200}
        }
    
    def calculate_tennis_iq(self, stroke_events: List[Dict], analytics: Dict, 
                           match_context: Dict = None) -> Tuple[TennisIQComponents, TennisIQInsights]:
        """Calculate comprehensive Tennis IQ score"""
        
        technical = self._calculate_technical_skill(stroke_events, analytics)
        tactical = self._calculate_tactical_intelligence(stroke_events, analytics)
        mental = self._calculate_mental_toughness(stroke_events, analytics)
        physical = self._calculate_physical_attributes(stroke_events, analytics)
        match_iq = self._calculate_match_intelligence(stroke_events, analytics)
        
        components = TennisIQComponents(
            technical_skill=technical,
            tactical_intelligence=tactical,
            mental_toughness=mental,
            physical_attributes=physical,
            match_intelligence=match_iq
        )
        
        insights = self._generate_insights(components, stroke_events, analytics)
        return components, insights
    
    def _calculate_technical_skill(self, stroke_events: List[Dict], analytics: Dict) -> float:
        """Calculate technical skill component (0-200)"""
        if not stroke_events:
            return 100.0
            
        # Stroke consistency
        consistency = self._analyze_consistency(stroke_events)
        variety = self._analyze_variety(stroke_events)
        technique = self._analyze_technique(stroke_events)
        accuracy = self._analyze_accuracy(analytics)
        
        score = (consistency * 0.3 + variety * 0.2 + technique * 0.3 + accuracy * 0.2) * 200
        return min(200.0, max(50.0, score))
    
    def _calculate_tactical_intelligence(self, stroke_events: List[Dict], analytics: Dict) -> float:
        """Calculate tactical intelligence (0-200)"""
        if not stroke_events:
            return 100.0
            
        positioning = self._analyze_positioning(analytics)
        selection = self._analyze_shot_selection(stroke_events)
        patterns = self._analyze_patterns(stroke_events)
        
        score = (positioning * 0.4 + selection * 0.4 + patterns * 0.2) * 200
        return min(200.0, max(50.0, score))
    
    def _calculate_mental_toughness(self, stroke_events: List[Dict], analytics: Dict) -> float:
        """Calculate mental toughness (0-200)"""
        if not stroke_events:
            return 100.0
            
        pressure = self._analyze_pressure(analytics)
        consistency = self._analyze_mental_consistency(stroke_events)
        recovery = self._analyze_recovery(stroke_events)
        
        score = (pressure * 0.4 + consistency * 0.3 + recovery * 0.3) * 200
        return min(200.0, max(50.0, score))
    
    def _calculate_physical_attributes(self, stroke_events: List[Dict], analytics: Dict) -> float:
        """Calculate physical attributes (0-200)"""
        if not stroke_events:
            return 100.0
            
        power = self._analyze_power(stroke_events)
        coverage = self._analyze_coverage(analytics)
        endurance = self._analyze_endurance(stroke_events)
        
        score = (power * 0.4 + coverage * 0.3 + endurance * 0.3) * 200
        return min(200.0, max(50.0, score))
    
    def _calculate_match_intelligence(self, stroke_events: List[Dict], analytics: Dict) -> float:
        """Calculate match intelligence (0-200)"""
        if not stroke_events:
            return 100.0
            
        adaptation = self._analyze_adaptation(stroke_events)
        strategy = self._analyze_strategy(stroke_events, analytics)
        learning = self._analyze_learning(stroke_events)
        
        score = (adaptation * 0.4 + strategy * 0.3 + learning * 0.3) * 200
        return min(200.0, max(50.0, score))
    
    def _analyze_consistency(self, stroke_events: List[Dict]) -> float:
        """Analyze stroke consistency"""
        if len(stroke_events) < 3:
            return 0.5
            
        confidences = [s.get('confidence', 0.5) for s in stroke_events]
        velocities = [s.get('peak_velocity', 0) for s in stroke_events if s.get('peak_velocity', 0) > 0]
        
        confidence_consistency = 1 - np.std(confidences) if confidences else 0.5
        velocity_consistency = 1 - (np.std(velocities) / (np.mean(velocities) + 1e-6)) if velocities else 0.5
        
        return (confidence_consistency + velocity_consistency) / 2
    
    def _analyze_variety(self, stroke_events: List[Dict]) -> float:
        """Analyze stroke variety"""
        stroke_types = set(s.get('stroke_type', 'unknown') for s in stroke_events)
        return min(1.0, len(stroke_types) / 6.0)
    
    def _analyze_technique(self, stroke_events: List[Dict]) -> float:
        """Analyze technique quality"""
        if not stroke_events:
            return 0.5
        return np.mean([s.get('confidence', 0.5) for s in stroke_events])
    
    def _analyze_accuracy(self, analytics: Dict) -> float:
        """Analyze shot accuracy"""
        if not analytics:
            return 0.5
        return analytics.get('shot_analysis', {}).get('accuracy', 0.5)
    
    def _analyze_positioning(self, analytics: Dict) -> float:
        """Analyze court positioning"""
        if not analytics or 'heatmap_data' not in analytics:
            return 0.5
        return analytics['heatmap_data'].get('strategic_score', 0.5)
    
    def _analyze_shot_selection(self, stroke_events: List[Dict]) -> float:
        """Analyze shot selection quality"""
        if not stroke_events:
            return 0.5
        
        good_selections = 0
        for stroke in stroke_events:
            stroke_type = stroke.get('stroke_type', '')
            position = stroke.get('court_position', '')
            
            if (position == 'baseline' and stroke_type in ['forehand', 'backhand']) or \
               (position == 'net' and stroke_type == 'volley') or \
               (position == 'service_box' and stroke_type == 'serve'):
                good_selections += 1
        
        return good_selections / len(stroke_events) if stroke_events else 0.5
    
    def _analyze_patterns(self, stroke_events: List[Dict]) -> float:
        """Analyze tactical patterns"""
        if len(stroke_events) < 3:
            return 0.5
        
        stroke_types = [s.get('stroke_type', '') for s in stroke_events]
        patterns = 0
        
        # Look for serve-volley patterns
        for i in range(len(stroke_types) - 1):
            if stroke_types[i] == 'serve' and stroke_types[i+1] == 'volley':
                patterns += 1
        
        return min(1.0, patterns / max(1, len(stroke_events) // 3))
    
    def _analyze_pressure(self, analytics: Dict) -> float:
        """Analyze pressure performance"""
        if not analytics:
            return 0.5
        return analytics.get('rally_analysis', {}).get('pressure_index', 0.5)
    
    def _analyze_mental_consistency(self, stroke_events: List[Dict]) -> float:
        """Analyze mental consistency"""
        if len(stroke_events) < 3:
            return 0.5
        
        confidences = [s.get('confidence', 0.5) for s in stroke_events]
        return max(0, 1 - np.std(confidences))
    
    def _analyze_recovery(self, stroke_events: List[Dict]) -> float:
        """Analyze error recovery"""
        if len(stroke_events) < 3:
            return 0.5
        
        recoveries = 0
        for i in range(1, len(stroke_events)):
            if stroke_events[i-1].get('confidence', 0.5) < 0.5 and \
               stroke_events[i].get('confidence', 0.5) > stroke_events[i-1].get('confidence', 0.5):
                recoveries += 1
        
        return recoveries / max(1, len(stroke_events) - 1)
    
    def _analyze_power(self, stroke_events: List[Dict]) -> float:
        """Analyze shot power"""
        velocities = [s.get('peak_velocity', 0) for s in stroke_events if s.get('peak_velocity', 0) > 0]
        if not velocities:
            return 0.3
        return min(1.0, np.mean(velocities) / 50.0)
    
    def _analyze_coverage(self, analytics: Dict) -> float:
        """Analyze court coverage"""
        if not analytics or 'heatmap_data' not in analytics:
            return 0.5
        
        zones = analytics['heatmap_data'].get('zones', [])
        active_zones = len([z for z in zones if z.get('intensity', 0) > 0])
        return min(1.0, active_zones / 12.0)
    
    def _analyze_endurance(self, stroke_events: List[Dict]) -> float:
        """Analyze endurance"""
        if len(stroke_events) < 10:
            return 0.5
        
        first_half = stroke_events[:len(stroke_events)//2]
        second_half = stroke_events[len(stroke_events)//2:]
        
        first_avg = np.mean([s.get('confidence', 0.5) for s in first_half])
        second_avg = np.mean([s.get('confidence', 0.5) for s in second_half])
        
        return min(1.0, second_avg / (first_avg + 1e-6))
    
    def _analyze_adaptation(self, stroke_events: List[Dict]) -> float:
        """Analyze adaptation"""
        if len(stroke_events) < 5:
            return 0.5
        
        confidences = [s.get('confidence', 0.5) for s in stroke_events]
        x = np.arange(len(confidences))
        slope = np.polyfit(x, confidences, 1)[0]
        
        return 0.5 + min(0.5, max(-0.5, slope * 10))
    
    def _analyze_strategy(self, stroke_events: List[Dict], analytics: Dict) -> float:
        """Analyze strategic thinking"""
        variety_score = self._analyze_variety(stroke_events)
        positioning_score = self._analyze_positioning(analytics)
        return (variety_score + positioning_score) / 2
    
    def _analyze_learning(self, stroke_events: List[Dict]) -> float:
        """Analyze learning rate"""
        if len(stroke_events) < 3:
            return 0.5
        
        improvements = 0
        opportunities = 0
        
        for i in range(1, len(stroke_events)):
            if stroke_events[i-1].get('confidence', 0.5) < 0.5:
                opportunities += 1
                if stroke_events[i].get('confidence', 0.5) > stroke_events[i-1].get('confidence', 0.5):
                    improvements += 1
        
        return improvements / max(1, opportunities)
    
    def _generate_insights(self, components: TennisIQComponents, 
                          stroke_events: List[Dict], analytics: Dict) -> TennisIQInsights:
        """Generate insights and recommendations"""
        
        scores = {
            'Technical Skill': components.technical_skill,
            'Tactical Intelligence': components.tactical_intelligence,
            'Mental Toughness': components.mental_toughness,
            'Physical Attributes': components.physical_attributes,
            'Match Intelligence': components.match_intelligence
        }
        
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        strengths = [f"{name}: {score:.0f}/200" for name, score in sorted_scores[:2]]
        weaknesses = [f"{name}: {score:.0f}/200" for name, score in sorted_scores[-2:]]
        
        improvements = []
        if components.technical_skill < 120:
            improvements.append("Focus on stroke consistency and technique")
        if components.tactical_intelligence < 120:
            improvements.append("Work on shot selection and positioning")
        if components.mental_toughness < 120:
            improvements.append("Practice pressure situations")
        
        level = components.level
        next_requirements = [f"Reach {level.value[2] + 50} total points to advance"]
        
        # Pro comparison
        federer_total = sum(self.pro_benchmarks['federer'].values())
        user_percentage = (components.total_score / federer_total) * 100
        
        comparison = {
            'federer_comparison': f"You're {user_percentage:.1f}% of Federer's level",
            'strongest_vs_federer': f"Your {sorted_scores[0][0].lower()} is {(sorted_scores[0][1]/195)*100:.1f}% of Federer's"
        }
        
        achievement = f"Tennis IQ Level: {level.value[0]} {level.value[3]}"
        motivation = f"You're a {level.value[0]} player! Keep pushing to reach the next level."
        
        return TennisIQInsights(
            strengths=strengths,
            weaknesses=weaknesses,
            improvement_areas=improvements,
            next_level_requirements=next_requirements,
            comparison_to_pros=comparison,
            achievement_unlocked=achievement,
            motivational_message=motivation
        )
