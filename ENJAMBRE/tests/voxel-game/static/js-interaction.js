const raycaster = new THREE.Raycaster();
const handRange = 4;
const handGeo = new THREE.BoxGeometry(0.2, 0.2, 0.6);
const handMat = new THREE.MeshBasicMaterial({ color: 0xFFCCAA });
const hand = new THREE.Mesh(handGeo, handMat);
camera.add(hand);
hand.position.set(0.3, -0.3, -0.5);
scene.add(camera);

// Particle System
window.particles = [];
const particleGeo = new THREE.BoxGeometry(0.1, 0.1, 0.1);
const particleMat = new THREE.MeshBasicMaterial({ color: 0x228B22 });

function spawnParticles(pos) {
    for (let i = 0; i < 8; i++) {
        const p = new THREE.Mesh(particleGeo, particleMat);
        p.position.copy(pos);
        // Random spread inside the block
        p.position.x += (Math.random() - 0.5) * 0.5;
        p.position.y += (Math.random() - 0.5) * 0.5;
        p.position.z += (Math.random() - 0.5) * 0.5;

        // Random velocity
        p.userData = {
            vel: new THREE.Vector3(
                (Math.random() - 0.5) * 0.2,
                (Math.random() * 0.2), // Upward pop
                (Math.random() - 0.5) * 0.2
            ),
            life: 60 // frames
        };
        scene.add(p);
        particles.push(p);
    }
}

document.addEventListener('click', () => {
    document.body.requestPointerLock();
    raycaster.setFromCamera(new THREE.Vector2(), camera);
    const intersects = raycaster.intersectObjects(voxels);
    if (intersects.length > 0 && intersects[0].distance < handRange) {
        const obj = intersects[0].object;

        // Play Sound
        if (window.playSound && window.playSound.break) window.playSound.break();

        // Spawn Particles
        spawnParticles(obj.position);

        scene.remove(obj);
        voxels.splice(voxels.indexOf(obj), 1);
        voxelMap.delete(obj.position.x + ',' + obj.position.y + ',' + obj.position.z); // Update Map for collision

        hand.position.z = -0.8;
        setTimeout(() => hand.position.z = -0.5, 100);
    } else {
        hand.position.z = -0.8;
        setTimeout(() => hand.position.z = -0.5, 100);
    }
});
