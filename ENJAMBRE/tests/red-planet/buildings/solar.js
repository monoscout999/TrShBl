class SolarPanel extends Building {
    constructor(x, y) {
        super(x, y);
        this.output = 0.5;
    }

    update() {
        if(Game.time < Game.dayCycle/2) {
            Resources.add('power', this.output);
        }
    }

    static getCost() {
        return { metal: 20 };
    }
}

window.SolarPanel = SolarPanel;
