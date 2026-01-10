window.Interface = {
  selectedBuild: null,
  init: function () {
    const menu = document.getElementById('build-menu');
    const types = ['SolarPanel', 'Habitat', 'Greenhouse', 'Mine', 'WaterExtractor', 'Battery'];
    types.forEach(t => {
      const btn = document.createElement('div');
      btn.className = 'build-btn';
      btn.innerText = t;
      btn.onclick = () => {
        this.selectedBuild = t;
        document.querySelectorAll('.build-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      };
      menu.appendChild(btn);
    });

    Game.canvas.onclick = (e) => {
      if (this.selectedBuild) {
        const x = Math.floor(e.offsetX / Game.tileSize);
        const y = Math.floor(e.offsetY / Game.tileSize);
        const Cost = window[this.selectedBuild].getCost();
        if (Resources.consume('metal', Cost.metal)) {
          const b = new window[this.selectedBuild](x, y);
          if (Grid.placeBuilding(x, y, b)) Game.buildings.push(b);
          else Resources.add('metal', Cost.metal);
        }
      }
    };
  },
  update: function () {
    document.getElementById('res-display').innerText = `Power: ${Math.floor(Resources.stock.power)} | Oxygen: ${Math.floor(Resources.stock.oxygen)} | Metal: ${Math.floor(Resources.stock.metal)} | Food: ${Math.floor(Resources.stock.meal)}`;
    requestAnimationFrame(() => this.update());
  }
};
