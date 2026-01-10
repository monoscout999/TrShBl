// Initialize sliders with default values
document.getElementById('intensity').value = 0.3;
document.getElementById('wind').value = 0.1;
document.getElementById('buoyancy').value = 0.4;
document.getElementById('heat').value = 0.5;
document.getElementById('sparks').value = 0.6;

// Update slider display
function updateSliderDisplay(id, value) {
    document.getElementById(id + '-val').textContent = value.toFixed(2);
}

// Add input event listeners to sliders
document.getElementById('intensity').addEventListener('input', function() {
    const intensity = parseFloat(this.value);
    config.intensity = intensity;
    updateSliderDisplay('intensity', intensity);
});

document.getElementById('wind').addEventListener('input', function() {
    const wind = parseFloat(this.value);
    config.wind = wind;
    updateSliderDisplay('wind', wind);
});

document.getElementById('buoyancy').addEventListener('input', function() {
    const buoyancy = parseFloat(this.value);
    config.buoyancy = buoyancy;
    updateSliderDisplay('buoyancy', buoyancy);
});

document.getElementById('heat').addEventListener('input', function() {
    const heat = parseFloat(this.value);
    config.heat = heat;
    updateSliderDisplay('heat', heat);
});

document.getElementById('sparks').addEventListener('input', function() {
    const sparks = parseFloat(this.value);
    config.sparks = sparks;
    updateSliderDisplay('sparks', sparks);
});

// Canvas click event to spawn flames and sparks
const canvas = document.getElementById('fireCanvas');
canvas.addEventListener('click', function(event) {
    for (let i = 0; i < 15; i++) {
        const flame = new Flame(event.clientX, event.clientY);
        flames.push(flame);
    }
    for (let i = 0; i < 10; i++) {
        const spark = new Spark(event.clientX, event.clientY);
        sparks.push(spark);
    }
});

// Preset buttons
document.getElementById('candle').addEventListener('click', function() {
    config.intensity = 0.3;
    config.wind = 0.1;
    config.buoyancy = 0.4;
    updateSliderDisplay('intensity', 0.3);
    updateSliderDisplay('wind', 0.1);
    updateSliderDisplay('buoyancy', 0.4);
});

document.getElementById('campfire').addEventListener('click', function() {
    config.intensity = 0.5;
    config.wind = 0.2;
    config.buoyancy = 0.6;
    updateSliderDisplay('intensity', 0.5);
    updateSliderDisplay('wind', 0.2);
    updateSliderDisplay('buoyancy', 0.6);
});

document.getElementById('torch').addEventListener('click', function() {
    config.intensity = 0.6;
    config.wind = 0.4;
    config.buoyancy = 0.7;
    updateSliderDisplay('intensity', 0.6);
    updateSliderDisplay('wind', 0.4);
    updateSliderDisplay('buoyancy', 0.7);
});

document.getElementById('bonfire').addEventListener('click', function() {
    config.intensity = 0.8;
    config.wind = 0.3;
    config.buoyancy = 0.7;
    updateSliderDisplay('intensity', 0.8);
    updateSliderDisplay('wind', 0.3);
    updateSliderDisplay('buoyancy', 0.7);
});

document.getElementById('inferno').addEventListener('click', function() {
    config.intensity = 1.0;
    config.wind = 0.6;
    config.buoyancy = 0.9;
    updateSliderDisplay('intensity', 1.0);
    updateSliderDisplay('wind', 0.6);
    updateSliderDisplay('buoyancy', 0.9);
});

// Log message when the script is loaded
console.log('Realistic Fire Simulator loaded. Click to spawn flames!');
