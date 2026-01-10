class Point {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.oldx = x;
        this.oldy = y;
        this.pinned = false;
    }

    update(friction, gravity, groundFriction) {
        if (this.pinned) return;
        const vx = (this.x - this.oldx) * friction;
        const vy = (this.y - this.oldy) * friction;
        this.oldx = this.x;
        this.oldy = this.y;
        this.x += vx;
        this.y += vy + gravity;
    }

    constrain(width, height) {
        if (this.x > width) {
            this.x = width;
            this.oldx = this.x + (this.x - this.oldx) * 0.5;
        } else if (this.x < 0) {
            this.x = 0;
            this.oldx = this.x + (this.x - this.oldx) * 0.5;
        }
        if (this.y > height - 50) {
            this.y = height - 50;
            this.oldy = this.y;
            this.x += (this.x - this.oldx) * 0.1;
        } else if (this.y < 0) {
            this.y = 0;
        }
    }
}

window.Point = Point;
