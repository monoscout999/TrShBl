window.Pathfinder = {
    findPath: function(sx, sy, tx, ty) {
        const dx = tx - sx;
        const dy = ty - sy;
        if(Math.abs(dx) > Math.abs(dy)) return [Math.sign(dx), 0];
        else return [0, Math.sign(dy)];
    }
};
