/**
 * 🔥 INTERACTIVE TENNIS COURT HEATMAP VISUALIZER
 * Advanced court positioning and movement pattern visualization
 */

class TennisCourtHeatmap {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            width: options.width || 400,
            height: options.height || 600,
            courtColor: options.courtColor || '#2d5a27',
            lineColor: options.lineColor || '#ffffff',
            heatmapOpacity: options.heatmapOpacity || 0.7,
            ...options
        };
        
        this.canvas = null;
        this.ctx = null;
        this.heatmapData = [];
        this.selectedZone = null;
        
        this.init();
    }
    
    init() {
        this.createCanvas();
        this.setupEventListeners();
        this.drawCourt();
    }
    
    createCanvas() {
        this.canvas = document.createElement('canvas');
        this.canvas.width = this.options.width;
        this.canvas.height = this.options.height;
        this.canvas.style.cursor = 'pointer';
        this.canvas.style.borderRadius = '12px';
        this.canvas.style.boxShadow = '0 4px 20px rgba(0,0,0,0.1)';
        
        this.ctx = this.canvas.getContext('2d');
        this.container.appendChild(this.canvas);
    }
    
    setupEventListeners() {
        this.canvas.addEventListener('click', (e) => this.handleCanvasClick(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('mouseleave', () => this.handleMouseLeave());
    }
    
    drawCourt() {
        const { width, height } = this.options;
        const ctx = this.ctx;
        
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        // Draw court background
        ctx.fillStyle = this.options.courtColor;
        ctx.fillRect(0, 0, width, height);
        
        // Court dimensions (proportional)
        const courtMargin = 20;
        const courtWidth = width - (courtMargin * 2);
        const courtHeight = height - (courtMargin * 2);
        
        // Draw court lines
        ctx.strokeStyle = this.options.lineColor;
        ctx.lineWidth = 2;
        
        // Outer boundary
        ctx.strokeRect(courtMargin, courtMargin, courtWidth, courtHeight);
        
        // Service boxes
        const serviceLineY = courtMargin + (courtHeight * 0.25);
        const centerLineX = courtMargin + (courtWidth / 2);
        
        // Net line
        ctx.beginPath();
        ctx.moveTo(courtMargin, height / 2);
        ctx.lineTo(courtMargin + courtWidth, height / 2);
        ctx.stroke();
        
        // Service lines
        ctx.beginPath();
        ctx.moveTo(courtMargin, serviceLineY);
        ctx.lineTo(courtMargin + courtWidth, serviceLineY);
        ctx.moveTo(courtMargin, height - serviceLineY);
        ctx.lineTo(courtMargin + courtWidth, height - serviceLineY);
        ctx.stroke();
        
        // Center service line
        ctx.beginPath();
        ctx.moveTo(centerLineX, serviceLineY);
        ctx.lineTo(centerLineX, height - serviceLineY);
        ctx.stroke();
        
        // Draw zone labels
        this.drawZoneLabels();
    }
    
    drawZoneLabels() {
        const ctx = this.ctx;
        const { width, height } = this.options;
        
        ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
        ctx.font = '12px -apple-system, BlinkMacSystemFont, sans-serif';
        ctx.textAlign = 'center';
        
        // Zone labels
        const zones = [
            { name: 'Baseline', x: width/2, y: height - 40 },
            { name: 'Mid-Court', x: width/2, y: height * 0.65 },
            { name: 'Net', x: width/2, y: height * 0.35 },
            { name: 'Service Box', x: width/4, y: height * 0.4 },
            { name: 'Service Box', x: width * 0.75, y: height * 0.4 }
        ];
        
        zones.forEach(zone => {
            ctx.fillText(zone.name, zone.x, zone.y);
        });
    }
    
    updateHeatmap(positionData) {
        this.heatmapData = positionData;
        this.redraw();
    }
    
    redraw() {
        this.drawCourt();
        this.drawHeatmap();
        this.drawSelectedZone();
    }
    
    drawHeatmap() {
        if (!this.heatmapData || this.heatmapData.length === 0) return;
        
        const ctx = this.ctx;
        const { width, height } = this.options;
        
        // Create gradient for heatmap
        const maxIntensity = Math.max(...this.heatmapData.map(d => d.intensity));
        
        this.heatmapData.forEach(point => {
            const intensity = point.intensity / maxIntensity;
            const radius = 30 * intensity + 10;
            
            // Convert normalized coordinates to canvas coordinates
            const x = point.x * width;
            const y = point.y * height;
            
            // Create radial gradient
            const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
            gradient.addColorStop(0, `rgba(255, 0, 0, ${intensity * this.options.heatmapOpacity})`);
            gradient.addColorStop(0.5, `rgba(255, 165, 0, ${intensity * this.options.heatmapOpacity * 0.7})`);
            gradient.addColorStop(1, `rgba(255, 255, 0, 0)`);
            
            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(x, y, radius, 0, Math.PI * 2);
            ctx.fill();
        });
    }
    
    drawSelectedZone() {
        if (!this.selectedZone) return;
        
        const ctx = this.ctx;
        ctx.strokeStyle = '#007AFF';
        ctx.lineWidth = 3;
        ctx.setLineDash([5, 5]);
        
        const { x, y, width, height } = this.selectedZone;
        ctx.strokeRect(x, y, width, height);
        
        ctx.setLineDash([]);
    }
    
    handleCanvasClick(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // Determine which zone was clicked
        const zone = this.getZoneAtPosition(x, y);
        
        if (zone) {
            this.selectedZone = zone;
            this.redraw();
            
            // Trigger zone selection event
            this.onZoneSelected?.(zone);
        }
    }
    
    handleMouseMove(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // Show tooltip with position data
        this.showTooltip(x, y);
    }
    
    handleMouseLeave() {
        this.hideTooltip();
    }
    
    getZoneAtPosition(x, y) {
        const { width, height } = this.options;
        const courtMargin = 20;
        
        // Define court zones
        const zones = {
            baseline: { 
                x: courtMargin, 
                y: height * 0.75, 
                width: width - (courtMargin * 2), 
                height: height * 0.25 - courtMargin,
                name: 'Baseline'
            },
            midcourt: { 
                x: courtMargin, 
                y: height * 0.5, 
                width: width - (courtMargin * 2), 
                height: height * 0.25,
                name: 'Mid-Court'
            },
            net: { 
                x: courtMargin, 
                y: courtMargin, 
                width: width - (courtMargin * 2), 
                height: height * 0.5 - courtMargin,
                name: 'Net Area'
            }
        };
        
        for (const [key, zone] of Object.entries(zones)) {
            if (x >= zone.x && x <= zone.x + zone.width &&
                y >= zone.y && y <= zone.y + zone.height) {
                return { ...zone, key };
            }
        }
        
        return null;
    }
    
    showTooltip(x, y) {
        // Find nearest heatmap point
        const nearestPoint = this.findNearestHeatmapPoint(x, y);
        
        if (nearestPoint && this.getDistance(x, y, nearestPoint.x * this.options.width, nearestPoint.y * this.options.height) < 50) {
            this.createTooltip(x, y, nearestPoint);
        } else {
            this.hideTooltip();
        }
    }
    
    findNearestHeatmapPoint(x, y) {
        if (!this.heatmapData || this.heatmapData.length === 0) return null;
        
        let nearest = null;
        let minDistance = Infinity;
        
        this.heatmapData.forEach(point => {
            const pointX = point.x * this.options.width;
            const pointY = point.y * this.options.height;
            const distance = this.getDistance(x, y, pointX, pointY);
            
            if (distance < minDistance) {
                minDistance = distance;
                nearest = point;
            }
        });
        
        return nearest;
    }
    
    getDistance(x1, y1, x2, y2) {
        return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
    }
    
    createTooltip(x, y, data) {
        this.hideTooltip();
        
        const tooltip = document.createElement('div');
        tooltip.className = 'heatmap-tooltip';
        tooltip.innerHTML = `
            <div class="tooltip-content">
                <div class="tooltip-title">Position Data</div>
                <div class="tooltip-stat">
                    <span class="stat-label">Intensity:</span>
                    <span class="stat-value">${data.intensity.toFixed(1)}</span>
                </div>
                <div class="tooltip-stat">
                    <span class="stat-label">Strokes:</span>
                    <span class="stat-value">${data.strokeCount || 'N/A'}</span>
                </div>
                <div class="tooltip-stat">
                    <span class="stat-label">Zone:</span>
                    <span class="stat-value">${data.zone || 'Unknown'}</span>
                </div>
            </div>
        `;
        
        tooltip.style.cssText = `
            position: absolute;
            left: ${x + 10}px;
            top: ${y - 10}px;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 12px;
            border-radius: 8px;
            font-size: 12px;
            pointer-events: none;
            z-index: 1000;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        `;
        
        this.container.style.position = 'relative';
        this.container.appendChild(tooltip);
        this.currentTooltip = tooltip;
    }
    
    hideTooltip() {
        if (this.currentTooltip) {
            this.currentTooltip.remove();
            this.currentTooltip = null;
        }
    }
    
    // Animation methods
    animateHeatmapUpdate(newData, duration = 1000) {
        const startTime = Date.now();
        const oldData = [...this.heatmapData];
        
        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Interpolate between old and new data
            const interpolatedData = newData.map((newPoint, index) => {
                const oldPoint = oldData[index] || { intensity: 0, x: newPoint.x, y: newPoint.y };
                
                return {
                    ...newPoint,
                    intensity: oldPoint.intensity + (newPoint.intensity - oldPoint.intensity) * progress
                };
            });
            
            this.heatmapData = interpolatedData;
            this.redraw();
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        animate();
    }
    
    // Export functionality
    exportAsImage() {
        const link = document.createElement('a');
        link.download = 'tennis-heatmap.png';
        link.href = this.canvas.toDataURL();
        link.click();
    }
    
    // Zone analysis
    analyzeZone(zoneName) {
        const zoneData = this.heatmapData.filter(point => point.zone === zoneName);
        
        if (zoneData.length === 0) {
            return { message: `No data available for ${zoneName}` };
        }
        
        const totalIntensity = zoneData.reduce((sum, point) => sum + point.intensity, 0);
        const avgIntensity = totalIntensity / zoneData.length;
        const maxIntensity = Math.max(...zoneData.map(p => p.intensity));
        
        return {
            zone: zoneName,
            totalPoints: zoneData.length,
            averageIntensity: avgIntensity.toFixed(2),
            maxIntensity: maxIntensity.toFixed(2),
            coverage: `${((zoneData.length / this.heatmapData.length) * 100).toFixed(1)}%`
        };
    }
}

// CSS for tooltips
const heatmapStyles = `
    .heatmap-tooltip {
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
    }
    
    .tooltip-content {
        min-width: 150px;
    }
    
    .tooltip-title {
        font-weight: 600;
        margin-bottom: 8px;
        color: #00d4ff;
    }
    
    .tooltip-stat {
        display: flex;
        justify-content: space-between;
        margin-bottom: 4px;
    }
    
    .stat-label {
        opacity: 0.8;
    }
    
    .stat-value {
        font-weight: 500;
        color: #00d4ff;
    }
`;

// Inject styles
if (!document.getElementById('heatmap-styles')) {
    const styleSheet = document.createElement('style');
    styleSheet.id = 'heatmap-styles';
    styleSheet.textContent = heatmapStyles;
    document.head.appendChild(styleSheet);
}

// Export for use
window.TennisCourtHeatmap = TennisCourtHeatmap;
