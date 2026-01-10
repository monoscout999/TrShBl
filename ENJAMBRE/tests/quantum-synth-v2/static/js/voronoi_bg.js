export class VoronoiBG {
  constructor(canvas) {
    this.ctx = canvas.getContext('2d');
    this.points = Array.from({ length: 32 }, () => [Math.random() * window.innerWidth, Math.random() * window.innerHeight]);
  }

  render(data) {
    const del = d3.Delaunay.from(this.points);
    const vor = del.voronoi([0, 0, window.innerWidth, window.innerHeight]);

    this.ctx.fillStyle = '#000';
    this.ctx.fillRect(0, 0, window.innerWidth, window.innerHeight);

    this.ctx.strokeStyle = `hsla(180, 100%, 50%, ${0.1 + data.bass * 0.5})`;
    this.ctx.lineWidth = 2;
    this.ctx.beginPath();
    vor.render(this.ctx);
    this.ctx.stroke();

    this.points.forEach(p => {
      p[0] += Math.sin(Date.now() * 0.001 + p[1]) * data.bass * 5;
      p[1] += Math.cos(Date.now() * 0.001 + p[0]) * data.bass * 5;
    });
  }
}
