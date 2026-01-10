let fps = 60;
let lastTime = performance.now();
let canvas = document.getElementById('canvas');
let ctx = canvas.getContext('2d');

function render() {
    let now = performance.now();
    fps = Math.round(1000 / (now - lastTime));
    lastTime = now;

    fillStyle = 'rgba(0,0,0,0.15)';
    clearCanvas();

    updateParticles();
    updateSparks();

    particles.sort((a, b) => b.y - a.y); // Sort by y descending for depth

    particles.forEach(particle => {
        ctx.fillStyle = particle.color;
        ctx.fillRect(particle.x, particle.y, particle.size, particle.size);
    });

    sparks.forEach(spark => {
        ctx.fillStyle = spark.color;
        ctx.fillRect(spark.x, spark.y, spark.size, spark.size);
    });

    document.getElementById('fps').textContent = `FPS: ${fps}`;
    document.getElementById('particleCount').textContent = `Particles: ${particles.length}`;

    requestAnimationFrame(render);
}

render();
