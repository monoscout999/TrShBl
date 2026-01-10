class FlameParticle {
    constructor(x, y, temp) {
        this.x = x;
        this.y = y;
        this.baseY = y;
        this.vx = Math.random() * 1 - 0.5;
        this.vy = Math.random() * 3 - 5;
        this.temp = temp;
        this.age = 0;
        this.maxAge = Math.random() * 40 + 80;
        this.width = Math.random() * 8 + 16;
        this.height = Math.random() * 20 + 40;
    }

    update() {
        this.age++;
        this.vy -= config.buoyancy * 0.08;
        this.temp *= 0.97;
        const flicker = noise(this.x * 0.05, this.y * 0.05, Date.now() * 0.001) - 0.5;
        this.vx += flicker * 0.3;
        this.width += flicker * 2;
        this.x += this.vx;
        this.y += this.vy;
        this.vx *= 0.98;
    }

    draw(ctx) {
        const alpha = (1 - this.age / this.maxAge);
        const gradient = ctx.createLinearGradient(this.x, this.y, this.x, this.y + this.height);
        gradient.addColorStop(0, 'white');
        gradient.addColorStop(0.9, 'yellow');
        gradient.addColorStop(0.7, 'orange');
        gradient.addColorStop(0.6, 'red');
        gradient.addColorStop(0.5, 'orange');
        gradient.addColorStop(0.2, 'white');
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.moveTo(this.x, this.y);
        ctx.arc(this.x, this.y + this.height / 2, this.width / 2, 0, Math.PI * 2);
        ctx.closePath();
        ctx.fill();
    }

    isDead() {
        return this.age > this.maxAge || this.temp < 300;
    }
}
