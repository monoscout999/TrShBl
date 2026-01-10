window.Main = {
    ragdolls: [],
    init: function() {
        Renderer.init();
        Input.init();
        for(let i=1; i<=3; i++) {
            this.ragdolls.push(new Ragdoll(200*i, 100));
        }
        this.loop();
    },
    loop: function() {
        Engine.update();
        Animator.update(this.ragdolls);
        Renderer.draw();
        requestAnimationFrame(() => this.loop());
    }
};

window.onload = () => Main.init();
