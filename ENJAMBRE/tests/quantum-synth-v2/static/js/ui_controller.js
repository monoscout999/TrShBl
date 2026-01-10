export class UIController {
  constructor(mainC, specC) {
    this.ctx = mainC.getContext('2d');
    this.sCtx = specC.getContext('2d');
    this.w = mainC.width;
    this.h = mainC.height;
  }

  update(data) {
    if (!data) return;

    this.ctx.clearRect(0, 0, this.w, this.h);
    this.ctx.strokeStyle = '#0f0';
    this.ctx.beginPath();

    const step = this.w / 128;
    for (let i = 0; i < 128; i++) {
      this.ctx.lineTo(i * step, 150 + data.freqs[i * 4] * 100);
    }
    this.ctx.stroke();

    this.sCtx.clearRect(0, 0, 240, 60);
    const bw = 240 / 32;
    for (let i = 0; i < 32; i++) {
      const v = Math.abs(data.freqs[i * 8]) * 50;
      this.sCtx.fillStyle = '#0ff';
      this.sCtx.fillRect(i * bw, 60 - v, bw - 1, v);
    }
  }
}
