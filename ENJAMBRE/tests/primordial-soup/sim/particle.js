class Particle {
    constructor(x, y, color) {
        this.x = x;
        this.y = y;
        this.vx = 0;
        this.vy = 0;
        this.color = color;
    }

    update() {
        this.x += this.vx;
        this.y += this.vy;

        if(this.x <= 0 || this.x >= Config.width) {
            this.vx *= -1;
        }

        if(this.y <= 0 || this.y >= Config.height) {
            this.vy *= -1;
        }
    }
}

window.Particle = Particle;
