class TennisAI {
    constructor() {
        this.currentVideo = null;
        this.analysisData = null;
        this.isAnalyzing = false;
        
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

        // Back button
        document.getElementById('back-btn').addEventListener('click', () => {
            this.showUploadSection();
        });

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
        await this.analyzeVideo(file);
    }

    async analyzeVideo(file) {
        this.isAnalyzing = true;
        this.showModal('progress-modal');
        
        try {
            // Create FormData
            const formData = new FormData();
            formData.append('file', file);

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

        this.analysisData.timeline.forEach((stroke, index) => {
            const strokeItem = this.createStrokeItem(stroke, index);
            timeline.appendChild(strokeItem);
        });
    }

    createStrokeItem(stroke, index) {
        const item = document.createElement('div');
        item.className = 'stroke-item';
        item.addEventListener('click', () => this.seekToStroke(stroke));

        const strokeType = stroke.stroke.toLowerCase();
        const icon = this.getStrokeIcon(strokeType);
        const color = this.getStrokeColor(strokeType);

        item.innerHTML = `
            <div class="stroke-info">
                <div class="stroke-icon ${strokeType}">
                    ${icon}
                </div>
                <div class="stroke-details">
                    <h4>${this.capitalizeFirst(stroke.stroke)}</h4>
                    <p>Stroke #${index + 1}</p>
                </div>
            </div>
            <div class="stroke-time">
                ${this.formatTime(stroke.start_sec)}
            </div>
        `;

        return item;
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

    showUploadSection() {
        document.getElementById('analysis-section').classList.add('hidden');
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
