// Get canvas by id 'fire-canvas'
const canvas = document.getElementById('fire-canvas');

// Get 2d context from the canvas
const ctx = canvas.getContext('2d');

// Set canvas width and height to window innerWidth and innerHeight
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

// Add window resize listener to update canvas size
window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
});

// Create config object with properties
const config = {
    intensity: 0.7,
    windStrength: 0.3,
    buoyancy: 0.5,
    tempRange: [500, 2000],
    particleCount: 400
};

// Create emptyparticles array
let particles = [];

// Add SimplexNoise initialization
const noise = new SimplexNoise();
