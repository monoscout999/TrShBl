class Ragdoll {
  constructor(x, y) {
    const p = (ox, oy) => {
      const pt = new Point(x + ox, y + oy);
      Engine.points.push(pt);
      return pt;
    };

    const s = (p1, p2) => {
      const st = new Stick(p1, p2);
      Engine.sticks.push(st);
      return st;
    };

    this.head = p(0, 0);
    const neck = p(0, 25);
    const torso = p(0, 80);
    const lElbow = p(-20, 40);
    const lHand = p(-40, 60);
    const rElbow = p(20, 40);
    const rHand = p(40, 60);
    const hips = p(0, 100);
    const lKnee = p(-15, 140);
    this.lFoot = p(-20, 190);
    const rKnee = p(15, 140);
    this.rFoot = p(20, 190);

    s(this.head, neck);
    s(neck, torso);
    s(neck, lElbow);
    s(lElbow, lHand);
    s(neck, rElbow);
    s(rElbow, rHand);
    s(torso, hips);
    s(hips, lKnee);
    s(lKnee, this.lFoot);
    s(hips, rKnee);
    s(rKnee, this.rFoot);
    s(this.head, torso);
    s(lElbow, torso);
    s(rElbow, torso);
    s(hips, this.head);
  }
}

window.Ragdoll = Ragdoll;
