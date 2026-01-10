class Spark {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.vx = Math.random() * 4 - 2; // Random velocity between -2 and 2
        this.vy = Math.random() * 8 - 6; // Random velocity between -4 and -6
        this.size = Math.random() * 3 + 1; // Random size between 1 and 3
        this.brightness = Math.random() * 0.3 + 0.7; // Random brightness between 0.7 and 1
        this.life = Math.random() * 30 + 30; // Random life span between 30 and 60
        this.trail = []; // Trail array to store previous positions
    }

    update() {
        this.vy += 0.05; // Gravity
        this.x += this.vx;
        this.y += this.vy;
        this.vx *= 0.99; // Friction
        this.life -= 1; // Decrease life
        this.trail.push({ x: this.x, y: this.y }); // Add current position to trail

        if (this.trail.length > 5) {
            this.trail.shift(); // Remove the oldest position from the trail
        }
    }

    draw(ctx) {
        ctx.shadowBlur = 10; // Set shadow blur for trails
        ctx.shadowColor = 'orange'; // Set shadow color to orange
        ctx.fillStyle = `rgba(255, 200, 100, ${this.brightness})`; // Set fill style with brightness

        this.trail.forEach(dot => {
            ctx.beginPath();
            ctx.arc(dot.x, dot.y, this.size, 0, Math.PI * 2); // Draw each trail dot
            ctx.fill(); // Fill the circle
            ctx.closePath();
        });

        ctx.shadowBlur = 0; // Reset shadow blur after drawing trails
    }

    isDead() {
        return this.life <= 0; // Check if the spark has died
    }
}
