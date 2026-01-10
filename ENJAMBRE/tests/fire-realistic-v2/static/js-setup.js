// Setup canvas and context
const canvas = document.createElement('canvas');
document.body.appendChild(canvas);
const ctx = canvas.getContext('2d');

// Set canvas width and height to window inner dimensions
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

// Add resize listener
window.addEventListener('resize', () => {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
});

// Create config object
const config = {
  intensity: 0.7,
  windStrength: 0.3,
  buoyancy: 0.6,
  heatIntensity: 0.8,
  sparkRate: 0.5
};

// Create empty particles array and empty sparks array
let particles = [];
let sparks = [];

// PerlinNoise function
function noise(x, y, time) {
  const s = x * 12.9898 + y * 78.233 + time * 43.758;
  return (Math.sin(s) * 43758.5453) % 1;
}
