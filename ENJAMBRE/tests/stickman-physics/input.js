window.Input = {
  dragPoint: null,
  init: function() {
    const c = document.getElementById('canvas');
    c.onmousedown = e => {
      let min = 1000, nearest = null;
      Engine.points.forEach(p => {
        const d = Math.hypot(p.x - e.clientX, p.y - e.clientY);
        if(d < 50 && d < min) {
          min = d;
          nearest = p;
        }
      });
      this.dragPoint = nearest;
    };
    window.onmousemove = e => {
      if(this.dragPoint) {
        this.dragPoint.x = e.clientX;
        this.dragPoint.y = e.clientY;
        this.dragPoint.oldx = e.clientX;
        this.dragPoint.oldy = e.clientY;
      }
    };
    window.onmouseup = () => this.dragPoint = null;
  }
};
