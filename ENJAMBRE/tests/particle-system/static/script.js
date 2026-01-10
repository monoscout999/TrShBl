const canvas = document.createElement('canvas');
document.body.appendChild(canvas);
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let particles = [];
const particleCount = 200;

// Initialize particles
for (let i = 0; i < particleCount; i++) {
    particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 3,
        vy: (Math.random() - 0.5) * 3,
        angle: Math.random() * Math.PI * 2,
        baseX: Math.random() * canvas.width,
        baseY: Math.random() * canvas.height
    });
}

// Mouse tracking
let mouse = { x: -1000, y: -1000, active: false };

canvas.addEventListener('mousemove', (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
    mouse.active = true;
});

canvas.addEventListener('mouseleave', () => {
    mouse.active = false;
});

// Update particles
function update() {
    particles.forEach(p => {
        // Sine wave motion
        p.angle += 0.05;
        const sineX = Math.sin(p.angle) * 2;
        const sineY = Math.cos(p.angle * 0.7) * 2;
        
        // Mouse attraction
        if (mouse.active) {
            const dx = mouse.x - p.x;
            const dy = mouse.y - p.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            
            if (dist > 1 && dist < 200) {
                const force = 1 / (dist * dist) * 50;
                const angle = Math.atan2(dy, dx);
                p.vx += Math.cos(angle) * force;
                p.vy += Math.sin(angle) * force;
            }
        }
        
        // Apply forces
        p.vx += sineX * 0.01;
        p.vy += sineY * 0.01;
        
        // Friction
        p.vx *= 0.98;
        p.vy *= 0.98;
        
        // Update position
        p.x += p.vx;
        p.y += p.vy;
        
        // Wrap around edges
        if (p.x < 0) p.x = canvas.width;
        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;
    });
}

// Draw particles
function draw() {
    // Trail effect
    ctx.fillStyle = 'rgba(10, 10, 10, 0.15)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw particles
    particles.forEach(p => {
        const vel = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
        const hue = Math.min(vel * 45, 180);
        
        ctx.fillStyle = `hsl(${hue}, 100%, 50%)`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, 2, 0, Math.PI * 2);
        ctx.fill();
    });
}

// Animation loop
function animate() {
    update();
    draw();
    requestAnimationFrame(animate);
}

animate();