function animate() {
    requestAnimationFrame(animate);
    updatePlayer();

    // Update Particles
    if (window.particles) {
        for (let i = particles.length - 1; i >= 0; i--) {
            const p = particles[i];
            p.position.add(p.userData.vel);
            p.userData.vel.y -= 0.01; // Gravity
            p.userData.life--;
            p.rotation.x += 0.1;
            p.rotation.y += 0.1;

            if (p.userData.life <= 0) {
                scene.remove(p);
                particles.splice(i, 1);
            }
        }
    }

    renderer.render(scene, camera);
}
animate();
