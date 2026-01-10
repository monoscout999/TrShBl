OS.apps.paint = {
    title: 'Paint',
    init: (el) => {
        el.innerHTML = `
            <div style='display:flex;height:100%;flex-direction:column'>
                <div style='background:#C0C0C0;padding:5px;display:flex;gap:5px'>
                    <button onclick='OS.apps.paint.color(this, "black")' style='background:black;width:20px;height:20px'></button>
                    <button onclick='OS.apps.paint.color(this, "red")' style='background:red;width:20px;height:20px'></button>
                    <button onclick='OS.apps.paint.color(this, "blue")' style='background:blue;width:20px;height:20px'></button>
                    <button onclick='OS.apps.paint.color(this, "green")' style='background:green;width:20px;height:20px'></button>
                    <button onclick='OS.apps.paint.clear(this)'>Clear</button>
                </div>
                <div style='flex:1;position:relative;background:white;cursor:crosshair'>
                    <canvas style='position:absolute;top:0;left:0;'></canvas>
                </div>
            </div>`;
        const canvas = el.querySelector('canvas');
        const container = canvas.parentElement;

        // Wait for layout
        setTimeout(() => {
            canvas.width = container.clientWidth;
            canvas.height = container.clientHeight;
            const ctx = canvas.getContext('2d');
            ctx.lineWidth = 3;
            ctx.lineCap = 'round';
            ctx.strokeStyle = 'black';

            let painting = false;

            canvas.onmousedown = (e) => { painting = true; ctx.beginPath(); ctx.moveTo(e.offsetX, e.offsetY); };
            canvas.onmousemove = (e) => {
                if (painting) { ctx.lineTo(e.offsetX, e.offsetY); ctx.stroke(); }
            };
            canvas.onmouseup = () => { painting = false; };
            canvas.onmouseleave = () => { painting = false; };

            el.dataset.color = 'black';
        }, 100);
    },
    color: (btn, color) => {
        const root = btn.closest('.window');
        const canvas = root.querySelector('canvas');
        const ctx = canvas.getContext('2d');
        ctx.strokeStyle = color;
    },
    clear: (btn) => {
        const root = btn.closest('.window');
        const canvas = root.querySelector('canvas');
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
};
