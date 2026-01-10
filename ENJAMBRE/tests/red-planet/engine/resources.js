window.Resources = {
  stock: {
    power: 100,
    oxygen: 100,
    meal: 50,
    water: 50,
    metal: 200
  },
  cap: {
    power: 500,
    oxygen: 500,
    meal: 200,
    water: 200,
    metal: 500
  },
  rates: {
    power: 0,
    oxygen: 0
  },
  init: function() {},
  update: function() {
    Object.keys(this.stock).forEach(key => {
      if (this.stock[key] > this.cap[key]) this.stock[key] = this.cap[key];
      if (this.stock[key] < 0) this.stock[key] = 0;
    });
  },
  add: function(type, amount) {
    this.stock[type] += amount;
  },
  consume: function(type, amount) {
    if (this.stock[type] >= amount) {
      this.stock[type] -= amount;
      return true;
    }
    return false;
  }
};
