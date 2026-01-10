// Define FlameParticle class
class FlameParticle {
    constructor(x, y, temp) {
        this.x = x;
        this.y = y;
        this.temp = temp;
        this.speedX = Math.random() * 2 - 1;
        this.speedY = Math.random() * 2 - 1;
    }

    update() {
        this.x += this.speedX;
        this.y += this.speedY;

        // Check if particle is dead
        if (this.isDead()) {
            particles.splice(particles.indexOf(this), 1);
        }
    }

    isDead() {
        return this.x < 0 || this.x > canvas.width || this.y < 0 || this.y > canvas.height;
    }
}

// Define Spark class
class Spark {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.speedX = Math.random() * 2 - 1;
        this.speedY = Math.random() * 2 - 1;
    }

    update() {
        this.x += this.speedX;
        this.y += this.speedY;

        // Check if spark is dead
        if (this.isDead()) {
            sparks.splice(sparks.indexOf(this), 1);
        }
    }

    isDead() {
        return this.x < 0 || this.x > canvas.width || this.y < 0 || this.y > canvas.height;
    }
}

// Global variables
let particles = [];
let sparks = [];

// Configuration
const config = {
    sparkRate: 5,
    intensity: 1
};

// Spawn FlameParticle function
function spawnFlame(x, y) {
    if (x === undefined) x = Math.random() * canvas.width;
    if (y === undefined) y = Math.random() * canvas.height;
    const temp = Math.floor(Math.random() * 600 + 1200);
    particles.push(new FlameParticle(x, y, temp));
}

// Spawn Spark function
function spawnSpark(x, y) {
    if (Math.random() < config.sparkRate / 100) {
        sparks.push(new Spark(x, y));
    }
}

// Update particles function
function updateParticles() {
    for (let i = particles.length - 1; i >= 0; i--) {
        particles[i].update();
        if (particles[i].isDead()) {
            particles.splice(i, 1);
        }
    }
}

// Update sparks function
function updateSparks() {
    for (let i = sparks.length - 1; i >= 0; i--) {
        sparks[i].update();
        if (sparks[i].isDead()) {
            sparks.splice(i, 1);
        }
    }
}

// Spawn continuous function
function spawnContinuous() {
    const count = Math.floor(config.intensity * 3);
    for (let i = 0; i < count; i++) {
        const xPos = canvas.width / 2 + Math.random() * 100 - 50;
        spawnFlame(xPos, canvas.height);
        if (Math.random() < 0.3) {
            spawnSpark(xPos, canvas.height);
        }
    }
}

// Set interval for spawnContinuous function
setInterval(spawnContinuous, 50);
