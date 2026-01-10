window.Engine = {
  points: [],
  sticks: [],
  gravity: 0.5,
  friction: 0.999,
  width: window.innerWidth,
  height: window.innerHeight,

  update: function () {
    this.points.forEach(p => {
      p.update(this.friction, this.gravity);
      p.constrain(this.width, this.height);
    });

    for (let i = 0; i < 5; i++) {
      this.sticks.forEach(s => s.update());
    }
  }
};
