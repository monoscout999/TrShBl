// Define Particle class
class Particle {
  constructor(x, y, temp) {
    this.x = x;
    this.y = y;
    this.temp = temp;
    this.vx = Math.random() * 0.1 - 0.05; // Random wind speed between -0.05 and 0.05
    this.vy = Math.random() * 0.02 - 0.01; // Random vertical velocity
    this.isDead = false;
  }

  update() {
    this.x += this.vx;
    this.y += this.vy;
    this.temp -= 0.01; // Decrease temperature over time

    if (this.temp < 1500) {
      this.isDead = true;
    }
  }

  draw(ctx) {
    ctx.fillStyle = `rgba(255, 255, 255, ${this.temp / 2000})`;
    ctx.fillRect(this.x, this.y, 2, 2);
  }
}

// Define config object
const config = {
  windStrength: 0.1,
};

// Initialize particles array
let particles = [];

// Function to spawn a new particle
function spawnParticle() {
  const x = Math.random() * canvas.width;
  const y = canvas.height;
  const temp = Math.random() * 500 + 1500; // Random temperature between 1500 and 2000
  particles.push(new Particle(x, y, temp));
}

// Function to update all particles
function updateParticles() {
  for (let i = particles.length - 1; i >= 0; i--) {
    particles[i].update();
    if (particles[i].isDead) {
      particles.splice(i, 1);
    }
  }
}

// Function to render the canvas
function render() {
  ctx.fillStyle = 'rgba(0,0,0,0.1)';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  for (let particle of particles) {
    particle.draw(ctx);
  }

  fpsCounter.innerText = `FPS: ${Math.round(fps)}`;

  requestAnimationFrame(render);
}

// Start the render loop
render();
