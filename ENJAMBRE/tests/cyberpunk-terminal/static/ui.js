setInterval(() => {
    const cpu = Math.floor(Math.random() * 100);
    const mem = Math.floor(Math.random() * 100);
    document.getElementById('cpu-val').innerText = cpu + '%';
    document.getElementById('cpu-bar').style.width = cpu + '%';
    document.getElementById('mem-val').innerText = mem + '%';
    document.getElementById('mem-bar').style.width = mem + '%';
}, 2000);

const map = document.getElementById('mini-map');
for (let i = 0; i < 5; i++) {
    const n = document.createElement('div');
    n.style.cssText = `width:10px;height:10px;background:#00ff41;position:absolute;top:${Math.random() * 100}px;left:${Math.random() * 100}px;border-radius:50%;box-shadow:0 0 5px #00ff41`;
    map.appendChild(n);
}
