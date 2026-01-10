class Habitat extends Building {
    constructor(x, y) {
        super(x, y);
        this.pop = 0;
    }

    update() {
        Resources.consume('power', 0.1);
        Resources.consume('oxygen', 0.1);
    }

    static getCost() {
        return { metal: 50 };
    }
}

window.Habitat = Habitat;
