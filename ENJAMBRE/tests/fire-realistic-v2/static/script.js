// Setup
const canvas = document.getElementById('fire-canvas');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
});

const config = {
    intensity: 0.7,
    windStrength: 0.3,
    buoyancy: 0.6,
    heatIntensity: 0.8,
    sparkRate: 0.5
};

let particles = [];
let sparks = [];

function noise(x, y, time) {
    const s = x * 12.9898 + y * 78.233 + time * 43.758;
    return (Math.sin(s) * 43758.5453) % 1;
}

// FlameParticle class
class FlameParticle {
    constructor(x, y, temp) {
        this.x = x;
        this.y = y;
        this.vx = (Math.random() - 0.5);
        this.vy = -(Math.random() * 2 + 3);
        this.temp = temp;
        this.age = 0;
        this.maxAge = Math.random() * 40 + 60;
        this.width = Math.random() * 8 + 12;
        this.height = Math.random() * 20 + 30;
    }

    update() {
        this.age++;
        this.vy -= config.buoyancy * 0.08;
        this.temp *= 0.97;
        const flicker = noise(this.x * 0.05, this.y * 0.05, Date.now() * 0.001) - 0.5;
        this.vx += flicker * 0.3;
        this.width = Math.max(4, this.width + flicker * 2);
        this.x += this.vx;
        this.y += this.vy;
        this.vx *= 0.98;
    }

    draw() {
        const alpha = (1 - this.age / this.maxAge);
        const gradient = ctx.createLinearGradient(this.x, this.y, this.x, this.y + this.height);
        gradient.addColorStop(0, `rgba(255,255,255,${alpha * 0.9})`);
        gradient.addColorStop(0.3, `rgba(255,255,100,${alpha * 0.8})`);
        gradient.addColorStop(0.6, `rgba(255,150,0,${alpha * 0.6})`);
        gradient.addColorStop(1, `rgba(255,50,0,${alpha * 0.2})`);

        ctx.save();
        ctx.fillStyle = gradient;
        ctx.shadowBlur = 20;
        ctx.shadowColor = 'rgba(255,100,0,0.5)';
        ctx.beginPath();
        ctx.ellipse(this.x, this.y + this.height / 2, this.width / 2, this.height / 2, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
    }

    isDead() {
        return this.age > this.maxAge || this.temp < 300;
    }
}

// Spark class
class Spark {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.vx = (Math.random() - 0.5) * 4;
        this.vy = -(Math.random() * 2 + 4);
        this.size = Math.random() * 2 + 1;
        this.brightness = Math.random() * 0.3 + 0.7;
        this.life = Math.random() * 30 + 30;
        this.trail = [];
    }

    update() {
        this.vy += 0.05;
        this.x += this.vx;
        this.y += this.vy;
        this.vx *= 0.99;
        this.life--;
        this.trail.push({ x: this.x, y: this.y });
        if (this.trail.length > 5) this.trail.shift();
    }

    draw() {
        this.trail.forEach((dot, i) => {
            const alpha = (i / this.trail.length) * this.brightness;
            ctx.fillStyle = `rgba(255,200,100,${alpha})`;
            ctx.beginPath();
            ctx.arc(dot.x, dot.y, this.size * 0.5, 0, Math.PI * 2);
            ctx.fill();
        });

        ctx.shadowBlur = 10;
        ctx.shadowColor = 'orange';
        ctx.fillStyle = `rgba(255,200,100,${this.brightness})`;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
    }

    isDead() {
        return this.life <= 0;
    }
}

// Physics
function spawnFlame(x, y) {
    if (!x) x = canvas.width / 2 + (Math.random() - 0.5) * 100;
    if (!y) y = canvas.height;
    const temp = Math.random() * 500 + 1300;
    particles.push(new FlameParticle(x, y, temp));
}

function spawnSpark(x, y) {
    if (Math.random() < config.sparkRate * 0.01) {
        sparks.push(new Spark(x, y));
    }
}

function updateParticles() {
    for (let i = particles.length - 1; i >= 0; i--) {
        particles[i].update();
        if (particles[i].isDead()) particles.splice(i, 1);
    }
}

function updateSparks() {
    for (let i = sparks.length - 1; i >= 0; i--) {
        sparks[i].update();
        if (sparks[i].isDead()) sparks.splice(i, 1);
    }
}

function spawnContinuous() {
    const count = Math.floor(config.intensity * 3);
    for (let i = 0; i < count; i++) {
        const xPos = canvas.width / 2 + (Math.random() - 0.5) * 100;
        spawnFlame(xPos, canvas.height);
        if (Math.random() < 0.3) spawnSpark(xPos, canvas.height);
    }
}

setInterval(spawnContinuous, 50);

// Rendering
let fps = 60;
let lastTime = performance.now();

function render() {
    const now = performance.now();
    fps = Math.round(1000 / (now - lastTime));
    lastTime = now;

    ctx.fillStyle = 'rgba(0,0,0,0.15)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    updateParticles();
    updateSparks();

    particles.sort((a, b) => b.y - a.y);
    particles.forEach(p => p.draw());
    sparks.forEach(s => s.draw());

    document.getElementById('fps').textContent = fps + ' FPS';
    document.getElementById('particle-count').textContent = 'Particles: ' + particles.length;

    requestAnimationFrame(render);
}

render();

// Controls
function updateSliderDisplay(id, value) {
    const el = document.getElementById(id + '-val');
    if (el) el.textContent = Math.round(value);
}

['intensity', 'wind', 'buoyancy', 'heat', 'sparks'].forEach(id => {
    const slider = document.getElementById(id);
    if (slider) {
        slider.addEventListener('input', (e) => {
            const val = e.target.value / 100;
            if (id === 'intensity') config.intensity = val * 10;
            else if (id === 'wind') config.windStrength = val;
            else if (id === 'buoyancy') config.buoyancy = val;
            else if (id === 'heat') config.heatIntensity = val;
            else if (id === 'sparks') config.sparkRate = val * 100;
            updateSliderDisplay(id, e.target.value);
        });
        updateSliderDisplay(id, slider.value);
    }
});

canvas.addEventListener('click', (e) => {
    for (let i = 0; i < 15; i++) spawnFlame(e.clientX, e.clientY);
    for (let i = 0; i < 10; i++) spawnSpark(e.clientX, e.clientY);
});

// Presets
const presets = {
    'preset-candle': { intensity: 0.3, windStrength: 0.1, buoyancy: 0.4 },
    'preset-campfire': { intensity: 0.5, windStrength: 0.2, buoyancy: 0.6 },
    'preset-torch': { intensity: 0.6, windStrength: 0.4, buoyancy: 0.7 },
    'preset-bonfire': { intensity: 0.8, windStrength: 0.3, buoyancy: 0.7 },
    'preset-inferno': { intensity: 1.0, windStrength: 0.6, buoyancy: 0.9 }
};

Object.keys(presets).forEach(id => {
    const btn = document.getElementById(id);
    if (btn) {
        btn.addEventListener('click', () => {
            Object.assign(config, presets[id]);
            updateSliderDisplay('intensity', config.intensity * 10);
            updateSliderDisplay('wind', config.windStrength * 100);
            updateSliderDisplay('buoyancy', config.buoyancy * 100);
        });
    }
});

console.log('Realistic Fire Simulator loaded! Click to spawn flames 🔥');
