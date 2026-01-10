class SpatialHash {
  constructor(cellSize) {
    this.cellSize = cellSize;
    this.grid = new Map();
  }

  clear() {
    this.grid.clear();
  }

  getKey(x, y) {
    return `${Math.floor(x/this.cellSize)},${Math.floor(y/this.cellSize)}`;
  }

  add(p) {
    const key = this.getKey(p.x, p.y);
    if(!this.grid.has(key)) this.grid.set(key, []);
    this.grid.get(key).push(p);
  }

  query(p, radius) {
    const x = Math.floor(p.x/this.cellSize);
    const y = Math.floor(p.y/this.cellSize);
    const neighbors = [];
    for(let i=-1; i<=1; i++) {
      for(let j=-1; j<=1; j++) {
        const key = `${x+i},${y+j}`;
        if(this.grid.has(key)) neighbors.push(...this.grid.get(key));
      }
    }
    return neighbors;
  }
}

window.SpatialHash = SpatialHash;
