class CyberpunkGrid {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.lineSpacing = 40;  
        this.scrollSpeed = 1;  
        this.offset = 0;
        this.alpha = 0.5;  

    }

    update() {
        this.offset = (this.offset + this.scrollSpeed) % this.lineSpacing;
    }

    draw() {
        this.ctx.save();
        this.ctx.strokeStyle = `rgba(0, 255, 255, ${this.alpha})`;
        this.ctx.lineWidth = 1;

        // Lignes horizontales
        for (let y = -this.lineSpacing + this.offset; y < this.canvas.height + this.lineSpacing; y += this.lineSpacing) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }

        // Lignes verticales
        for (let x = -this.lineSpacing + this.offset; x < this.canvas.width + this.lineSpacing; x += this.lineSpacing) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }

        this.ctx.restore();
    }
}
