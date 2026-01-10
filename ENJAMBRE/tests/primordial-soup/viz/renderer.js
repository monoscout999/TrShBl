window.Renderer = {
    ctx: null,
    init: function() {
        const cvs = document.getElementById('canvas');
        cvs.width = Config.width;
        cvs.height = Config.height;
        this.ctx = cvs.getContext('2d');
    },
    draw: function(particles) {
        const ctx = this.ctx;
        ctx.globalCompositeOperation = 'source-over';
        ctx.fillStyle = 'rgba(0, 0, 0, 0.4)';
        ctx.fillRect(0, 0, Config.width, Config.height);
        ctx.globalCompositeOperation = 'lighter';
        particles.forEach(p => {
            ctx.fillStyle = Colors[p.color];
            ctx.beginPath();
            ctx.arc(p.x, p.y, 2, 0, Math.PI*2);
            ctx.fill();
        });
    }
};
