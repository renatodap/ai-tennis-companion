/**
 * 🎾 ADVANCED STROKE REPLAY ANIMATION SYSTEM
 * Real-time pose overlay and stroke visualization
 */

class StrokeReplayAnimator {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            width: options.width || 800,
            height: options.height || 600,
            backgroundColor: options.backgroundColor || '#0a0a0f',
            strokeColor: options.strokeColor || '#00d4ff',
            poseColor: options.poseColor || '#ffffff',
            animationSpeed: options.animationSpeed || 1.0,
            showTrajectory: options.showTrajectory !== false,
            showPoseOverlay: options.showPoseOverlay !== false,
            ...options
        };
        
        this.canvas = null;
        this.ctx = null;
        this.animationFrame = null;
        this.isPlaying = false;
        this.currentFrame = 0;
        this.strokeData = null;
        this.poseData = null;
        this.trajectoryPoints = [];
        
        this.init();
    }
    
    init() {
        this.createCanvas();
        this.setupControls();
        this.setupEventListeners();
    }
    
    createCanvas() {
        // Create main container
        const wrapper = document.createElement('div');
        wrapper.className = 'stroke-replay-wrapper';
        wrapper.style.cssText = `
            position: relative;
            background: ${this.options.backgroundColor};
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        `;
        
        // Create canvas
        this.canvas = document.createElement('canvas');
        this.canvas.width = this.options.width;
        this.canvas.height = this.options.height;
        this.canvas.style.cssText = `
            display: block;
            width: 100%;
            height: auto;
        `;
        
        this.ctx = this.canvas.getContext('2d');
        wrapper.appendChild(this.canvas);
        this.container.appendChild(wrapper);
        this.wrapper = wrapper;
    }
    
    setupControls() {
        const controls = document.createElement('div');
        controls.className = 'replay-controls';
        controls.innerHTML = `
            <div class="controls-row">
                <button class="control-btn play-btn" id="playBtn">
                    <span class="play-icon">▶️</span>
                    <span class="pause-icon" style="display: none;">⏸️</span>
                </button>
                <button class="control-btn" id="resetBtn">🔄</button>
                <div class="progress-container">
                    <input type="range" class="progress-slider" id="progressSlider" 
                           min="0" max="100" value="0">
                    <div class="progress-labels">
                        <span class="time-label" id="currentTime">0:00</span>
                        <span class="time-label" id="totalTime">0:00</span>
                    </div>
                </div>
                <div class="speed-control">
                    <label>Speed:</label>
                    <select id="speedSelect">
                        <option value="0.25">0.25x</option>
                        <option value="0.5">0.5x</option>
                        <option value="1" selected>1x</option>
                        <option value="2">2x</option>
                        <option value="4">4x</option>
                    </select>
                </div>
            </div>
            <div class="controls-row">
                <label class="toggle-control">
                    <input type="checkbox" id="showTrajectory" checked>
                    <span>Show Trajectory</span>
                </label>
                <label class="toggle-control">
                    <input type="checkbox" id="showPose" checked>
                    <span>Show Pose</span>
                </label>
                <label class="toggle-control">
                    <input type="checkbox" id="showMetrics" checked>
                    <span>Show Metrics</span>
                </label>
            </div>
        `;
        
        controls.style.cssText = `
            padding: 16px;
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border-top: 1px solid rgba(255,255,255,0.1);
        `;
        
        this.wrapper.appendChild(controls);
        this.controls = controls;
    }
    
    setupEventListeners() {
        const playBtn = this.controls.querySelector('#playBtn');
        const resetBtn = this.controls.querySelector('#resetBtn');
        const progressSlider = this.controls.querySelector('#progressSlider');
        const speedSelect = this.controls.querySelector('#speedSelect');
        const showTrajectory = this.controls.querySelector('#showTrajectory');
        const showPose = this.controls.querySelector('#showPose');
        const showMetrics = this.controls.querySelector('#showMetrics');
        
        playBtn.addEventListener('click', () => this.togglePlayback());
        resetBtn.addEventListener('click', () => this.reset());
        progressSlider.addEventListener('input', (e) => this.seekTo(e.target.value));
        speedSelect.addEventListener('change', (e) => this.setSpeed(parseFloat(e.target.value)));
        showTrajectory.addEventListener('change', (e) => this.toggleTrajectory(e.target.checked));
        showPose.addEventListener('change', (e) => this.togglePose(e.target.checked));
        showMetrics.addEventListener('change', (e) => this.toggleMetrics(e.target.checked));
    }
    
    loadStrokeData(strokeData, poseData = null) {
        this.strokeData = strokeData;
        this.poseData = poseData;
        this.currentFrame = 0;
        this.trajectoryPoints = [];
        
        // Update total time
        if (strokeData && strokeData.duration) {
            const totalTime = this.formatTime(strokeData.duration);
            this.controls.querySelector('#totalTime').textContent = totalTime;
        }
        
        this.render();
    }
    
    togglePlayback() {
        if (this.isPlaying) {
            this.pause();
        } else {
            this.play();
        }
    }
    
    play() {
        if (!this.strokeData) return;
        
        this.isPlaying = true;
        this.updatePlayButton();
        this.animate();
    }
    
    pause() {
        this.isPlaying = false;
        this.updatePlayButton();
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
        }
    }
    
    reset() {
        this.pause();
        this.currentFrame = 0;
        this.trajectoryPoints = [];
        this.updateProgress();
        this.render();
    }
    
    seekTo(percentage) {
        if (!this.strokeData) return;
        
        const totalFrames = this.getTotalFrames();
        this.currentFrame = Math.floor((percentage / 100) * totalFrames);
        this.updateProgress();
        this.render();
    }
    
    setSpeed(speed) {
        this.options.animationSpeed = speed;
    }
    
    toggleTrajectory(show) {
        this.options.showTrajectory = show;
        this.render();
    }
    
    togglePose(show) {
        this.options.showPoseOverlay = show;
        this.render();
    }
    
    toggleMetrics(show) {
        this.options.showMetrics = show;
        this.render();
    }
    
    animate() {
        if (!this.isPlaying) return;
        
        const totalFrames = this.getTotalFrames();
        
        if (this.currentFrame >= totalFrames) {
            this.pause();
            return;
        }
        
        this.currentFrame += this.options.animationSpeed;
        this.updateProgress();
        this.render();
        
        this.animationFrame = requestAnimationFrame(() => this.animate());
    }
    
    render() {
        this.clearCanvas();
        
        if (!this.strokeData) {
            this.drawPlaceholder();
            return;
        }
        
        // Draw stroke visualization
        this.drawStrokeVisualization();
        
        // Draw pose overlay if enabled
        if (this.options.showPoseOverlay && this.poseData) {
            this.drawPoseOverlay();
        }
        
        // Draw trajectory if enabled
        if (this.options.showTrajectory) {
            this.drawTrajectory();
        }
        
        // Draw metrics if enabled
        if (this.options.showMetrics) {
            this.drawMetrics();
        }
        
        // Draw frame indicator
        this.drawFrameIndicator();
    }
    
    clearCanvas() {
        this.ctx.fillStyle = this.options.backgroundColor;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    }
    
    drawPlaceholder() {
        const ctx = this.ctx;
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        
        ctx.fillStyle = 'rgba(255,255,255,0.3)';
        ctx.font = '24px -apple-system, BlinkMacSystemFont, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('🎾 Load stroke data to begin replay', centerX, centerY);
        
        ctx.font = '16px -apple-system, BlinkMacSystemFont, sans-serif';
        ctx.fillStyle = 'rgba(255,255,255,0.5)';
        ctx.fillText('Stroke analysis and pose overlay will appear here', centerX, centerY + 40);
    }
    
    drawStrokeVisualization() {
        const ctx = this.ctx;
        const progress = this.currentFrame / this.getTotalFrames();
        
        // Draw stroke arc/path
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        const radius = 150;
        
        // Stroke path (simplified arc)
        ctx.strokeStyle = this.options.strokeColor;
        ctx.lineWidth = 4;
        ctx.lineCap = 'round';
        
        const startAngle = -Math.PI / 3;
        const endAngle = Math.PI / 3;
        const currentAngle = startAngle + (endAngle - startAngle) * progress;
        
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, startAngle, currentAngle);
        ctx.stroke();
        
        // Racket position
        const racketX = centerX + Math.cos(currentAngle) * radius;
        const racketY = centerY + Math.sin(currentAngle) * radius;
        
        // Draw racket
        this.drawRacket(racketX, racketY, currentAngle);
        
        // Add trajectory point
        if (this.options.showTrajectory) {
            this.trajectoryPoints.push({ x: racketX, y: racketY, time: this.currentFrame });
            
            // Limit trajectory points
            if (this.trajectoryPoints.length > 50) {
                this.trajectoryPoints.shift();
            }
        }
    }
    
    drawRacket(x, y, angle) {
        const ctx = this.ctx;
        
        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(angle);
        
        // Racket head
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.ellipse(0, 0, 25, 15, 0, 0, Math.PI * 2);
        ctx.stroke();
        
        // Racket handle
        ctx.strokeStyle = '#8B4513';
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.moveTo(0, 15);
        ctx.lineTo(0, 40);
        ctx.stroke();
        
        // Strings (simplified)
        ctx.strokeStyle = 'rgba(255,255,255,0.6)';
        ctx.lineWidth = 1;
        for (let i = -20; i <= 20; i += 8) {
            ctx.beginPath();
            ctx.moveTo(i, -12);
            ctx.lineTo(i, 12);
            ctx.stroke();
        }
        
        ctx.restore();
    }
    
    drawPoseOverlay() {
        // Simplified pose overlay - would integrate with actual pose data
        const ctx = this.ctx;
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        
        ctx.strokeStyle = this.options.poseColor;
        ctx.lineWidth = 2;
        ctx.globalAlpha = 0.7;
        
        // Draw simplified skeleton
        const joints = [
            { name: 'head', x: centerX, y: centerY - 100 },
            { name: 'shoulder', x: centerX, y: centerY - 60 },
            { name: 'elbow', x: centerX + 40, y: centerY - 30 },
            { name: 'wrist', x: centerX + 80, y: centerY },
            { name: 'hip', x: centerX, y: centerY + 20 },
            { name: 'knee', x: centerX - 10, y: centerY + 60 },
            { name: 'ankle', x: centerX - 5, y: centerY + 100 }
        ];
        
        // Draw connections
        const connections = [
            ['head', 'shoulder'],
            ['shoulder', 'elbow'],
            ['elbow', 'wrist'],
            ['shoulder', 'hip'],
            ['hip', 'knee'],
            ['knee', 'ankle']
        ];
        
        connections.forEach(([start, end]) => {
            const startJoint = joints.find(j => j.name === start);
            const endJoint = joints.find(j => j.name === end);
            
            ctx.beginPath();
            ctx.moveTo(startJoint.x, startJoint.y);
            ctx.lineTo(endJoint.x, endJoint.y);
            ctx.stroke();
        });
        
        // Draw joints
        joints.forEach(joint => {
            ctx.fillStyle = this.options.poseColor;
            ctx.beginPath();
            ctx.arc(joint.x, joint.y, 4, 0, Math.PI * 2);
            ctx.fill();
        });
        
        ctx.globalAlpha = 1.0;
    }
    
    drawTrajectory() {
        if (this.trajectoryPoints.length < 2) return;
        
        const ctx = this.ctx;
        
        // Draw trajectory trail
        for (let i = 1; i < this.trajectoryPoints.length; i++) {
            const prev = this.trajectoryPoints[i - 1];
            const curr = this.trajectoryPoints[i];
            const alpha = i / this.trajectoryPoints.length;
            
            ctx.strokeStyle = `rgba(0, 212, 255, ${alpha * 0.8})`;
            ctx.lineWidth = 3;
            ctx.lineCap = 'round';
            
            ctx.beginPath();
            ctx.moveTo(prev.x, prev.y);
            ctx.lineTo(curr.x, curr.y);
            ctx.stroke();
        }
    }
    
    drawMetrics() {
        if (!this.strokeData) return;
        
        const ctx = this.ctx;
        const metrics = [
            { label: 'Stroke Type', value: this.strokeData.stroke_type || 'Unknown' },
            { label: 'Speed', value: `${(this.strokeData.swing_speed * 100 || 0).toFixed(1)} km/h` },
            { label: 'Confidence', value: `${(this.strokeData.confidence * 100 || 0).toFixed(0)}%` },
            { label: 'Duration', value: `${(this.strokeData.duration || 0).toFixed(2)}s` }
        ];
        
        // Draw metrics panel
        const panelX = 20;
        const panelY = 20;
        const panelWidth = 200;
        const panelHeight = metrics.length * 25 + 20;
        
        ctx.fillStyle = 'rgba(0,0,0,0.7)';
        ctx.fillRect(panelX, panelY, panelWidth, panelHeight);
        
        ctx.strokeStyle = 'rgba(0,212,255,0.5)';
        ctx.lineWidth = 1;
        ctx.strokeRect(panelX, panelY, panelWidth, panelHeight);
        
        // Draw metrics text
        ctx.fillStyle = '#ffffff';
        ctx.font = '14px -apple-system, BlinkMacSystemFont, sans-serif';
        ctx.textAlign = 'left';
        
        metrics.forEach((metric, index) => {
            const y = panelY + 20 + (index * 25);
            ctx.fillStyle = 'rgba(255,255,255,0.7)';
            ctx.fillText(metric.label + ':', panelX + 10, y);
            ctx.fillStyle = '#00d4ff';
            ctx.fillText(metric.value, panelX + 100, y);
        });
    }
    
    drawFrameIndicator() {
        const ctx = this.ctx;
        const progress = this.currentFrame / this.getTotalFrames();
        
        // Draw progress bar on canvas
        const barWidth = this.canvas.width - 40;
        const barHeight = 4;
        const barX = 20;
        const barY = this.canvas.height - 30;
        
        // Background
        ctx.fillStyle = 'rgba(255,255,255,0.2)';
        ctx.fillRect(barX, barY, barWidth, barHeight);
        
        // Progress
        ctx.fillStyle = '#00d4ff';
        ctx.fillRect(barX, barY, barWidth * progress, barHeight);
        
        // Current time indicator
        const indicatorX = barX + (barWidth * progress);
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(indicatorX, barY + barHeight/2, 6, 0, Math.PI * 2);
        ctx.fill();
    }
    
    updatePlayButton() {
        const playIcon = this.controls.querySelector('.play-icon');
        const pauseIcon = this.controls.querySelector('.pause-icon');
        
        if (this.isPlaying) {
            playIcon.style.display = 'none';
            pauseIcon.style.display = 'inline';
        } else {
            playIcon.style.display = 'inline';
            pauseIcon.style.display = 'none';
        }
    }
    
    updateProgress() {
        const progress = (this.currentFrame / this.getTotalFrames()) * 100;
        const progressSlider = this.controls.querySelector('#progressSlider');
        const currentTimeLabel = this.controls.querySelector('#currentTime');
        
        progressSlider.value = progress;
        
        if (this.strokeData && this.strokeData.duration) {
            const currentTime = (progress / 100) * this.strokeData.duration;
            currentTimeLabel.textContent = this.formatTime(currentTime);
        }
    }
    
    getTotalFrames() {
        return this.strokeData ? (this.strokeData.duration || 3) * 30 : 90; // 30 FPS
    }
    
    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
    
    // Export functionality
    exportAnimation() {
        // This would capture frames and create a GIF/video
        console.log('Export animation functionality would be implemented here');
    }
}

// CSS for controls
const replayStyles = `
    .stroke-replay-wrapper {
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
    }
    
    .replay-controls {
        color: white;
    }
    
    .controls-row {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 12px;
    }
    
    .controls-row:last-child {
        margin-bottom: 0;
    }
    
    .control-btn {
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        color: white;
        padding: 8px 12px;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
        font-size: 16px;
    }
    
    .control-btn:hover {
        background: rgba(255,255,255,0.2);
        border-color: #00d4ff;
    }
    
    .progress-container {
        flex: 1;
        margin: 0 16px;
    }
    
    .progress-slider {
        width: 100%;
        height: 4px;
        background: rgba(255,255,255,0.2);
        border-radius: 2px;
        outline: none;
        -webkit-appearance: none;
    }
    
    .progress-slider::-webkit-slider-thumb {
        -webkit-appearance: none;
        width: 16px;
        height: 16px;
        background: #00d4ff;
        border-radius: 50%;
        cursor: pointer;
    }
    
    .progress-labels {
        display: flex;
        justify-content: space-between;
        margin-top: 4px;
        font-size: 12px;
        opacity: 0.7;
    }
    
    .speed-control {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
    }
    
    .speed-control select {
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
    }
    
    .toggle-control {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
        cursor: pointer;
    }
    
    .toggle-control input[type="checkbox"] {
        accent-color: #00d4ff;
    }
`;

// Inject styles
if (!document.getElementById('replay-styles')) {
    const styleSheet = document.createElement('style');
    styleSheet.id = 'replay-styles';
    styleSheet.textContent = replayStyles;
    document.head.appendChild(styleSheet);
}

// Export for use
window.StrokeReplayAnimator = StrokeReplayAnimator;
