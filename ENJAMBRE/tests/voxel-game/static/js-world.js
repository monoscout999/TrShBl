const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshLambertMaterial({ color: 0x228B22 });

function createVoxel(x, y, z) {
    const voxel = new THREE.Mesh(geometry, material);
    voxel.position.set(x, y, z);
    scene.add(voxel);
    voxels.push(voxel);
    voxelMap.set(x + ',' + y + ',' + z, voxel);
}

for (let x = -chunkSize; x < chunkSize; x++) {
    for (let z = -chunkSize; z < chunkSize; z++) {
        createVoxel(x, 0, z);
        if (Math.random() > 0.95) {
            createVoxel(x, 1, z);
            if (Math.random() > 0.5) createVoxel(x, 2, z);
        }
    }
}
