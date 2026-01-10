window.Game = {
    tileSize: 32,
    width: 0,
    height: 0,
    entities: [],
    buildings: [],
    speed: 1,
    time: 0,
    dayCycle: 12000,

    init: function () {
        this.canvas = document.getElementById('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.resize();
        window.onresize = () => this.resize();
        Grid.init(50, 50);
        Renderer.init();
        Interface.init();

        // Spawn Initial Colonists
        for (let i = 0; i < 5; i++) {
            this.entities.push(new Colonist(10 + Math.random() * 5, 10 + Math.random() * 5));
        }

        this.loop();
    },

    resize: function () {
        this.width = window.innerWidth;
        this.height = window.innerHeight;
        this.canvas.width = this.width;
        this.canvas.height = this.height;
    },

    update: function () {
        this.time += this.speed;
        if (this.time > this.dayCycle) this.time = 0;
        Resources.update();
        this.entities.forEach(e => e.update());
        this.buildings.forEach(b => b.update());
    },

    loop: function () {
        requestAnimationFrame(() => this.loop());
        this.update();
        Renderer.draw();
    }
};

window.onload = () => Game.init();
