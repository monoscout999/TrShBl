// Canvas setup
const canvas = document.getElementById('fire-canvas');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

window.addEventListener('resize', () => {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
});

// Config object
const config = {
  intensity: 0.7,
  windStrength: 0.3,
  buoyancy: 0.5,
  tempRange: [500, 2000],
  particleCount: 400
};

// Particles array
let particles = [];

// Simple noise function to replace SimplexNoise
function simpleNoise(x, y) {
  const seed = x * 12.9898 + y * 78.233;
  return (Math.sin(seed) * 43758.5453) % 1;
}

// Particle class
class Particle {
  constructor(x, y, temp) {
    this.x = x;
    this.y = y;
    this.vx = (Math.random() - 0.5) * 1;
    this.vy = -(Math.random() * 2 + 2); // Negative to go up
    this.temperature = temp;
    this.age = 0;
    this.maxAge = Math.random() * 60 + 60;
    this.size = this.map(this.temperature, 500, 2000, 2, 8);
  }

  map(value, start1, end1, start2, end2) {
    return ((value - start1) / (end1 - start1)) * (end2 - start2) + start2;
  }

  update() {
    this.age++;
    this.vy -= config.buoyancy * 0.05; // Buoyancy
    this.temperature *= 0.99; // Cool down

    // Wind turbulence
    const windOffset = simpleNoise(this.x * 0.01, this.y * 0.01) - 0.5;
    this.vx += windOffset * config.windStrength * 0.1;

    this.x += this.vx;
    this.y += this.vy;

    this.vx *= 0.99; // Dampening
  }

  draw() {
    const color = this.getColor();
    ctx.shadowBlur = 20;
    ctx.shadowColor = color;
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
    ctx.fill();
  }

  getColor() {
    if (this.temperature < 750) return '#ff0000'; // Red
    else if (this.temperature < 1250) return '#ff8800'; // Orange
    else if (this.temperature < 1750) return '#ffff00'; // Yellow
    else return '#ffffff'; // White
  }

  isDead() {
    return this.age > this.maxAge || this.temperature < 400 || this.y < -50;
  }
}

// Spawn particle function
function spawnParticle(x, y) {
  if (!x) x = Math.random() * canvas.width;
  if (!y) y = canvas.height;
  const temp = Math.random() * 500 + 1500;
  particles.push(new Particle(x, y, temp));
}

// Update particles
function updateParticles() {
  for (let i = particles.length - 1; i >= 0; i--) {
    particles[i].update();
    if (particles[i].isDead()) {
      particles.splice(i, 1);
    }
  }
}

// FPS tracking
let fps = 60;
let lastFrameTime = performance.now();

// Render function
function render() {
  const now = performance.now();
  fps = Math.round(1000 / (now - lastFrameTime));
  lastFrameTime = now;

  ctx.fillStyle = 'rgba(0,0,0,0.1)';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  updateParticles();
  particles.forEach(p => p.draw());

  document.getElementById('fps-counter').textContent = fps + ' FPS';

  requestAnimationFrame(render);
}

// Spawn particles based on intensity
setInterval(() => {
  const spawnCount = Math.floor(config.intensity * config.particleCount / 100);
  for (let i = 0; i < spawnCount; i++) {
    spawnParticle();
  }
}, 100);

// Event listeners - Sliders
document.getElementById('intensity').addEventListener('input', (e) => {
  config.intensity = e.target.value / 100;
});

document.getElementById('wind').addEventListener('input', (e) => {
  config.windStrength = e.target.value / 100;
});

document.getElementById('buoyancy').addEventListener('input', (e) => {
  config.buoyancy = e.target.value / 100;
});

document.getElementById('temperature').addEventListener('input', (e) => {
  config.tempRange[1] = parseInt(e.target.value);
});

document.getElementById('particle-count').addEventListener('input', (e) => {
  config.particleCount = parseInt(e.target.value);
});

// Canvas click - spawn burst
canvas.addEventListener('click', (e) => {
  for (let i = 0; i < 20; i++) {
    spawnParticle(e.clientX, e.clientY);
  }
});

// Preset buttons
document.getElementById('preset-campfire').addEventListener('click', () => {
  config.intensity = 0.4;
  config.windStrength = 0.2;
  config.buoyancy = 0.3;
  config.particleCount = 300;
});

document.getElementById('preset-torch').addEventListener('click', () => {
  config.intensity = 0.6;
  config.windStrength = 0.4;
  config.buoyancy = 0.5;
  config.particleCount = 400;
});

document.getElementById('preset-inferno').addEventListener('click', () => {
  config.intensity = 1.0;
  config.windStrength = 0.7;
  config.buoyancy = 0.8;
  config.particleCount = 700;
});

// Start render loop
render();

console.log('Fire Particle Simulator loaded. Click to spawn fire bursts!');
