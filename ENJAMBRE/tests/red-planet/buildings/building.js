class Building {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.active = true;
    }

    update() {}

    static getCost() {
        return { metal: 10 };
    }
}

window.Building = Building;
