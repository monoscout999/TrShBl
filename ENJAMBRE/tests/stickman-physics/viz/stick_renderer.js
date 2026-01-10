window.Renderer = {
    canvas: null,
    ctx: null,
    init: function () {
        this.canvas = document.getElementById('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.width = this.canvas.width = window.innerWidth;
        this.height = this.canvas.height = window.innerHeight;
        Engine.width = this.width;
        Engine.height = this.height;
    },
    draw: function () {
        const ctx = this.ctx;
        ctx.clearRect(0, 0, this.width, this.height);
        ctx.lineWidth = 4;
        ctx.strokeStyle = 'white';
        ctx.beginPath();
        Engine.sticks.forEach(s => {
            ctx.moveTo(s.p1.x, s.p1.y);
            ctx.lineTo(s.p2.x, s.p2.y);
        });
        ctx.stroke();

        // Draw Floor
        ctx.strokeStyle = '#555';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(0, this.height - 50);
        ctx.lineTo(this.width, this.height - 50);
        ctx.stroke();

        // Draw Stickmen Points
        ctx.fillStyle = 'red';
        Engine.points.forEach(p => {
            ctx.beginPath();
            ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
            ctx.fill();
        });
    }
};
