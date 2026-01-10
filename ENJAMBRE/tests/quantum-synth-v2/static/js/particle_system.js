export class ParticleSystem {
  constructor(ctx, count) {
    this.ctx = ctx;
    this.particles = Array.from({ length: count }, () => ({
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      vx: 0,
      vy: 0
    }));
  }

  draw(mouse, data, settings) {
    this.ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
    this.particles.forEach(p => {
      const dx = mouse.x - p.x;
      const dy = mouse.y - p.y;
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist < 400) {
        const f = (1 - dist / 400) * 0.03;
        p.vx += dx * f;
        p.vy += dy * f;
      }

      if (dist < 50) {
        const rep = (1 - dist / 50) * 0.5;
        p.vx -= dx * rep;
        p.vy -= dy * rep;
      }

      p.x += p.vx * (settings.speed / 50);
      p.y += p.vy * (settings.speed / 50);

      p.vx *= 0.92;
      p.vy *= 0.92;

      if (p.x < 0) p.x = window.innerWidth;
      if (p.x > window.innerWidth) p.x = 0;
      if (p.y < 0) p.y = window.innerHeight;
      if (p.y > window.innerHeight) p.y = 0;

      this.ctx.fillStyle = `hsla(${200 + data.bass * 100}, 100%, 70%, 0.8)`;
      this.ctx.beginPath();
      this.ctx.arc(p.x, p.y, 2 + data.mid * 5, 0, Math.PI * 2);
      this.ctx.fill();
    });
  }
}
