class WaterExtractor extends Building {
    constructor(x, y) {
        super(x, y);
    }

    update() {
        if (Resources.consume('power', 0.2)) {
            Resources.add('water', 0.1);
        }
    }

    static getCost() {
        return { metal: 40 };
    }
}

window.WaterExtractor = WaterExtractor;
