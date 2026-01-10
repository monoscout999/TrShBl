class Mine extends Building {
    constructor(x, y) {
        super(x, y);
    }

    update() {
        if (Resources.consume('power', 0.3)) {
            Resources.add('metal', 0.2);
        }
    }

    static getCost() {
        return { metal: 100 };
    }
}

window.Mine = Mine;
