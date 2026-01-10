window.App = {
  init: function() {
    Physics.init();
    Renderer.init();
    this.loop();
  },
  loop: function() {
    Physics.update();
    Renderer.draw(Physics.particles);
    requestAnimationFrame(() => App.loop());
  }
};

window.onload = () => App.init();
