window.Grid = {
    width: 0,
    height: 0,
    cells: [],
    init: function(w, h) {
        this.width = w;
        this.height = h;
        for(let x=0; x<w; x++) {
            this.cells[x] = [];
            for(let y=0; y<h; y++) {
                this.cells[x][y] = { terrain: Math.random()>0.8 ? 1 : 0, building: null };
            }
        }
    },
    get: function(x, y) {
        if(x<0||x>=this.width||y<0||y>=this.height) return null;
        return this.cells[x][y];
    },
    placeBuilding: function(x, y, building) {
        const cell = this.get(x,y);
        if(cell && !cell.building && cell.terrain === 0) {
            cell.building = building;
            return true;
        }
        return false;
    }
};
