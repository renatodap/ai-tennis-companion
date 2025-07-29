class ParticleSystem {
    constructor() {
        this.canvas = null;
        this.ctx = null;
        this.particles = [];
        this.animationId = null;
        this.mouse = { x: 0, y: 0 };
        
        this.init();
    }

    init() {
        // Create canvas
        this.canvas = document.createElement('canvas');
        this.canvas.style.position = 'fixed';
        this.canvas.style.top = '0';
        this.canvas.style.left = '0';
        this.canvas.style.width = '100%';
        this.canvas.style.height = '100%';
        this.canvas.style.pointerEvents = 'none';
        this.canvas.style.zIndex = '1';
        this.canvas.style.opacity = '0.6';
        
        document.body.appendChild(this.canvas);
        this.ctx = this.canvas.getContext('2d');
        
        this.resize();
        this.createParticles();
        this.animate();
        
        // Event listeners
        window.addEventListener('resize', () => this.resize());
        document.addEventListener('mousemove', (e) => {
            this.mouse.x = e.clientX;
            this.mouse.y = e.clientY;
        });
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    createParticles() {
        const particleCount = Math.min(150, Math.floor(window.innerWidth * window.innerHeight / 8000));
        
        for (let i = 0; i < particleCount; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                size: Math.random() * 2 + 1,
                opacity: Math.random() * 0.5 + 0.2,
                color: this.getRandomColor(),
                pulsePhase: Math.random() * Math.PI * 2,
                originalSize: 0
            });
        }
        
        // Set original sizes
        this.particles.forEach(particle => {
            particle.originalSize = particle.size;
        });
    }

    getRandomColor() {
        const colors = [
            'rgba(99, 102, 241, ',   // Primary
            'rgba(139, 92, 246, ',   // Purple
            'rgba(6, 182, 212, ',    // Cyan
            'rgba(245, 158, 11, ',   // Amber
            'rgba(239, 68, 68, '     // Red
        ];
        return colors[Math.floor(Math.random() * colors.length)];
    }

    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Update and draw particles
        this.particles.forEach((particle, index) => {
            // Update position
            particle.x += particle.vx;
            particle.y += particle.vy;
            
            // Wrap around edges
            if (particle.x < 0) particle.x = this.canvas.width;
            if (particle.x > this.canvas.width) particle.x = 0;
            if (particle.y < 0) particle.y = this.canvas.height;
            if (particle.y > this.canvas.height) particle.y = 0;
            
            // Mouse interaction
            const dx = this.mouse.x - particle.x;
            const dy = this.mouse.y - particle.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < 100) {
                const force = (100 - distance) / 100;
                particle.vx += (dx / distance) * force * 0.01;
                particle.vy += (dy / distance) * force * 0.01;
                particle.opacity = Math.min(1, particle.opacity + force * 0.02);
            } else {
                particle.opacity = Math.max(0.2, particle.opacity - 0.01);
            }
            
            // Pulse effect
            particle.pulsePhase += 0.02;
            particle.size = particle.originalSize + Math.sin(particle.pulsePhase) * 0.5;
            
            // Apply friction
            particle.vx *= 0.99;
            particle.vy *= 0.99;
            
            // Draw particle
            this.ctx.save();
            this.ctx.globalAlpha = particle.opacity;
            this.ctx.fillStyle = particle.color + particle.opacity + ')';
            this.ctx.shadowBlur = 10;
            this.ctx.shadowColor = particle.color + '0.8)';
            
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            this.ctx.fill();
            this.ctx.restore();
        });
        
        // Draw connections
        this.drawConnections();
        
        this.animationId = requestAnimationFrame(() => this.animate());
    }

    drawConnections() {
        this.particles.forEach((particle, i) => {
            this.particles.slice(i + 1).forEach(otherParticle => {
                const dx = particle.x - otherParticle.x;
                const dy = particle.y - otherParticle.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < 80) {
                    const opacity = (80 - distance) / 80 * 0.1;
                    
                    this.ctx.save();
                    this.ctx.globalAlpha = opacity;
                    this.ctx.strokeStyle = 'rgba(99, 102, 241, 0.3)';
                    this.ctx.lineWidth = 1;
                    this.ctx.beginPath();
                    this.ctx.moveTo(particle.x, particle.y);
                    this.ctx.lineTo(otherParticle.x, otherParticle.y);
                    this.ctx.stroke();
                    this.ctx.restore();
                }
            });
        });
    }

    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        if (this.canvas && this.canvas.parentNode) {
            this.canvas.parentNode.removeChild(this.canvas);
        }
    }
}

// Initialize particle system when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Wait a bit for the page to load
    setTimeout(() => {
        new ParticleSystem();
    }, 1000);
});
