class Colonist {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.hunger = 0;
        this.fatigue = 0;
        this.state = 'IDLE';
    }

    update() {
        this.hunger += 0.05;
        this.fatigue += 0.02;

        if(this.hunger > 80 && Resources.consume('meal', 1)) {
            this.hunger = 0;
        }

        if(this.fatigue > 90) {
            this.state = 'SLEEP';
        }

        if(this.state === 'SLEEP') {
            this.fatigue -= 0.5;

            if(this.fatigue <= 0) {
                this.state = 'IDLE';
            }
        } else {
            // Random wander
            const move = Pathfinder.findPath(this.x, this.y, this.x + (Math.random() - 0.5) * 10, this.y + (Math.random() - 0.5) * 10);
            this.x += move[0] * 0.1;
            this.y += move[1] * 0.1;
        }
    }
}

window.Colonist = Colonist;
