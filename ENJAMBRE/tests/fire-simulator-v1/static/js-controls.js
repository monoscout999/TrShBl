// Initialize configuration object
let config = {
    intensity: 0.4,
    windStrength: 0.2,
    buoyancy: 0.3,
    tempRange: [1, 5],
    particleCount: 300
};

// Event listeners for sliders
document.getElementById('intensitySlider').addEventListener('input', function() {
    config.intensity = this.value;
});

document.getElementById('windSlider').addEventListener('input', function() {
    config.windStrength = this.value;
});

document.getElementById('buoyancySlider').addEventListener('input', function() {
    config.buoyancy = this.value;
});

document.getElementById('tempRangeSlider').addEventListener('input', function() {
    config.tempRange[1] = this.value;
});

document.getElementById('particleCountSlider').addEventListener('input', function() {
    config.particleCount = this.value;
});

// Event listener for canvas click
document.getElementById('canvas').addEventListener('click', function(event) {
    const rect = event.target.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Spawn 20 particles at the clicked position
    for (let i = 0; i < 20; i++) {
        spawnParticle(x, y);
    }
});

// Preset-campfire button
document.getElementById('presetCampfireButton').addEventListener('click', function() {
    config.intensity = 0.4;
    config.windStrength = 0.2;
    config.buoyancy = 0.3;
    config.particleCount = 300;
});

// Preset-torch button
document.getElementById('presetTorchButton').addEventListener('click', function() {
    config.intensity = 0.6;
    config.windStrength = 0.4;
    config.buoyancy = 0.5;
    config.particleCount = 400;
});

// Preset-inferno button
document.getElementById('presetInfernoButton').addEventListener('click', function() {
    config.intensity = 1.0;
    config.windStrength = 0.7;
    config.buoyancy = 0.8;
    config.particleCount = 700;
});

// Function to spawn a particle
function spawnParticle(x, y) {
    // Implementation of particle spawning logic
}

// FPS counter update every frame
let fpsCounter = 0;
setInterval(() => {
    fpsCounter++;
}, 1000);

// Main loop for rendering particles and updating the canvas
function render() {
    // Implementation of rendering logic
}
