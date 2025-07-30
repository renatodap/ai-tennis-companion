// 🎾 TENNISVIZ PWA JAVASCRIPT - Elite Tennis Analytics
class TennisVizApp {
    constructor() {
        this.selectedFile = null;
        this.sessionType = 'practice';
        this.cameraView = 'side_view';
        this.analysisMode = 'technique';
        this.currentResults = null;
        this.timeline = null;
        this.isPlaying = false;
        
        this.initializeEventListeners();
        this.initializeServiceWorker();
    }
    
    initializeEventListeners() {
        // File upload
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        
        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
        uploadArea.addEventListener('drop', this.handleDrop.bind(this));
        
        fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        
        // Session type buttons
        document.querySelectorAll('.session-btn').forEach(btn => {
            btn.addEventListener('click', this.handleSessionTypeChange.bind(this));
        });
        
        // Analysis options
        document.querySelectorAll('.option-card').forEach(card => {
            card.addEventListener('click', this.handleOptionSelect.bind(this));
        });
        
        // Analyze button
        document.getElementById('analyzeBtn').addEventListener('click', this.startAnalysis.bind(this));
        
        // Timeline controls
        document.getElementById('playBtn').addEventListener('click', this.togglePlayback.bind(this));
        document.getElementById('exportBtn').addEventListener('click', this.exportResults.bind(this));
    }
    
    async initializeServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                await navigator.serviceWorker.register('/sw.js');
                console.log('🎾 Service Worker registered');
            } catch (error) {
                console.log('SW registration failed:', error);
            }
        }
    }
    
    handleDragOver(e) {
        e.preventDefault();
        document.getElementById('uploadArea').classList.add('dragover');
    }
    
    handleDragLeave(e) {
        e.preventDefault();
        document.getElementById('uploadArea').classList.remove('dragover');
    }
    
    handleDrop(e) {
        e.preventDefault();
        document.getElementById('uploadArea').classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.selectFile(files[0]);
        }
    }
    
    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.selectFile(file);
        }
    }
    
    selectFile(file) {
        if (!file.type.startsWith('video/')) {
            this.showNotification('Please select a video file', 'error');
            return;
        }
        
        this.selectedFile = file;
        const fileSize = (file.size / (1024 * 1024)).toFixed(1);
        
        document.getElementById('uploadArea').innerHTML = `
            <div class="upload-icon">✅</div>
            <div class="upload-text">${file.name}</div>
            <div class="upload-subtext">${fileSize}MB • Ready for analysis</div>
        `;
        
        document.getElementById('analyzeBtn').disabled = false;
        this.showNotification('Video loaded successfully!', 'success');
    }
    
    handleSessionTypeChange(e) {
        document.querySelectorAll('.session-btn').forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');
        this.sessionType = e.target.dataset.type;
    }
    
    handleOptionSelect(e) {
        document.querySelectorAll('.option-card').forEach(card => card.classList.remove('selected'));
        e.currentTarget.classList.add('selected');
        
        this.cameraView = e.currentTarget.dataset.view;
        this.analysisMode = e.currentTarget.dataset.mode;
    }
    
    async startAnalysis() {
        if (!this.selectedFile) return;
        
        document.getElementById('loadingOverlay').classList.add('show');
        
        try {
            const formData = new FormData();
            formData.append('video', this.selectedFile);
            formData.append('session_type', this.sessionType);
            formData.append('camera_view', this.cameraView);
            formData.append('analysis_mode', this.analysisMode);
            
            const response = await fetch('/api/analyze-tennisviz', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`Analysis failed: ${response.statusText}`);
            }
            
            const results = await response.json();
            this.currentResults = results;
            this.displayResults(results);
            
            this.showNotification('Analysis complete! 🎾', 'success');
            
        } catch (error) {
            console.error('Analysis failed:', error);
            this.showNotification(`Analysis failed: ${error.message}`, 'error');
        } finally {
            document.getElementById('loadingOverlay').classList.remove('show');
        }
    }
    
    displayResults(results) {
        document.getElementById('resultsSection').classList.add('show');
        
        this.renderTimeline(results.timeline);
        this.renderAnalytics(results.analytics);
        this.renderAIInsights(results.ai_insights);
        
        setTimeout(() => {
            document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
        }, 300);
    }
    
    renderTimeline(timeline) {
        const timelineEl = document.getElementById('timeline');
        timelineEl.innerHTML = '';
        
        if (!timeline || timeline.length === 0) return;
        
        this.timeline = timeline;
        const maxTime = Math.max(...timeline.map(stroke => stroke.end_time));
        
        timeline.forEach((stroke, index) => {
            const marker = document.createElement('div');
            marker.className = `stroke-marker ${stroke.stroke_type.toLowerCase()}`;
            marker.style.left = `${(stroke.start_time / maxTime) * 100}%`;
            marker.title = `${stroke.stroke_type} at ${stroke.start_time.toFixed(1)}s`;
            
            marker.addEventListener('click', () => {
                this.showStrokeDetails(stroke, index);
            });
            
            timelineEl.appendChild(marker);
        });
    }
    
    renderAnalytics(analytics) {
        document.getElementById('totalStrokes').textContent = analytics.total_strokes || 0;
        document.getElementById('sessionDuration').textContent = 
            analytics.processing_time ? `${analytics.processing_time.toFixed(1)}s` : '-';
        
        const strokeDist = analytics.stroke_distribution || {};
        document.getElementById('forehandCount').textContent = strokeDist.forehand || 0;
        document.getElementById('backhandCount').textContent = strokeDist.backhand || 0;
        document.getElementById('serveCount').textContent = strokeDist.serve || 0;
        document.getElementById('volleyCount').textContent = strokeDist.volley || 0;
        
        document.getElementById('avgSwingSpeed').textContent = 
            analytics.average_swing_speed ? analytics.average_swing_speed.toFixed(2) : '-';
        document.getElementById('consistencyScore').textContent = 
            analytics.consistency_score ? `${(analytics.consistency_score * 100).toFixed(0)}%` : '-';
    }
    
    renderAIInsights(aiInsights) {
        document.getElementById('aiSummary').textContent = 
            aiInsights?.ai_summary || 'AI analysis complete. Review your performance metrics above.';
        
        const recommendationsEl = document.getElementById('recommendations');
        recommendationsEl.innerHTML = '';
        
        const recommendations = aiInsights?.coaching_recommendations || [];
        
        if (recommendations.length === 0) {
            recommendationsEl.innerHTML = `
                <div class="recommendation low">
                    <div class="recommendation-title">GREAT JOB!</div>
                    <div class="recommendation-text">No specific issues detected. Keep practicing!</div>
                </div>
            `;
            return;
        }
        
        recommendations.forEach(rec => {
            const recEl = document.createElement('div');
            recEl.className = `recommendation ${rec.priority}`;
            recEl.innerHTML = `
                <div class="recommendation-title">${rec.category.toUpperCase()}: ${rec.insight}</div>
                <div class="recommendation-text">${rec.recommendation}</div>
            `;
            recommendationsEl.appendChild(recEl);
        });
    }
    
    showStrokeDetails(stroke, index) {
        alert(`Stroke #${index + 1}\nType: ${stroke.stroke_type}\nTime: ${stroke.start_time.toFixed(1)}s\nConfidence: ${(stroke.confidence * 100).toFixed(0)}%`);
    }
    
    togglePlayback() {
        if (!this.timeline) return;
        
        const playBtn = document.getElementById('playBtn');
        
        if (this.isPlaying) {
            this.isPlaying = false;
            playBtn.textContent = '▶️ Play';
        } else {
            this.isPlaying = true;
            playBtn.textContent = '⏸️ Pause';
            this.startPlayback();
        }
    }
    
    startPlayback() {
        // Simple playback simulation
        setTimeout(() => {
            if (this.isPlaying) {
                this.togglePlayback();
            }
        }, 5000);
    }
    
    exportResults() {
        if (!this.currentResults) return;
        
        const dataStr = JSON.stringify(this.currentResults, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `tennisviz-analysis-${new Date().toISOString().split('T')[0]}.json`;
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        this.showNotification('Analysis exported! 📤', 'success');
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 1001;
            background: ${type === 'success' ? '#34c759' : type === 'error' ? '#ff3b30' : '#007aff'};
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 3000);
    }
    
    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.tennisVizApp = new TennisVizApp();
});

// Add CSS for notifications and modals
const additionalStyles = `
    .notification {
        animation: slideIn 0.3s ease;
    }
    
    @keyframes slideIn {
        from { transform: translateX(100%); }
        to { transform: translateX(0); }
    }
    
    .metric-value.updated {
        animation: pulse 1s ease;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); color: #007aff; }
    }
    
    .stroke-marker:hover {
        transform: translateY(-50%) scale(1.3) !important;
        z-index: 20 !important;
    }
    
    .recommendation {
        animation: fadeInUp 0.5s ease;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;

// Inject additional styles
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);
