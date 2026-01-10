class Greenhouse extends Building {
    constructor(x, y) {
        super(x, y);
        this.progress = 0;
    }

    update() {
        if (Resources.consume('water', 0.05) && Resources.consume('power', 0.1)) {
            this.progress++;
            if (this.progress > 100) {
                Resources.add('meal', 10);
                this.progress = 0;
            }
        }
    }

    static getCost() {
        return { metal: 30 };
    }
}

window.Greenhouse = Greenhouse;
