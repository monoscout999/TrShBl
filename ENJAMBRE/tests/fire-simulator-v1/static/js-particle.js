class Particle {
    constructor(x, y, temp) {
        this.x = x;
        this.y = y;
        this.vx = Math.random() * 1 - 0.5; // Random between -0.5 and 0.5
        this.vy = Math.random() * 2 + 4; // Random between -2 and -4
        this.temperature = temp;
        this.age = 0;
        this.maxAge = Math.random() * 60 + 120; // Random between 60 and 120
        this.size = map(this.temperature, 500, 2000, 2, 8); // Map temperature to size
    }

    update() {
        this.age++;
        this.vy -= config.buoyancy * 0.1; // Apply buoyancy
        this.temperature *= 0.98; // Decrease temperature
        this.x += this.vx;
        this.y += this.vy;
    }

    draw(ctx) {
        ctx.shadowBlur = 15;
        ctx.shadowColor = calculateColor(this.temperature);
        ctx.fillStyle = calculateColor(this.temperature);
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
    }

    isDead() {
        return this.age > this.maxAge || this.temperature < 400;
    }
}

function map(value, start1, end1, start2, end2) {
    return (value - start1) / (end1 - start1) * (end2 - start2) + start2;
}

function calculateColor(temp) {
    if (temp < 750) return '#ff0000';
    else if (temp < 1250) return '#ff8800';
    else if (temp < 1750) return '#ffff00';
    else return '#ffffff';
}
