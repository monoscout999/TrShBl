window.Renderer = {
    init: function() {},
    draw: function() {
        const ctx = Game.ctx;
        ctx.fillStyle = '#0b0c10';
        ctx.fillRect(0, 0, Game.width, Game.height);
        
        const ts = Game.tileSize; // Camera offset placeholder
        let cx = 0, cy = 0; // Draw Visible Grid using nested loops
        
        for(let x=0; x<Grid.width; x++) {
            for(let y=0; y<Grid.height; y++) {
                let cell = Grid.cells[x][y];
                ctx.fillStyle = cell.terrain === 1 ? '#444' : '#c2b280';
                ctx.fillRect(x*ts, y*ts, ts-1, ts-1);
                
                if(cell.building) {
                    ctx.fillStyle = cell.building.constructor.name === 'SolarPanel' ? 'blue' : 'gray';
                    ctx.fillRect(x*ts+4, y*ts+4, ts-8, ts-8);
                }
            }
        }
        
        Game.entities.forEach(e => {
            ctx.fillStyle = 'white';
            ctx.beginPath();
            ctx.arc(e.x*ts + ts/2, e.y*ts + ts/2, ts/3, 0, Math.PI*2);
            ctx.fill();
        });
    }
};
