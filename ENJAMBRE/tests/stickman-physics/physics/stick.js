class Stick {
  constructor(p1, p2) {
    this.p1 = p1;
    this.p2 = p2;
    this.length = Math.hypot(p2.x - p1.x, p2.y - p1.y);
  }

  update() {
    const dx = this.p2.x - this.p1.x;
    const dy = this.p2.y - this.p1.y;
    const dist = Math.sqrt(dx*dx + dy*dy);
    const diff = this.length - dist;
    const percent = diff / dist / 2;
    const offsetX = dx * percent;
    const offsetY = dy * percent;

    if(!this.p1.pinned) {
      this.p1.x -= offsetX;
      this.p1.y -= offsetY;
    }

    if(!this.p2.pinned) {
      this.p2.x += offsetX;
      this.p2.y += offsetY;
    }
  }
}

window.Stick = Stick;
