window.Animator = {
    update: function (ragdolls) {
        const time = Date.now() * 0.005;
        ragdolls.forEach(r => {
            // Only move feet if they are somewhat grounded (y > height - 60)
            // And apply a smaller force
            if (r.lFoot.y > Engine.height - 60) {
                r.lFoot.x += Math.sin(time) * 0.5;
                r.lFoot.y -= Math.max(0, Math.sin(time)) * 2; // lift foot
            }
            if (r.rFoot.y > Engine.height - 60) {
                r.rFoot.x += Math.cos(time) * 0.5;
                r.rFoot.y -= Math.max(0, Math.cos(time)) * 2; // lift foot
            }
        });
    }
};
