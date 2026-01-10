window.Physics = {
  particles: [],
  hash: null,

  init: function () {
    this.hash = new SpatialHash(Config.radius);
    for (let i = 0; i < Config.particleCount; i++) {
      const type = Config.types[Math.floor(Math.random() * Config.types.length)];
      this.particles.push(new Particle(Math.random() * Config.width, Math.random() * Config.height, type));
    }
  },

  update: function () {
    this.hash.clear();
    this.particles.forEach(p => this.hash.add(p));

    this.particles.forEach(p1 => {
      let Fx = 0, Fy = 0;
      const neighbors = this.hash.query(p1, Config.radius);

      neighbors.forEach(p2 => {
        if (p1 === p2) return;

        const dx = p2.x - p1.x;
        const dy = p2.y - p1.y;
        const d = Math.sqrt(dx * dx + dy * dy);

        if (d > 0 && d < Config.radius) {
          const F = InteractionMatrix.getForce(p1.color, p2.color) / d;
          Fx += (dx / d) * F;
          Fy += (dy / d) * F;
        }
      });

      p1.vx = (p1.vx + Fx * Config.forceFactor) * Config.friction;
      p1.vy = (p1.vy + Fy * Config.forceFactor) * Config.friction;
      p1.update();
    });
  }
};
