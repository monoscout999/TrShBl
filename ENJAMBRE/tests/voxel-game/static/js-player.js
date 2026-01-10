camera.position.y = 2;

const keys = {};
document.addEventListener('keydown', (e) => keys[e.code] = true);
document.addEventListener('keyup', (e) => keys[e.code] = false);

// Mouse Look Logic
const euler = new THREE.Euler(0, 0, 0, 'YXZ');
document.addEventListener('mousemove', (event) => {
    if (document.pointerLockElement === document.body) {
        euler.setFromQuaternion(camera.quaternion);
        euler.y -= event.movementX * 0.002;
        euler.x -= event.movementY * 0.002;
        euler.x = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, euler.x));
        camera.quaternion.setFromEuler(euler);
    }
});

const playerSize = 0.6; // Player width/depth

function checkCollision(newX, newZ) {
    if (!window.voxelMap) return false;

    // Check bounding box corners around the new position
    const minX = Math.floor(newX - playerSize / 2);
    const maxX = Math.floor(newX + playerSize / 2);
    const minZ = Math.floor(newZ - playerSize / 2);
    const maxZ = Math.floor(newZ + playerSize / 2);

    // Check collision at foot level (y=0) and head level (y=1)
    // Assuming player is on the ground, y=0 blocks are floor, y=1 are obstacles
    // Current simple world has voxels at y=0, y=1, y=2

    for (let x = minX; x <= maxX; x++) {
        for (let z = minZ; z <= maxZ; z++) {
            // Check if there is a voxel at head or body height
            if (voxelMap.has(x + ',1,' + z) || voxelMap.has(x + ',2,' + z)) {
                return true;
            }
        }
    }
    return false;
}

let lastStepTime = 0;

function updatePlayer() {
    velocity.x -= velocity.x * 10.0 * 0.01;
    velocity.z -= velocity.z * 10.0 * 0.01;

    direction.z = Number(!!keys['KeyW']) - Number(!!keys['KeyS']);
    direction.x = Number(!!keys['KeyD']) - Number(!!keys['KeyA']);
    direction.normalize();

    if (keys['KeyW'] || keys['KeyS']) velocity.z -= direction.z * 400.0 * 0.01;
    if (keys['KeyA'] || keys['KeyD']) velocity.x -= direction.x * 400.0 * 0.01;

    const moveRotation = new THREE.Euler(0, euler.y, 0, 'YXZ');
    const moveQuaternion = new THREE.Quaternion().setFromEuler(moveRotation);

    // Calculate intended movement in local space relative to camera look direction
    // We want W to move forward, but restrict movement to XZ plane if we were flying
    // actually just use the velocity.z and x as magnitude

    // Local move vector
    const intendedMove = new THREE.Vector3(-velocity.x * 0.001, 0, velocity.z * 0.001);
    intendedMove.applyQuaternion(moveQuaternion);

    // Try Move X
    if (!checkCollision(camera.position.x + intendedMove.x, camera.position.z)) {
        camera.position.x += intendedMove.x;
    }

    // Try Move Z
    if (!checkCollision(camera.position.x, camera.position.z + intendedMove.z)) {
        camera.position.z += intendedMove.z;
    }

    // Footsteps
    if (intendedMove.length() > 0.01) {
        if (Date.now() - lastStepTime > 400) {
            if (window.playSound && window.playSound.step) window.playSound.step();
            lastStepTime = Date.now();
        }
    }
}
