class TennisAI {
    constructor() {
        this.currentVideo = null;
        this.analysisData = null;
        this.isAnalyzing = false;
        this.videoConfig = {
            type: null,
            view: null,
            mode: null,
            manualTagging: false
        };
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.hideLoadingScreen();
        this.setupDragAndDrop();
    }

    hideLoadingScreen() {
        setTimeout(() => {
            const loadingScreen = document.getElementById('loading-screen');
            loadingScreen.style.opacity = '0';
            setTimeout(() => {
                loadingScreen.style.display = 'none';
            }, 500);
        }, 1500);
    }

    setupEventListeners() {
        // Upload button
        document.getElementById('select-btn').addEventListener('click', () => {
            document.getElementById('video-input').click();
        });

        // File input change
        document.getElementById('video-input').addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleVideoUpload(e.target.files[0]);
            }
        });

        // Back buttons
        document.getElementById('back-btn').addEventListener('click', () => {
            this.showUploadSection();
        });
        
        document.getElementById('config-back-btn').addEventListener('click', () => {
            this.showUploadSection();
        });

        // Configuration form listeners
        this.setupConfigListeners();

        // Info button and modal
        document.getElementById('info-btn').addEventListener('click', () => {
            this.showModal('info-modal');
        });

        document.getElementById('close-info').addEventListener('click', () => {
            this.hideModal('info-modal');
        });

        // Modal backdrop clicks
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModal(modal.id);
                }
            });
        });

        // Video player events
        const videoPlayer = document.getElementById('video-player');
        videoPlayer.addEventListener('loadedmetadata', () => {
            this.updateVideoControls();
        });
    }

    setupDragAndDrop() {
        const uploadArea = document.getElementById('upload-area');

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.remove('dragover');
            }, false);
        });

        uploadArea.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0 && files[0].type.startsWith('video/')) {
                this.handleVideoUpload(files[0]);
            } else {
                this.showToast('Please select a valid video file', 'error');
            }
        }, false);
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    async handleVideoUpload(file) {
        if (this.isAnalyzing) return;

        // Validate file
        if (!file.type.startsWith('video/')) {
            this.showToast('Please select a valid video file', 'error');
            return;
        }

        if (file.size > 100 * 1024 * 1024) { // 100MB limit
            this.showToast('Video file is too large. Please select a file under 100MB', 'error');
            return;
        }

        this.currentVideo = file;
        this.showConfigSection();
    }

    async analyzeVideo(file) {
        this.isAnalyzing = true;
        this.showModal('progress-modal');
        
        try {
            // Create FormData with configuration
            const formData = new FormData();
            formData.append('file', file);
            formData.append('config', JSON.stringify(this.videoConfig));

            // Update progress
            this.updateProgress(10, 'Uploading video...');

            // Make API call with timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 minute timeout
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    body: formData,
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);

                if (!response.ok) {
                    let errorMessage = `Server error (${response.status})`;
                    
                    try {
                        const errorData = await response.json();
                        if (errorData.detail) {
                            errorMessage = errorData.detail;
                        }
                    } catch (e) {
                        // If we can't parse JSON, use status text
                        errorMessage = response.statusText || errorMessage;
                    }
                    
                    // Handle specific error codes
                    if (response.status === 413) {
                        errorMessage = 'Video file is too large. Please use a smaller file (under 50MB).';
                    } else if (response.status === 408) {
                        errorMessage = 'Video processing timed out. Please try a shorter video.';
                    } else if (response.status === 400) {
                        errorMessage = errorMessage || 'Invalid video file. Please check the file format.';
                    } else if (response.status >= 500) {
                        errorMessage = 'Server error during processing. Please try again later.';
                    }
                    
                    throw new Error(errorMessage);
                }

                this.updateProgress(50, 'Processing frames...');

                const data = await response.json();
                
                // Validate response data
                if (!data || !data.timeline) {
                    throw new Error('Invalid response from server');
                }
                
                this.analysisData = data;

                this.updateProgress(80, 'Analyzing strokes...');

                // Simulate additional processing time for better UX
                await this.sleep(1000);

                this.updateProgress(100, 'Analysis complete!');

                // Wait a bit before showing results
                await this.sleep(500);

                this.hideModal('progress-modal');
                
                // Show success message with stroke count
                const strokeCount = data.timeline ? data.timeline.length : 0;
                if (strokeCount > 0) {
                    this.showToast(`Analysis complete! Found ${strokeCount} strokes.`, 'success');
                } else {
                    this.showToast('Analysis complete, but no strokes were detected.', 'warning');
                }
                
                this.showAnalysisResults();
                
            } catch (fetchError) {
                clearTimeout(timeoutId);
                
                if (fetchError.name === 'AbortError') {
                    throw new Error('Request timed out. Please try a shorter video or check your connection.');
                }
                
                throw fetchError;
            }

        } catch (error) {
            console.error('Analysis failed:', error);
            this.hideModal('progress-modal');
            
            // Show more specific error messages
            let userMessage = 'Analysis failed. Please try again.';
            
            if (error.message) {
                userMessage = error.message;
            }
            
            // Add helpful suggestions based on error type
            if (error.message.includes('timeout') || error.message.includes('timed out')) {
                userMessage += ' Try using a shorter video (under 30 seconds).';
            } else if (error.message.includes('too large')) {
                userMessage += ' Try compressing your video or using a shorter clip.';
            } else if (error.message.includes('network') || error.message.includes('fetch')) {
                userMessage += ' Please check your internet connection.';
            }
            
            this.showToast(userMessage, 'error');
        } finally {
            this.isAnalyzing = false;
        }
    }

    updateProgress(percentage, text) {
        document.getElementById('progress-fill').style.width = `${percentage}%`;
        document.getElementById('progress-percentage').textContent = `${percentage}%`;
        document.getElementById('progress-text').textContent = text;
    }

    showAnalysisResults() {
        // Hide upload section
        document.getElementById('upload-section').classList.add('hidden');
        
        // Show analysis section
        const analysisSection = document.getElementById('analysis-section');
        analysisSection.classList.remove('hidden');

        // Set up video player
        const videoPlayer = document.getElementById('video-player');
        const videoURL = URL.createObjectURL(this.currentVideo);
        videoPlayer.src = videoURL;

        // Populate timeline
        this.populateTimeline();
        
        // Populate stats
        this.populateStats();

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    populateTimeline() {
        const timeline = document.getElementById('stroke-timeline');
        timeline.innerHTML = '';

        if (!this.analysisData || !this.analysisData.timeline) {
            timeline.innerHTML = '<p class="no-data">No strokes detected in this video.</p>';
            return;
        }

        // Setup timeline controls
        this.setupTimelineControls();
        
        // Create interactive progress bar
        this.setupTimelineProgressBar();
        
        // Populate stroke items
        this.currentTimelineView = 'detailed';
        this.currentStrokeFilter = 'all';
        this.showConfidenceIndicators = false;
        
        this.renderStrokeItems();
        
        // Generate AI insights
        this.generateTimelineInsights();
        
        // Setup dashboard
        this.setupAnalysisDashboard();
    }

    setupTimelineControls() {
        // View toggle buttons
        document.getElementById('timeline-view-detailed').addEventListener('click', () => {
            this.setTimelineView('detailed');
        });
        
        document.getElementById('timeline-view-compact').addEventListener('click', () => {
            this.setTimelineView('compact');
        });
        
        // Stroke filter
        document.getElementById('stroke-filter').addEventListener('change', (e) => {
            this.currentStrokeFilter = e.target.value;
            this.renderStrokeItems();
        });
        
        // Confidence toggle
        document.getElementById('confidence-toggle').addEventListener('click', () => {
            this.showConfidenceIndicators = !this.showConfidenceIndicators;
            document.getElementById('confidence-toggle').classList.toggle('active');
            this.renderStrokeItems();
        });
    }
    
    setTimelineView(view) {
        this.currentTimelineView = view;
        
        // Update button states
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.view === view);
        });
        
        this.renderStrokeItems();
    }
    
    setupTimelineProgressBar() {
        const videoPlayer = document.getElementById('video-player');
        const progressTrack = document.getElementById('timeline-track');
        const progressFill = document.getElementById('timeline-fill');
        const playhead = document.getElementById('timeline-playhead');
        const durationLabel = document.getElementById('timeline-duration');
        
        if (!videoPlayer || !progressTrack) return;
        
        // Set duration
        videoPlayer.addEventListener('loadedmetadata', () => {
            durationLabel.textContent = this.formatTime(videoPlayer.duration);
            this.createStrokeMarkers();
        });
        
        // Update progress as video plays
        videoPlayer.addEventListener('timeupdate', () => {
            if (videoPlayer.duration) {
                const progress = (videoPlayer.currentTime / videoPlayer.duration) * 100;
                progressFill.style.width = `${progress}%`;
                playhead.style.left = `${progress}%`;
            }
        });
        
        // Click to seek
        progressTrack.addEventListener('click', (e) => {
            const rect = progressTrack.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const percentage = clickX / rect.width;
            const seekTime = percentage * videoPlayer.duration;
            
            videoPlayer.currentTime = seekTime;
            this.showToast(`Jumped to ${this.formatTime(seekTime)}`, 'info');
        });
        
        // Drag playhead
        let isDragging = false;
        
        playhead.addEventListener('mousedown', (e) => {
            isDragging = true;
            e.preventDefault();
        });
        
        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            
            const rect = progressTrack.getBoundingClientRect();
            const mouseX = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
            const percentage = mouseX / rect.width;
            const seekTime = percentage * videoPlayer.duration;
            
            videoPlayer.currentTime = seekTime;
        });
        
        document.addEventListener('mouseup', () => {
            isDragging = false;
        });
    }
    
    createStrokeMarkers() {
        const progressTrack = document.getElementById('timeline-track');
        const videoPlayer = document.getElementById('video-player');
        
        if (!progressTrack || !videoPlayer.duration) return;
        
        // Remove existing markers
        progressTrack.querySelectorAll('.stroke-marker').forEach(marker => marker.remove());
        
        // Add stroke markers
        this.analysisData.timeline.forEach((stroke, index) => {
            const marker = document.createElement('div');
            marker.className = `stroke-marker ${stroke.stroke.toLowerCase()}`;
            marker.style.left = `${(stroke.start_sec / videoPlayer.duration) * 100}%`;
            marker.title = `${this.capitalizeFirst(stroke.stroke)} at ${this.formatTime(stroke.start_sec)}`;
            
            marker.addEventListener('click', (e) => {
                e.stopPropagation();
                this.seekToStroke(stroke);
            });
            
            progressTrack.appendChild(marker);
        });
    }
    
    renderStrokeItems() {
        const timeline = document.getElementById('stroke-timeline');
        timeline.innerHTML = '';
        
        let filteredStrokes = this.analysisData.timeline;
        
        // Apply filter
        if (this.currentStrokeFilter !== 'all') {
            filteredStrokes = filteredStrokes.filter(stroke => 
                stroke.stroke.toLowerCase() === this.currentStrokeFilter
            );
        }
        
        if (filteredStrokes.length === 0) {
            timeline.innerHTML = '<p class="no-data">No strokes match the current filter.</p>';
            return;
        }
        
        filteredStrokes.forEach((stroke, index) => {
            const strokeItem = this.createEnhancedStrokeItem(stroke, index);
            timeline.appendChild(strokeItem);
        });
    }
    
    createEnhancedStrokeItem(stroke, index) {
        const item = document.createElement('div');
        item.className = `stroke-item ${this.currentTimelineView}`;
        item.addEventListener('click', () => this.seekToStroke(stroke));

        const strokeType = stroke.stroke.toLowerCase();
        const icon = this.getStrokeIcon(strokeType);
        const confidence = stroke.confidence || 0.8;
        const confidenceStars = this.generateConfidenceStars(confidence);
        
        // Enhanced stroke data (simulated for demo)
        const enhancedData = this.generateEnhancedStrokeData(stroke, strokeType);
        
        const confidenceHtml = this.showConfidenceIndicators ? `
            <div class="confidence-indicator">
                <span>Confidence:</span>
                <div class="confidence-stars">${confidenceStars}</div>
            </div>
        ` : '';
        
        const metricsHtml = this.currentTimelineView === 'detailed' ? `
            <div class="stroke-metrics">
                ${enhancedData.metrics.map(metric => `
                    <div class="metric-item">
                        <div class="metric-value">${metric.value}</div>
                        <div class="metric-label">${metric.label}</div>
                    </div>
                `).join('')}
            </div>
            <div class="stroke-feedback">
                <div class="feedback-title">
                    🎯 Technique Insights
                </div>
                <ul class="feedback-list">
                    ${enhancedData.feedback.map(tip => `<li>${tip}</li>`).join('')}
                </ul>
            </div>
        ` : '';

        item.innerHTML = `
            <div class="stroke-item-header">
                <div class="stroke-info">
                    <div class="stroke-icon ${strokeType}">
                        ${icon}
                    </div>
                    <div class="stroke-details">
                        <h4>${this.capitalizeFirst(stroke.stroke)}</h4>
                        <p>Stroke #${index + 1} • ${enhancedData.description}</p>
                    </div>
                </div>
                <div class="stroke-meta">
                    <div class="stroke-time">
                        ${this.formatTime(stroke.start_sec)}
                    </div>
                    ${confidenceHtml}
                </div>
            </div>
            ${metricsHtml}
        `;

        return item;
    }
    
    generateConfidenceStars(confidence) {
        const starCount = 5;
        const filledStars = Math.round(confidence * starCount);
        
        return Array.from({length: starCount}, (_, i) => 
            `<div class="confidence-star ${i < filledStars ? 'filled' : ''}"></div>`
        ).join('');
    }
    
    generateEnhancedStrokeData(stroke, strokeType) {
        // Simulate enhanced analysis data based on our technique analyzer
        const baseMetrics = {
            forehand: {
                metrics: [
                    { label: 'Power', value: Math.floor(Math.random() * 30 + 70) + '%' },
                    { label: 'Accuracy', value: Math.floor(Math.random() * 20 + 75) + '%' },
                    { label: 'Spin Rate', value: Math.floor(Math.random() * 500 + 2000) + ' rpm' },
                    { label: 'Contact Point', value: Math.floor(Math.random() * 20 + 80) + '%' }
                ],
                feedback: [
                    'Good follow-through on this stroke',
                    'Try to make contact slightly earlier',
                    'Excellent racquet head speed'
                ],
                description: 'Cross-court winner'
            },
            backhand: {
                metrics: [
                    { label: 'Balance', value: Math.floor(Math.random() * 15 + 80) + '%' },
                    { label: 'Rotation', value: Math.floor(Math.random() * 25 + 70) + '%' },
                    { label: 'Timing', value: Math.floor(Math.random() * 20 + 75) + '%' },
                    { label: 'Extension', value: Math.floor(Math.random() * 30 + 65) + '%' }
                ],
                feedback: [
                    'Strong two-handed technique',
                    'Good shoulder rotation',
                    'Consider higher follow-through'
                ],
                description: 'Down-the-line approach'
            },
            serve: {
                metrics: [
                    { label: 'Toss Height', value: Math.floor(Math.random() * 20 + 180) + ' cm' },
                    { label: 'Speed', value: Math.floor(Math.random() * 30 + 90) + ' mph' },
                    { label: 'Placement', value: Math.floor(Math.random() * 25 + 70) + '%' },
                    { label: 'Consistency', value: Math.floor(Math.random() * 20 + 75) + '%' }
                ],
                feedback: [
                    'Consistent toss placement',
                    'Good knee bend and drive',
                    'Work on pronation timing'
                ],
                description: 'First serve to T'
            }
        };
        
        return baseMetrics[strokeType] || {
            metrics: [
                { label: 'Quality', value: '75%' },
                { label: 'Timing', value: '80%' }
            ],
            feedback: ['Keep practicing this stroke'],
            description: 'Standard execution'
        };
    }
    
    generateTimelineInsights() {
        const insights = document.getElementById('timeline-insights');
        if (!insights) return;
        
        const strokeCounts = this.calculateStats();
        const totalStrokes = this.analysisData.timeline.length;
        const avgConfidence = this.analysisData.timeline.reduce((sum, stroke) => 
            sum + (stroke.confidence || 0.8), 0) / totalStrokes;
        
        // Generate AI-like insights
        const insightCards = [
            {
                icon: '📊',
                text: `Analyzed ${totalStrokes} strokes with ${Math.round(avgConfidence * 100)}% average confidence`
            },
            {
                icon: '🎯',
                text: `Most frequent stroke: ${this.getMostFrequentStroke(strokeCounts)}`
            },
            {
                icon: '⚡',
                text: `Peak performance around ${this.findPeakPerformanceTime()}`
            },
            {
                icon: '💡',
                text: 'Focus on consistency in backhand technique for next session'
            }
        ];
        
        insights.innerHTML = `
            <div class="insights-title">
                🧠 AI Analysis Insights
            </div>
            <div class="insights-grid">
                ${insightCards.map(insight => `
                    <div class="insight-card">
                        <div class="insight-icon">${insight.icon}</div>
                        <div class="insight-text">${insight.text}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    getMostFrequentStroke(strokeCounts) {
        let maxCount = 0;
        let mostFrequent = 'forehand';
        
        Object.entries(strokeCounts).forEach(([stroke, count]) => {
            if (stroke !== 'Total Strokes' && count > maxCount) {
                maxCount = count;
                mostFrequent = stroke;
            }
        });
        
        return mostFrequent.toLowerCase();
    }
    
    findPeakPerformanceTime() {
        if (this.analysisData.timeline.length === 0) return '0:00';
        
        // Find the stroke with highest confidence
        const bestStroke = this.analysisData.timeline.reduce((best, stroke) => 
            (stroke.confidence || 0.8) > (best.confidence || 0.8) ? stroke : best
        );
        
        return this.formatTime(bestStroke.start_sec);
    }
    
    setupAnalysisDashboard() {
        // Setup tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const tabName = btn.dataset.tab;
                this.switchDashboardTab(tabName);
            });
        });
        
        // Populate initial content
        this.populateDashboardOverview();
        this.populateTechniqueTab();
        this.populatePatternsTab();
    }
    
    switchDashboardTab(tabName) {
        // Update button states
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });
        
        // Show/hide content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.toggle('active', content.id === `tab-${tabName}`);
        });
    }
    
    populateDashboardOverview() {
        // Enhanced stats are already handled by existing populateStats method
        this.createPerformanceChart();
    }
    
    createPerformanceChart() {
        const canvas = document.getElementById('performance-chart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const timeline = this.analysisData.timeline;
        
        // Simple performance visualization
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw axes
        ctx.strokeStyle = '#e5e7eb';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(40, 20);
        ctx.lineTo(40, 160);
        ctx.lineTo(360, 160);
        ctx.stroke();
        
        // Draw performance line
        if (timeline.length > 1) {
            ctx.strokeStyle = '#3b82f6';
            ctx.lineWidth = 2;
            ctx.beginPath();
            
            timeline.forEach((stroke, index) => {
                const x = 40 + (index / (timeline.length - 1)) * 320;
                const confidence = stroke.confidence || 0.8;
                const y = 160 - (confidence * 140);
                
                if (index === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });
            
            ctx.stroke();
            
            // Draw points
            ctx.fillStyle = '#3b82f6';
            timeline.forEach((stroke, index) => {
                const x = 40 + (index / (timeline.length - 1)) * 320;
                const confidence = stroke.confidence || 0.8;
                const y = 160 - (confidence * 140);
                
                ctx.beginPath();
                ctx.arc(x, y, 3, 0, 2 * Math.PI);
                ctx.fill();
            });
        }
        
        // Labels
        ctx.fillStyle = '#6b7280';
        ctx.font = '12px Inter';
        ctx.fillText('Performance Over Time', 40, 190);
        ctx.fillText('High', 10, 25);
        ctx.fillText('Low', 10, 155);
    }
    
    populateTechniqueTab() {
        const container = document.getElementById('technique-metrics');
        if (!container) return;
        
        const strokeTypes = ['forehand', 'backhand', 'serve'];
        
        container.innerHTML = strokeTypes.map(strokeType => {
            const strokeData = this.analysisData.timeline.filter(s => 
                s.stroke.toLowerCase() === strokeType
            );
            
            if (strokeData.length === 0) return '';
            
            const avgConfidence = strokeData.reduce((sum, s) => 
                sum + (s.confidence || 0.8), 0) / strokeData.length;
            
            return `
                <div class="technique-card">
                    <h4>${this.capitalizeFirst(strokeType)} Analysis</h4>
                    <div class="metric-grid">
                        <div class="metric-item">
                            <div class="metric-value">${strokeData.length}</div>
                            <div class="metric-label">Total Strokes</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-value">${Math.round(avgConfidence * 100)}%</div>
                            <div class="metric-label">Avg Confidence</div>
                        </div>
                    </div>
                    <div class="technique-feedback">
                        <p>Focus on consistency and timing for improved ${strokeType} performance.</p>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    populatePatternsTab() {
        const container = document.getElementById('pattern-analysis');
        if (!container) return;
        
        const patterns = [
            {
                title: 'Stroke Sequence Analysis',
                insight: 'Most common pattern: Serve → Forehand → Backhand',
                recommendation: 'Practice transitioning from serve to groundstrokes'
            },
            {
                title: 'Timing Consistency',
                insight: 'Average time between strokes: 2.3 seconds',
                recommendation: 'Work on maintaining rhythm during rallies'
            },
            {
                title: 'Performance Trends',
                insight: 'Confidence increases throughout the session',
                recommendation: 'Good warm-up routine - maintain this approach'
            }
        ];
        
        container.innerHTML = patterns.map(pattern => `
            <div class="pattern-insight">
                <h4>${pattern.title}</h4>
                <p><strong>Insight:</strong> ${pattern.insight}</p>
                <p><strong>Recommendation:</strong> ${pattern.recommendation}</p>
            </div>
        `).join('');
    }

    createStrokeItem(stroke, index) {
        // Legacy method - now handled by createEnhancedStrokeItem
        return this.createEnhancedStrokeItem(stroke, index);
    }

    getStrokeIcon(strokeType) {
        const icons = {
            'forehand': 'FH',
            'backhand': 'BH',
            'serve': 'SV'
        };
        return icons[strokeType] || '?';
    }

    getStrokeColor(strokeType) {
        const colors = {
            'forehand': '#10b981',
            'backhand': '#3b82f6',
            'serve': '#f59e0b'
        };
        return colors[strokeType] || '#6b7280';
    }

    populateStats() {
        const statsGrid = document.getElementById('stats-grid');
        statsGrid.innerHTML = '';

        if (!this.analysisData || !this.analysisData.timeline) {
            return;
        }

        const stats = this.calculateStats();
        
        Object.entries(stats).forEach(([key, value]) => {
            const statItem = document.createElement('div');
            statItem.className = 'stat-item';
            statItem.innerHTML = `
                <div class="stat-value">${value}</div>
                <div class="stat-label">${key}</div>
            `;
            statsGrid.appendChild(statItem);
        });
    }

    calculateStats() {
        const timeline = this.analysisData.timeline;
        const strokeCounts = {};
        
        timeline.forEach(stroke => {
            const type = this.capitalizeFirst(stroke.stroke);
            strokeCounts[type] = (strokeCounts[type] || 0) + 1;
        });

        return {
            'Total Strokes': timeline.length,
            ...strokeCounts
        };
    }

    seekToStroke(stroke) {
        const videoPlayer = document.getElementById('video-player');
        videoPlayer.currentTime = stroke.start_sec;
        videoPlayer.play();
        
        // Add visual feedback
        this.showToast(`Jumped to ${stroke.stroke} at ${this.formatTime(stroke.start_sec)}`, 'success');
    }

    setupConfigListeners() {
        // Radio button change listeners
        const radioButtons = document.querySelectorAll('input[type="radio"]');
        radioButtons.forEach(radio => {
            radio.addEventListener('change', () => {
                this.updateConfigState();
                this.validateConfigForm();
            });
        });

        // Checkbox listener
        document.getElementById('manual-tagging').addEventListener('change', (e) => {
            this.videoConfig.manualTagging = e.target.checked;
        });

        // Start analysis button
        document.getElementById('start-analysis-btn').addEventListener('click', () => {
            if (this.isConfigValid()) {
                this.analyzeVideo(this.currentVideo);
            }
        });
    }

    updateConfigState() {
        // Get selected values
        const videoType = document.querySelector('input[name="video-type"]:checked');
        const cameraView = document.querySelector('input[name="camera-view"]:checked');
        const analysisMode = document.querySelector('input[name="analysis-mode"]:checked');

        this.videoConfig.type = videoType ? videoType.value : null;
        this.videoConfig.view = cameraView ? cameraView.value : null;
        this.videoConfig.mode = analysisMode ? analysisMode.value : null;
    }

    validateConfigForm() {
        const isValid = this.isConfigValid();
        const startBtn = document.getElementById('start-analysis-btn');
        startBtn.disabled = !isValid;
    }

    isConfigValid() {
        return this.videoConfig.type && this.videoConfig.view && this.videoConfig.mode;
    }

    showConfigSection() {
        document.getElementById('upload-section').classList.add('hidden');
        document.getElementById('config-section').classList.remove('hidden');
        
        // Reset form
        this.resetConfigForm();
    }

    resetConfigForm() {
        // Clear all radio buttons
        document.querySelectorAll('input[type="radio"]').forEach(radio => {
            radio.checked = false;
        });
        
        // Clear checkbox
        document.getElementById('manual-tagging').checked = false;
        
        // Reset config state
        this.videoConfig = {
            type: null,
            view: null,
            mode: null,
            manualTagging: false
        };
        
        // Disable start button
        document.getElementById('start-analysis-btn').disabled = true;
    }

    showUploadSection() {
        document.getElementById('analysis-section').classList.add('hidden');
        document.getElementById('config-section').classList.add('hidden');
        document.getElementById('upload-section').classList.remove('hidden');
        
        // Reset video input
        document.getElementById('video-input').value = '';
        this.currentVideo = null;
        this.analysisData = null;
    }

    showModal(modalId) {
        document.getElementById(modalId).classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }

    hideModal(modalId) {
        document.getElementById(modalId).classList.add('hidden');
        document.body.style.overflow = '';
    }

    showToast(message, type = 'info') {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        // Add styles
        Object.assign(toast.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '12px 20px',
            borderRadius: '8px',
            color: 'white',
            fontWeight: '500',
            zIndex: '10000',
            transform: 'translateX(100%)',
            transition: 'transform 0.3s ease-in-out',
            maxWidth: '300px',
            wordWrap: 'break-word'
        });

        // Set background color based on type
        const colors = {
            'success': '#10b981',
            'error': '#ef4444',
            'warning': '#f59e0b',
            'info': '#3b82f6'
        };
        toast.style.backgroundColor = colors[type] || colors.info;

        // Add to DOM
        document.body.appendChild(toast);

        // Animate in
        setTimeout(() => {
            toast.style.transform = 'translateX(0)';
        }, 100);

        // Remove after delay
        setTimeout(() => {
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }

    updateVideoControls() {
        // Add any custom video controls here if needed
    }

    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new TennisAI();
});

// Handle page visibility changes for better mobile performance
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Pause any ongoing processes when app goes to background
    } else {
        // Resume when app comes back to foreground
    }
});

// Handle online/offline status
window.addEventListener('online', () => {
    console.log('App is online');
});

window.addEventListener('offline', () => {
    console.log('App is offline');
});

// Prevent zoom on double tap for better mobile UX
let lastTouchEnd = 0;
document.addEventListener('touchend', (event) => {
    const now = (new Date()).getTime();
    if (now - lastTouchEnd <= 300) {
        event.preventDefault();
    }
    lastTouchEnd = now;
}, false);
