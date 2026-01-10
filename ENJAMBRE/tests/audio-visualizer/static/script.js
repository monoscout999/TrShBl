// Initialize the audio context and analyser
audioCtx = new (window.AudioContext || window.webkitAudioContext)();
analyser = audioCtx.createAnalyser();
dataArray = new Uint8Array(analyser.frequencyBinCount);

// Create a source node for the audio
source = audioCtx.createMediaElementSource(document.getElementById('audio'));

// Connect the source to the analyser
source.connect(analyser);

// Set up the configuration
const CONFIG = {
  barCount: 64,
  barGap: 2,
  smoothing: 0.8,
  minDecibels: -90,
  maxDecibels: -10
};

// Function to draw bars on the canvas
function drawBars() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const barWidth = (canvas.width / CONFIG.barCount) - CONFIG.barGap;
  const barHeight = dataArray[0] * (canvas.height / 256);

  for (let i = 0; i < CONFIG.barCount; i++) {
    ctx.fillStyle = `hsl(${i * 360 / CONFIG.barCount}, 100%, ${dataArray[i] + 90}%)`;
    ctx.fillRect(i * barWidth, canvas.height - barHeight, barWidth, barHeight);
  }
}

// Function to update the audio data
function updateAudioData() {
  dataArray = new Uint8Array(analyser.frequencyBinCount);
  analyser.getByteFrequencyData(dataArray);
}

// Event listener for resizing the window
window.addEventListener('resize', () => {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
});

// Function to play or pause the audio
function togglePlayPause() {
  if (isPlaying) {
    source.stop();
    isPlaying = false;
  } else {
    source.start(0);
    isPlaying = true;
  }
}

// Event listener for playing/pausing the audio
document.getElementById('play-pause-btn').addEventListener('click', togglePlayPause);

// Start drawing bars on the canvas
drawBars();

// Update the audio data every frame
setInterval(updateAudioData, 20);

// --- MODULE ---

async function initAudio() {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = CONFIG.barCount * 2;
    analyser.smoothingTimeConstant = CONFIG.smoothing;
    analyser.minDecibels = CONFIG.minDecibels;
    analyser.maxDecibels = CONFIG.maxDecibels;
    dataArray = new Uint8Array(analyser.frequencyBinCount);
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        source = audioCtx.createMediaStreamSource(stream);
        source.connect(analyser);
        isPlaying = true;
        animate();
    } catch (e) {
        console.error('Audio error:', e);
    }
}

// --- MODULE ---

class Bar {
    constructor(x, width, index) {
        this.x = x;
        this.width = width;
        this.height = 0;
        this.targetHeight = 0;
        this.index = index;
        this.hue = index * (360 / CONFIG.barCount);
    }

    update(value) {
        this.targetHeight = (value / 255) * canvas.height * 0.8;
        this.height += (this.targetHeight - this.height) * 0.1;
    }

    draw() {
        const gradient = ctx.createLinearGradient(this.x, canvas.height, this.x, canvas.height - this.height);
        gradient.addColorStop(0, `hsl(${this.hue},100%,50%)`);
        gradient.addColorStop(1, `hsl(${this.hue + 30},100%,70%)`);
        ctx.fillStyle = gradient;
        ctx.fillRect(this.x, canvas.height - this.height, this.width, this.height);
    }
}

let bars = [];

function createBars() {
    bars = [];
    const barWidth = (canvas.width - (CONFIG.barCount - 1) * CONFIG.barGap) / CONFIG.barCount;
    for (let i = 0; i < CONFIG.barCount; i++) {
        bars.push(new Bar(i * (barWidth + CONFIG.barGap), barWidth, i));
    }
}

createBars();

// --- MODULE ---

function draw() {
    ctx.fillStyle = 'rgba(0,0,0,0.2)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    if (isPlaying && analyser) {
        analyser.getByteFrequencyData(dataArray);
        bars.forEach((bar, i) => {
            bar.update(dataArray[i]);
            bar.draw();
        });
    }
}

function animate() {
    draw();
    requestAnimationFrame(animate);
}

// --- MODULE ---

const startBtn = document.createElement('button');
startBtn.textContent = 'Start Audio';
startBtn.id = 'startBtn';
startBtn.onclick = () => {
  if (!isPlaying) {
    initAudio();
    startBtn.textContent = 'Listening...';
  }
};

document.body.appendChild(startBtn);

window.addEventListener('resize', createBars);