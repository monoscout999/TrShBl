window.InteractionMatrix = {
    matrix: {},
    init: function(types) {
        types.forEach(t1 => {
            this.matrix[t1] = {};
            types.forEach(t2 => {
                this.matrix[t1][t2] = Math.random() * 2 - 1;
            });
        });
    },
    getForce: function(t1, t2) {
        return this.matrix[t1][t2];
    }
};

window.InteractionMatrix.init(Config.types);
