/**
 * 🎾 Tennis IQ Display Component - The Most Engaging Tennis Score Ever Created
 * 
 * Features:
 * - Animated score reveal with dramatic effects
 * - Interactive radar chart showing 5 components
 * - Pro comparison with visual bars
 * - Achievement badges and level progression
 * - Social sharing with beautiful graphics
 * - Motivational messaging and next steps
 */

class TennisIQDisplay {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.currentIQ = null;
        this.animationSpeed = 50; // ms per point
        this.isAnimating = false;
        
        this.init();
    }
    
    init() {
        this.createHTML();
        this.setupEventListeners();
    }
    
    createHTML() {
        this.container.innerHTML = `
            <div class="tennis-iq-container">
                <!-- Main Score Display -->
                <div class="iq-score-section">
                    <div class="iq-score-circle">
                        <div class="iq-score-number">0</div>
                        <div class="iq-score-label">Tennis IQ</div>
                    </div>
                    <div class="iq-level-badge">
                        <span class="level-icon">🏁</span>
                        <span class="level-name">Just Started</span>
                    </div>
                </div>
                
                <!-- Component Breakdown -->
                <div class="iq-components-section">
                    <h3>Your Tennis Profile</h3>
                    <div class="component-bars">
                        <div class="component-bar" data-component="technical">
                            <div class="component-label">
                                <span class="component-icon">🎯</span>
                                <span class="component-name">Technical Skill</span>
                            </div>
                            <div class="component-progress">
                                <div class="component-fill" data-score="0"></div>
                                <span class="component-score">0/200</span>
                            </div>
                        </div>
                        
                        <div class="component-bar" data-component="tactical">
                            <div class="component-label">
                                <span class="component-icon">🧠</span>
                                <span class="component-name">Tactical Intelligence</span>
                            </div>
                            <div class="component-progress">
                                <div class="component-fill" data-score="0"></div>
                                <span class="component-score">0/200</span>
                            </div>
                        </div>
                        
                        <div class="component-bar" data-component="mental">
                            <div class="component-label">
                                <span class="component-icon">💪</span>
                                <span class="component-name">Mental Toughness</span>
                            </div>
                            <div class="component-progress">
                                <div class="component-fill" data-score="0"></div>
                                <span class="component-score">0/200</span>
                            </div>
                        </div>
                        
                        <div class="component-bar" data-component="physical">
                            <div class="component-label">
                                <span class="component-icon">⚡</span>
                                <span class="component-name">Physical Attributes</span>
                            </div>
                            <div class="component-progress">
                                <div class="component-fill" data-score="0"></div>
                                <span class="component-score">0/200</span>
                            </div>
                        </div>
                        
                        <div class="component-bar" data-component="match">
                            <div class="component-label">
                                <span class="component-icon">🎾</span>
                                <span class="component-name">Match Intelligence</span>
                            </div>
                            <div class="component-progress">
                                <div class="component-fill" data-score="0"></div>
                                <span class="component-score">0/200</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Pro Comparison -->
                <div class="pro-comparison-section">
                    <h3>Compare to the Legends</h3>
                    <div class="pro-comparisons">
                        <div class="pro-comparison" data-pro="federer">
                            <div class="pro-info">
                                <span class="pro-name">Roger Federer</span>
                                <span class="pro-comparison-text">You're 0% of Federer's level</span>
                            </div>
                            <div class="pro-bar">
                                <div class="pro-fill" data-percentage="0"></div>
                            </div>
                        </div>
                        
                        <div class="pro-comparison" data-pro="nadal">
                            <div class="pro-info">
                                <span class="pro-name">Rafael Nadal</span>
                                <span class="pro-comparison-text">You're 0% of Nadal's level</span>
                            </div>
                            <div class="pro-bar">
                                <div class="pro-fill" data-percentage="0"></div>
                            </div>
                        </div>
                        
                        <div class="pro-comparison" data-pro="djokovic">
                            <div class="pro-info">
                                <span class="pro-name">Novak Djokovic</span>
                                <span class="pro-comparison-text">You're 0% of Djokovic's level</span>
                            </div>
                            <div class="pro-bar">
                                <div class="pro-fill" data-percentage="0"></div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Insights Section -->
                <div class="insights-section">
                    <div class="insights-grid">
                        <div class="insight-card strengths-card">
                            <h4>💪 Your Strengths</h4>
                            <ul class="strengths-list">
                                <li>Analyzing your game...</li>
                            </ul>
                        </div>
                        
                        <div class="insight-card weaknesses-card">
                            <h4>🎯 Areas to Improve</h4>
                            <ul class="weaknesses-list">
                                <li>Analyzing your game...</li>
                            </ul>
                        </div>
                        
                        <div class="insight-card improvement-card">
                            <h4>📈 Next Steps</h4>
                            <ul class="improvement-list">
                                <li>Analyzing your game...</li>
                            </ul>
                        </div>
                        
                        <div class="insight-card achievement-card">
                            <h4>🏆 Achievement Unlocked</h4>
                            <div class="achievement-content">
                                <div class="achievement-badge">🏁</div>
                                <div class="achievement-text">Getting Started!</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Action Buttons -->
                <div class="iq-actions">
                    <button class="iq-action-btn share-btn" id="shareIQBtn">
                        <span class="btn-icon">📱</span>
                        Share My Tennis IQ
                    </button>
                    <button class="iq-action-btn challenge-btn" id="challengeBtn">
                        <span class="btn-icon">⚔️</span>
                        Challenge Friends
                    </button>
                    <button class="iq-action-btn improve-btn" id="improveBtn">
                        <span class="btn-icon">🚀</span>
                        Improve My Game
                    </button>
                </div>
                
                <!-- Motivational Message -->
                <div class="motivation-section">
                    <div class="motivation-message">
                        Ready to discover your Tennis IQ? Upload a video to get started!
                    </div>
                </div>
            </div>
        `;
    }
    
    setupEventListeners() {
        // Share button
        document.getElementById('shareIQBtn').addEventListener('click', () => {
            this.shareIQ();
        });
        
        // Challenge button
        document.getElementById('challengeBtn').addEventListener('click', () => {
            this.challengeFriends();
        });
        
        // Improve button
        document.getElementById('improveBtn').addEventListener('click', () => {
            this.showImprovementPlan();
        });
    }
    
    async displayTennisIQ(iqData) {
        if (this.isAnimating) return;
        
        this.currentIQ = iqData;
        this.isAnimating = true;
        
        try {
            // Animate main score
            await this.animateMainScore(iqData.components.total_score);
            
            // Update level badge
            this.updateLevelBadge(iqData.components.level);
            
            // Animate component bars
            await this.animateComponentBars(iqData.components);
            
            // Animate pro comparisons
            await this.animateProComparisons(iqData.insights.comparison_to_pros);
            
            // Update insights
            this.updateInsights(iqData.insights);
            
            // Show achievement
            this.showAchievement(iqData.insights.achievement_unlocked);
            
            // Update motivation
            this.updateMotivation(iqData.insights.motivational_message);
            
        } finally {
            this.isAnimating = false;
        }
    }
    
    async animateMainScore(targetScore) {
        const scoreElement = this.container.querySelector('.iq-score-number');
        const currentScore = parseInt(scoreElement.textContent) || 0;
        
        return new Promise((resolve) => {
            let current = currentScore;
            const increment = Math.ceil((targetScore - currentScore) / 50);
            
            const animate = () => {
                if (current < targetScore) {
                    current = Math.min(current + increment, targetScore);
                    scoreElement.textContent = current;
                    scoreElement.style.transform = 'scale(1.1)';
                    setTimeout(() => {
                        scoreElement.style.transform = 'scale(1)';
                    }, 100);
                    setTimeout(animate, this.animationSpeed);
                } else {
                    // Final celebration animation
                    scoreElement.classList.add('score-celebration');
                    setTimeout(() => {
                        scoreElement.classList.remove('score-celebration');
                        resolve();
                    }, 1000);
                }
            };
            
            animate();
        });
    }
    
    updateLevelBadge(level) {
        const iconElement = this.container.querySelector('.level-icon');
        const nameElement = this.container.querySelector('.level-name');
        
        iconElement.textContent = level.value[3]; // Emoji
        nameElement.textContent = level.value[0]; // Name
        
        // Add celebration effect
        const badge = this.container.querySelector('.iq-level-badge');
        badge.classList.add('level-celebration');
        setTimeout(() => {
            badge.classList.remove('level-celebration');
        }, 2000);
    }
    
    async animateComponentBars(components) {
        const componentData = [
            { key: 'technical', score: components.technical_skill },
            { key: 'tactical', score: components.tactical_intelligence },
            { key: 'mental', score: components.mental_toughness },
            { key: 'physical', score: components.physical_attributes },
            { key: 'match', score: components.match_intelligence }
        ];
        
        for (const component of componentData) {
            await this.animateComponentBar(component.key, component.score);
            await new Promise(resolve => setTimeout(resolve, 200)); // Stagger animations
        }
    }
    
    async animateComponentBar(componentKey, targetScore) {
        const bar = this.container.querySelector(`[data-component="${componentKey}"]`);
        const fill = bar.querySelector('.component-fill');
        const scoreSpan = bar.querySelector('.component-score');
        
        return new Promise((resolve) => {
            let currentScore = 0;
            const increment = Math.ceil(targetScore / 30);
            
            const animate = () => {
                if (currentScore < targetScore) {
                    currentScore = Math.min(currentScore + increment, targetScore);
                    const percentage = (currentScore / 200) * 100;
                    
                    fill.style.width = `${percentage}%`;
                    fill.setAttribute('data-score', currentScore);
                    scoreSpan.textContent = `${Math.round(currentScore)}/200`;
                    
                    // Color coding based on score
                    if (currentScore >= 160) {
                        fill.className = 'component-fill excellent';
                    } else if (currentScore >= 120) {
                        fill.className = 'component-fill good';
                    } else if (currentScore >= 80) {
                        fill.className = 'component-fill average';
                    } else {
                        fill.className = 'component-fill needs-work';
                    }
                    
                    setTimeout(animate, 50);
                } else {
                    resolve();
                }
            };
            
            animate();
        });
    }
    
    async animateProComparisons(comparisonData) {
        const pros = ['federer', 'nadal', 'djokovic'];
        const proBenchmarks = {
            federer: 960,
            nadal: 970,
            djokovic: 975
        };
        
        for (const pro of pros) {
            const percentage = (this.currentIQ.components.total_score / proBenchmarks[pro]) * 100;
            await this.animateProBar(pro, percentage);
            await new Promise(resolve => setTimeout(resolve, 300));
        }
    }
    
    async animateProBar(pro, targetPercentage) {
        const comparison = this.container.querySelector(`[data-pro="${pro}"]`);
        const fill = comparison.querySelector('.pro-fill');
        const text = comparison.querySelector('.pro-comparison-text');
        
        return new Promise((resolve) => {
            let currentPercentage = 0;
            const increment = Math.ceil(targetPercentage / 20);
            
            const animate = () => {
                if (currentPercentage < targetPercentage) {
                    currentPercentage = Math.min(currentPercentage + increment, targetPercentage);
                    fill.style.width = `${Math.min(currentPercentage, 100)}%`;
                    fill.setAttribute('data-percentage', currentPercentage);
                    
                    const proName = pro.charAt(0).toUpperCase() + pro.slice(1);
                    text.textContent = `You're ${currentPercentage.toFixed(1)}% of ${proName}'s level`;
                    
                    setTimeout(animate, 100);
                } else {
                    resolve();
                }
            };
            
            animate();
        });
    }
    
    updateInsights(insights) {
        // Update strengths
        const strengthsList = this.container.querySelector('.strengths-list');
        strengthsList.innerHTML = insights.strengths.map(strength => 
            `<li>${strength}</li>`
        ).join('');
        
        // Update weaknesses
        const weaknessesList = this.container.querySelector('.weaknesses-list');
        weaknessesList.innerHTML = insights.weaknesses.map(weakness => 
            `<li>${weakness}</li>`
        ).join('');
        
        // Update improvements
        const improvementsList = this.container.querySelector('.improvement-list');
        improvementsList.innerHTML = insights.improvement_areas.map(improvement => 
            `<li>${improvement}</li>`
        ).join('');
    }
    
    showAchievement(achievement) {
        const achievementBadge = this.container.querySelector('.achievement-badge');
        const achievementText = this.container.querySelector('.achievement-text');
        
        // Extract emoji and text from achievement
        const match = achievement.match(/^(.*?):\s*(.+?)\s*(.+)$/);
        if (match) {
            achievementBadge.textContent = match[3]; // Emoji
            achievementText.textContent = match[2]; // Level name
        } else {
            achievementText.textContent = achievement;
        }
        
        // Celebration animation
        const achievementCard = this.container.querySelector('.achievement-card');
        achievementCard.classList.add('achievement-celebration');
        setTimeout(() => {
            achievementCard.classList.remove('achievement-celebration');
        }, 3000);
    }
    
    updateMotivation(message) {
        const motivationElement = this.container.querySelector('.motivation-message');
        motivationElement.textContent = message;
        
        // Fade in animation
        motivationElement.style.opacity = '0';
        setTimeout(() => {
            motivationElement.style.opacity = '1';
        }, 100);
    }
    
    shareIQ() {
        if (!this.currentIQ) {
            alert('No Tennis IQ data to share!');
            return;
        }
        
        const shareData = {
            title: 'My Tennis IQ Score',
            text: `I just scored ${Math.round(this.currentIQ.components.total_score)} on my Tennis IQ! I'm a ${this.currentIQ.components.level.value[0]} level player. Check out your tennis skills!`,
            url: window.location.href
        };
        
        if (navigator.share) {
            navigator.share(shareData);
        } else {
            // Fallback: copy to clipboard
            navigator.clipboard.writeText(`${shareData.text} ${shareData.url}`);
            this.showNotification('Tennis IQ score copied to clipboard!');
        }
    }
    
    challengeFriends() {
        if (!this.currentIQ) {
            alert('Complete your Tennis IQ assessment first!');
            return;
        }
        
        const challengeText = `I scored ${Math.round(this.currentIQ.components.total_score)} on my Tennis IQ! Can you beat my score? 🎾`;
        
        if (navigator.share) {
            navigator.share({
                title: 'Tennis IQ Challenge',
                text: challengeText,
                url: window.location.href
            });
        } else {
            navigator.clipboard.writeText(`${challengeText} ${window.location.href}`);
            this.showNotification('Challenge copied to clipboard!');
        }
    }
    
    showImprovementPlan() {
        if (!this.currentIQ) {
            alert('Complete your Tennis IQ assessment first!');
            return;
        }
        
        // Create improvement plan modal
        const modal = document.createElement('div');
        modal.className = 'improvement-modal';
        modal.innerHTML = `
            <div class="improvement-modal-content">
                <div class="improvement-header">
                    <h2>🚀 Your Personal Improvement Plan</h2>
                    <button class="close-modal">&times;</button>
                </div>
                <div class="improvement-body">
                    <div class="current-level">
                        <h3>Current Level: ${this.currentIQ.components.level.value[0]} ${this.currentIQ.components.level.value[3]}</h3>
                        <p>Score: ${Math.round(this.currentIQ.components.total_score)}/1000</p>
                    </div>
                    <div class="improvement-areas">
                        <h4>Priority Improvements:</h4>
                        <ul>
                            ${this.currentIQ.insights.improvement_areas.map(area => `<li>${area}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="next-level">
                        <h4>To Reach Next Level:</h4>
                        <ul>
                            ${this.currentIQ.insights.next_level_requirements.map(req => `<li>${req}</li>`).join('')}
                        </ul>
                    </div>
                </div>
                <div class="improvement-actions">
                    <button class="improvement-btn" onclick="this.closest('.improvement-modal').remove()">
                        Got It! Let's Improve
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Close modal functionality
        modal.querySelector('.close-modal').onclick = () => modal.remove();
        modal.onclick = (e) => {
            if (e.target === modal) modal.remove();
        };
    }
    
    showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'iq-notification';
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    reset() {
        this.currentIQ = null;
        
        // Reset score
        this.container.querySelector('.iq-score-number').textContent = '0';
        
        // Reset level badge
        this.container.querySelector('.level-icon').textContent = '🏁';
        this.container.querySelector('.level-name').textContent = 'Just Started';
        
        // Reset component bars
        this.container.querySelectorAll('.component-fill').forEach(fill => {
            fill.style.width = '0%';
            fill.setAttribute('data-score', '0');
        });
        
        this.container.querySelectorAll('.component-score').forEach(score => {
            score.textContent = '0/200';
        });
        
        // Reset pro comparisons
        this.container.querySelectorAll('.pro-fill').forEach(fill => {
            fill.style.width = '0%';
        });
        
        this.container.querySelectorAll('.pro-comparison-text').forEach(text => {
            const proName = text.closest('[data-pro]').getAttribute('data-pro');
            const displayName = proName.charAt(0).toUpperCase() + proName.slice(1);
            text.textContent = `You're 0% of ${displayName}'s level`;
        });
        
        // Reset motivation
        this.container.querySelector('.motivation-message').textContent = 
            'Ready to discover your Tennis IQ? Upload a video to get started!';
    }
}
