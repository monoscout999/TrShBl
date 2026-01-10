const pCanvas = document.getElementById('particle-canvas');
const pCtx = pCanvas.getContext('2d');
pCanvas.width = window.innerWidth;
pCanvas.height = window.innerHeight;

let particles = [];

window.addEventListener('mousemove', e => {
  for (let i = 0; i < 5; i++) {
    particles.push({
      x: e.clientX,
      y: e.clientY,
      vx: (Math.random() - 0.5) * 5,
      vy: (Math.random() - 0.5) * 5,
      life: 100
    });
  }
});

function update() {
  pCtx.clearRect(0, 0, pCanvas.width, pCanvas.height);
  particles.forEach((p, i) => {
    p.x += p.vx;
    p.y += p.vy;
    p.life--;
    if (p.life <= 0) particles.splice(i, 1);
    pCtx.fillStyle = `rgba(0,255,65,${p.life / 100})`;
    pCtx.beginPath();
    pCtx.arc(p.x, p.y, 2, 0, Math.PI * 2);
    pCtx.fill();
  });
}

requestAnimationFrame(update);
