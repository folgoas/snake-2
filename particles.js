class Particle {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.vx = (Math.random() - 0.5) * 4;
        this.vy = (Math.random() - 0.5) * 4;
        this.lifetime = 255;
        this.colors = [
            [0, 255, 255],    // Neon Blue
            [255, 20, 147],   // Neon Pink
            [57, 255, 20]     // Neon Green
        ];
        this.color = this.colors[Math.floor(Math.random() * this.colors.length)];
    }

    update() {
        this.x += this.vx;
        this.y += this.vy;
        this.lifetime -= 5;
        return this.lifetime > 0;
    }

    draw(ctx) {
        const alpha = Math.max(0, Math.min(255, this.lifetime)) / 255;
        ctx.save();
        ctx.fillStyle = `rgba(${this.color[0]}, ${this.color[1]}, ${this.color[2]}, ${alpha})`;
        ctx.beginPath();
        ctx.arc(this.x, this.y, 2, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
    }
}

class ParticleSystem {
    constructor() {
        this.particles = [];
    }

    emit(x, y, count = 20) {
        for (let i = 0; i < count; i++) {
            this.particles.push(new Particle(x, y));
        }
    }

    update() {
        this.particles = this.particles.filter(particle => particle.update());
    }

    draw(ctx) {
        this.particles.forEach(particle => particle.draw(ctx));
    }
}
