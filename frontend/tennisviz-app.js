// 🎾 TENNISVIZ PWA// TennisViz PWA - Enhanced Tennis Analytics
class TennisVizApp {
    constructor() {
        this.currentAnalysis = null;
        this.isAnalyzing = false;
        this.advancedMode = false;
        
        // Initialize advanced components
        this.heatmapVisualizer = new TennisCourtHeatmap('heatmapCanvas');
        this.strokeReplayAnimator = new StrokeReplayAnimator('replayCanvas');
        this.patternSearchEngine = new TennisPatternSearchEngine('patternSearchContainer');
        this.tennisIQDisplay = new TennisIQDisplay('tennisIQDisplay');
        this.selectedFile = null;
        this.sessionType = 'practice';
        this.cameraView = 'side_view';
        this.analysisMode = 'technique';
        this.currentResults = null;
        this.timeline = null;
        this.isPlaying = false;
        
        this.init();
    }
    
    init() {
        this.initializeEventListeners();
        this.initializeServiceWorker();
    }
    
    initializeEventListeners() {
        // Wait for DOM to be fully loaded before setting up event listeners
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupFileUploadListeners());
        } else {
            this.setupFileUploadListeners();
        }
        
        this.setupOtherListeners();
    }
    
    setupFileUploadListeners() {
        // File upload
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('videoInput');
        
        console.log('Setting up file upload listeners:', { uploadArea, fileInput });
        
        if (uploadArea && fileInput) {
            uploadArea.addEventListener('click', () => {
                console.log('Upload area clicked, triggering file input');
                fileInput.click();
            });
            uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
            uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
            uploadArea.addEventListener('drop', this.handleDrop.bind(this));
            
            fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        } else {
            console.error('Upload elements not found:', { uploadArea, fileInput });
        }
    }
    
    setupOtherListeners() {
        
        // Session type buttons (using radio buttons instead of .session-btn)
        document.querySelectorAll('input[name="sessionType"]').forEach(radio => {
            radio.addEventListener('change', this.handleSessionTypeChange.bind(this));
        });
        
        // Camera view options
        document.querySelectorAll('input[name="cameraView"]').forEach(radio => {
            radio.addEventListener('change', this.handleOptionSelect.bind(this));
        });
        
        // Analysis mode options
        document.querySelectorAll('input[name="analysisMode"]').forEach(radio => {
            radio.addEventListener('change', this.handleOptionSelect.bind(this));
        });
        
        // Analyze button
        const analyzeBtn = document.getElementById('analyzeBtn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', this.startAnalysis.bind(this));
        }
        
        // Export button
        const exportBtn = document.getElementById('exportBtn');
        if (exportBtn) {
            exportBtn.addEventListener('click', this.exportResults.bind(this));
        }
        
        // Advanced analytics toggle
        const advancedToggleBtn = document.getElementById('advancedToggleBtn');
        if (advancedToggleBtn) {
            advancedToggleBtn.addEventListener('click', this.toggleAdvancedAnalytics.bind(this));
        }
        
        // Initialize advanced components when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.initializeAdvancedComponents();
            });
        } else {
            this.initializeAdvancedComponents();
        }
        
        // Listen for search results
        document.addEventListener('tennisSearchResults', this.handleSearchResults.bind(this));
        
        // Timeline controls
        const playBtn = document.getElementById('playBtn');
        if (playBtn) {
            playBtn.addEventListener('click', this.togglePlayback.bind(this));
        }
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
        console.log('File selected:', file);
        if (file) {
            this.selectFile(file);
        }
    }
    
    selectFile(file) {
        console.log('selectFile called with:', file);
        
        if (!file || !file.type.startsWith('video/')) {
            this.showNotification('Please select a valid video file', 'error');
            return;
        }
        
        this.selectedFile = file;
        console.log('File stored:', this.selectedFile);
        
        // Update UI with retry logic
        this.updateUploadUI(file);
        
        // Show upload success notification
        this.showNotification('Video uploaded! Starting analysis...', 'success');
        
        // Automatically start analysis after a brief delay to show the upload success
        setTimeout(() => {
            this.startAnalysis();
        }, 1000);
    }
    
    updateUploadUI(file) {
        // Retry finding elements if not found initially
        const maxRetries = 5;
        let retryCount = 0;
        
        const updateElements = () => {
            const uploadText = document.querySelector('.upload-text');
            const uploadHint = document.querySelector('.upload-hint');
            const analyzeBtn = document.getElementById('analyzeBtn');
            const uploadArea = document.getElementById('uploadArea');
            
            console.log('UI elements found (attempt ' + (retryCount + 1) + '):', { uploadText, uploadHint, analyzeBtn, uploadArea });
            
            if (uploadText && uploadHint && analyzeBtn) {
                // Update upload area appearance
                if (uploadArea) {
                    uploadArea.style.background = 'linear-gradient(135deg, #34c759, #28a745)';
                    uploadArea.style.borderColor = '#34c759';
                    uploadArea.style.color = 'white';
                }
                
                // Update text content
                uploadText.textContent = `✅ ${file.name}`;
                uploadHint.textContent = `${(file.size / 1024 / 1024).toFixed(1)} MB • Analysis starting...`;
                
                // Hide the analyze button since analysis starts automatically
                analyzeBtn.style.display = 'none';
                
                console.log('UI successfully updated for auto-analysis!');
                return true;
            } else {
                console.warn('Some UI elements not found, retrying...');
                return false;
            }
        };
        
        // Try immediately
        if (updateElements()) {
            return;
        }
        
        // Retry with delays if initial attempt failed
        const retryUpdate = () => {
            retryCount++;
            if (retryCount < maxRetries) {
                setTimeout(() => {
                    if (!updateElements()) {
                        retryUpdate();
                    }
                }, 100 * retryCount); // Increasing delay
            } else {
                console.error('Failed to update UI after', maxRetries, 'attempts');
            }
        };
        
        retryUpdate();
    }
    
    handleSessionTypeChange(e) {
        this.sessionType = e.target.value;
        console.log('Session type changed to:', this.sessionType);
    }
    
    handleOptionSelect(e) {
        const name = e.target.name;
        const value = e.target.value;
        
        if (name === 'cameraView') {
            this.cameraView = value;
            console.log('Camera view changed to:', this.cameraView);
        } else if (name === 'analysisMode') {
            this.analysisMode = value;
            console.log('Analysis mode changed to:', this.analysisMode);
        }
    }
    
    async startAnalysis() {
        if (!this.selectedFile) {
            this.showNotification('Please select a video file first!', 'error');
            return;
        }
        
        console.log('🎾 Starting automatic analysis with file:', this.selectedFile.name);
        
        // Update upload area to show analysis in progress
        const uploadHint = document.querySelector('.upload-hint');
        if (uploadHint) {
            uploadHint.textContent = `${(this.selectedFile.size / 1024 / 1024).toFixed(1)} MB • Analyzing video...`;
        }
        
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'flex';
        }
        
        // Update loading text
        const loadingProgress = document.getElementById('loadingProgress');
        if (loadingProgress) {
            loadingProgress.textContent = 'Processing your tennis video...';
        }
        
        try {
            // Step 1: Upload the video file
            console.log('📤 Uploading video...');
            const formData = new FormData();
            formData.append('file', this.selectedFile);  // Changed from 'video' to 'file'
            formData.append('session_type', this.sessionType);
            formData.append('camera_view', this.cameraView);
            formData.append('analysis_mode', this.analysisMode);
            
            const uploadResponse = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            console.log('📤 Upload response status:', uploadResponse.status);
            
            if (!uploadResponse.ok) {
                throw new Error(`Upload failed: ${uploadResponse.status} ${uploadResponse.statusText}`);
            }
            
            const uploadResults = await uploadResponse.json();
            console.log('✅ Upload successful:', uploadResults);
            
            // Step 2: Start analysis (optional separate call)
            console.log('🔍 Starting analysis...');
            
            // For now, use the upload results directly since our local server
            // returns mock analysis data in the upload response
            this.currentResults = uploadResults;
            this.displayResults(uploadResults);
            
            this.showNotification('Analysis complete! 🎾', 'success');
            
        } catch (error) {
            console.error('❌ Analysis failed:', error);
            this.showNotification(`Analysis failed: ${error.message}`, 'error');
        } finally {
            if (loadingOverlay) {
                loadingOverlay.style.display = 'none';
            }
        }
    }
    
    displayResults(results) {
        document.getElementById('resultsSection').classList.add('show');
        
        this.renderTimeline(results.timeline);
        this.renderAnalytics(results.analytics);
        this.renderAIInsights(results.ai_insights);
        
        // Display Tennis IQ Score - The Game Changer!
        if (results.tennis_iq) {
            this.tennisIQDisplay.displayTennisIQ(results.tennis_iq);
            document.getElementById('tennisIQSection').classList.add('show');
        }
        
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
        if (!this.currentResults) {
            this.showNotification('No analysis results to export', 'warning');
            return;
        }
        
        const dataStr = JSON.stringify(this.currentResults, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `tennis-analysis-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        
        this.showNotification('Analysis results exported successfully!', 'success');
    }
    
    // Advanced Analytics Methods
    initializeAdvancedComponents() {
        // Initialize Pattern Search Engine
        this.patternSearchEngine = new TennisPatternSearchEngine();
        const searchContainer = document.getElementById('patternSearchContainer');
        if (searchContainer) {
            searchContainer.appendChild(this.patternSearchEngine.createSearchInterface());
            this.patternSearchEngine.bindEvents();
        }
        
        // Initialize Heatmap Visualizer
        const heatmapContainer = document.getElementById('courtHeatmap');
        if (heatmapContainer) {
            this.heatmapVisualizer = new TennisCourtHeatmap('courtHeatmap', {
                width: 400,
                height: 600
            });
            
            // Setup heatmap controls
            this.setupHeatmapControls();
        }
        
        // Initialize Stroke Replay Animator
        const replayContainer = document.getElementById('strokeReplayContainer');
        if (replayContainer) {
            this.strokeReplayAnimator = new StrokeReplayAnimator('strokeReplayContainer', {
                width: 800,
                height: 500
            });
            
            // Setup replay controls
            this.setupReplayControls();
        }
    }
    
    toggleAdvancedAnalytics() {
        this.advancedMode = !this.advancedMode;
        const advancedSection = document.getElementById('advancedAnalytics');
        const toggleBtn = document.getElementById('advancedToggleBtn');
        
        if (this.advancedMode) {
            advancedSection.style.display = 'block';
            toggleBtn.textContent = '✅ Advanced Analytics Active';
            toggleBtn.classList.add('active');
            
            // Load data into advanced components if analysis exists
            if (this.currentResults) {
                this.loadAdvancedAnalytics(this.currentResults);
            }
            
            this.showNotification('🚀 Advanced analytics unlocked!', 'success');
        } else {
            advancedSection.style.display = 'none';
            toggleBtn.textContent = '🚀 Unlock Advanced Analytics';
            toggleBtn.classList.remove('active');
        }
    }
    
    setupHeatmapControls() {
        const filterSelect = document.getElementById('heatmapFilter');
        const zoneBtn = document.getElementById('heatmapZoneBtn');
        const exportBtn = document.getElementById('heatmapExportBtn');
        
        if (filterSelect) {
            filterSelect.addEventListener('change', (e) => {
                this.filterHeatmapData(e.target.value);
            });
        }
        
        if (zoneBtn) {
            zoneBtn.addEventListener('click', () => {
                this.analyzeSelectedZone();
            });
        }
        
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                if (this.heatmapVisualizer) {
                    this.heatmapVisualizer.exportAsImage();
                }
            });
        }
        
        // Setup heatmap zone selection callback
        if (this.heatmapVisualizer) {
            this.heatmapVisualizer.onZoneSelected = (zone) => {
                this.displayZoneAnalysis(zone);
            };
        }
    }
    
    setupReplayControls() {
        const strokeSelector = document.getElementById('strokeSelector');
        
        if (strokeSelector) {
            strokeSelector.addEventListener('change', (e) => {
                const strokeIndex = parseInt(e.target.value);
                if (!isNaN(strokeIndex) && this.currentResults) {
                    const stroke = this.currentResults.stroke_events[strokeIndex];
                    if (stroke && this.strokeReplayAnimator) {
                        this.strokeReplayAnimator.loadStrokeData(stroke);
                    }
                }
            });
        }
    }
    
    loadAdvancedAnalytics(results) {
        // Load data into pattern search engine
        if (this.patternSearchEngine) {
            this.patternSearchEngine.loadData(
                results.stroke_events || [],
                results.analytics?.rally_analysis?.rallies || []
            );
        }
        
        // Load heatmap data
        if (this.heatmapVisualizer && results.analytics?.heatmap_analysis) {
            const heatmapData = this.convertToHeatmapFormat(results.analytics.heatmap_analysis);
            this.heatmapVisualizer.updateHeatmap(heatmapData);
        }
        
        // Populate stroke selector
        this.populateStrokeSelector(results.stroke_events || []);
        
        // Update pattern analysis cards
        this.updatePatternAnalysisCards(results);
    }
    
    convertToHeatmapFormat(heatmapAnalysis) {
        // Convert backend heatmap data to frontend format
        const positions = heatmapAnalysis.positions || [];
        return positions.map(pos => ({
            x: pos.x || 0.5,
            y: pos.y || 0.8,
            intensity: pos.intensity || 1,
            strokeCount: pos.stroke_count || 1,
            zone: pos.zone || 'unknown'
        }));
    }
    
    populateStrokeSelector(strokeEvents) {
        const selector = document.getElementById('strokeSelector');
        if (!selector) return;
        
        selector.innerHTML = '<option value="">Choose a stroke...</option>';
        
        strokeEvents.forEach((stroke, index) => {
            const option = document.createElement('option');
            option.value = index;
            option.textContent = `${stroke.stroke_type} at ${stroke.contact_time.toFixed(1)}s (${(stroke.confidence * 100).toFixed(0)}%)`;
            selector.appendChild(option);
        });
    }
    
    filterHeatmapData(strokeType) {
        if (!this.heatmapVisualizer || !this.currentResults) return;
        
        let filteredEvents = this.currentResults.stroke_events || [];
        
        if (strokeType !== 'all') {
            filteredEvents = filteredEvents.filter(stroke => 
                stroke.stroke_type === strokeType
            );
        }
        
        // Convert to heatmap format and update
        const heatmapData = filteredEvents.map(stroke => ({
            x: stroke.player_position?.[0] || 0.5,
            y: stroke.player_position?.[1] || 0.8,
            intensity: stroke.confidence || 0.5,
            strokeCount: 1,
            zone: stroke.court_zone || 'unknown'
        }));
        
        this.heatmapVisualizer.animateHeatmapUpdate(heatmapData);
    }
    
    handleSearchResults(event) {
        const { type, data, visualizations } = event.detail;
        
        // Handle different types of search results
        if (visualizations.includes('heatmap') && this.heatmapVisualizer) {
            // Update heatmap with search results
            if (data.positions) {
                this.heatmapVisualizer.updateHeatmap(data.positions);
            }
        }
        
        if (visualizations.includes('timeline') && data.strokes) {
            // Highlight strokes on timeline
            this.highlightTimelineStrokes(data.strokes);
        }
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
