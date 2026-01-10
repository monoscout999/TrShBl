export class AudioEngine {
  constructor() {
    this.fft = new Tone.Analyser('fft', 1024);
    this.meter = new Tone.Meter();
    this.gainNode = new Tone.Gain(-12).toDestination();
    this.osc = new Tone.Oscillator('C2', 'sawtooth').connect(this.gainNode);
    this.gainNode.connect(this.fft);
    this.gainNode.connect(this.meter);
    this.active = false;
  }

  async start() {
    await Tone.start();
    this.osc.start();
    this.active = true;
  }

  setGain(db) {
    this.gainNode.gain.rampTo(Tone.dbToGain(db), 0.1);
  }

  update() {
    if (!this.active) return null;

    const f = this.fft.getValue();
    return {
      freqs: f,
      bass: Math.abs(f[5]) * 2,
      mid: Math.abs(f[50]) * 2,
      high: Math.abs(f[200]) * 2,
      level: this.meter.getValue()
    };
  }
}
