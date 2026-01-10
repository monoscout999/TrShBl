window.scene = new THREE.Scene();
window.scene.background = new THREE.Color(0x87CEEB);
window.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
window.renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
dirLight.position.set(100, 100, 50);
scene.add(dirLight);

window.voxels = [];
window.voxelMap = new Map();
window.chunkSize = 20;

// Player physics globals
window.velocity = new THREE.Vector3();
window.direction = new THREE.Vector3();
