const canvas = document.createElement('canvas');
document.body.appendChild(canvas);
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

window.addEventListener('resize', () => {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  createBars();
});

const CONFIG = { barCount: 32, smoothing: 0.85 };

let audioCtx, analyser, dataArray, isPlaying = false;

// --- MODULE ---

async function initAudio() {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 128;
    analyser.smoothingTimeConstant = CONFIG.smoothing;
    dataArray = new Uint8Array(analyser.frequencyBinCount);
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const source = audioCtx.createMediaStreamSource(stream);
    source.connect(analyser);
    isPlaying = true;
    animate();
}

// --- MODULE ---

let bars = [];
function createBars() {
  bars = [];
  const w = canvas.width / CONFIG.barCount;
  for (let i = 0; i < CONFIG.barCount; i++) {
    bars.push({ x: i * w, w: w - 2, h: 0, hue: i * (360 / CONFIG.barCount) });
  }
}
createBars();

// --- MODULE ---

// Function to draw the canvas
function draw() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.15)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    if (isPlaying && analyser) {
        analyser.getByteFrequencyData(dataArray);
        bars.forEach(function(bar, i) {
            var val = dataArray[i] || 0;
            bar.h += (val / 255 * canvas.height - bar.h) * 0.15;
            ctx.fillStyle = 'hsl(' + bar.hue + ', 100%, 50%)';
            ctx.fillRect(bar.x, canvas.height - bar.h, bar.w, bar.h);
        });
    }
}

// Function to animate the drawing
function animate() {
    draw();
    requestAnimationFrame(animate);
}

// Create a button and add it to the body
var btn = document.createElement('button');
btn.id = 'startBtn';
btn.textContent = 'START';
btn.onclick = function() {
    initAudio();
    btn.remove();
};
document.body.appendChild(btn);