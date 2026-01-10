import { AudioEngine } from './audio_engine.js';
import { ParticleSystem } from './particle_system.js';
import { VoronoiBG } from './voronoi_bg.js';
import { UIController } from './ui_controller.js';

const canvasP = document.getElementById('particle-canvas');
const canvasB = document.getElementById('bg-canvas');
const canvasU = document.getElementById('ui-canvas');
const canvasS = document.getElementById('spectrogram-canvas');

const state = {
  density: 500,
  speed: 50,
  gain: -12
};

const resize = () => {
  [canvasP, canvasB, canvasU].forEach(c => {
    c.width = window.innerWidth;
    c.height = window.innerHeight;
  });
};

window.onresize = resize;
resize();

const audio = new AudioEngine();
const particles = new ParticleSystem(canvasP.getContext('2d'), 500);
const voronoi = new VoronoiBG(canvasB);
const ui = new UIController(canvasU, canvasS);

const mouse = { x: window.innerWidth / 2, y: window.innerHeight / 2 };

window.onmousemove = e => {
  mouse.x = e.clientX;
  mouse.y = e.clientY;
};

document.getElementById('start').onclick = async (e) => {
  await audio.start();
  e.target.style.display = 'none';
};

document.getElementById('gain-slider').oninput = e => {
  state.gain = parseFloat(e.target.value);
  audio.setGain(state.gain);
};

document.getElementById('speed-slider').oninput = e => {
  state.speed = parseFloat(e.target.value);
};

document.getElementById('density-slider').oninput = e => {
  state.density = parseInt(e.target.value);
  // Note: To change density dynamically we'd need a re-init or pool management
  // For now we use it as a speed multiplier or alpha tweak if logic allows
};

const loop = () => {
  const data = audio.update() || {
    freqs: new Float32Array(1024).fill(-100),
    bass: 0,
    mid: 0,
    high: 0,
    level: -60
  };

  voronoi.render(data);
  particles.draw(mouse, data, state);
  ui.update(data);

  requestAnimationFrame(loop);
};

loop();
