class Battery extends Building {
    constructor(x, y) {
        super(x, y);
        this.resources.cap.power += 500;
    }

    static getCost() {
        return { metal: 30 };
    }
}

window.Battery = Battery;
