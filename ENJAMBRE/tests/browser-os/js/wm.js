class WindowManager {
  constructor() {
    this.windows = [];
    this.zIndex = 100;
  }

  open(appId) {
    const app = OS.apps[appId];
    if (!app) return;

    const win = document.createElement('div');
    win.className = 'window';
    win.style.left = '50px';
    win.style.top = '50px';
    win.style.width = '400px';
    win.style.height = '300px';
    win.style.zIndex = ++this.zIndex;
    win.innerHTML = `<div class='title-bar'><span>${app.title}</span><button onclick='OS.wm.close(this.parentElement.parentElement)'>X</button></div><div class='content'></div>`;
    const content = win.querySelector('.content');
    app.init(content);
    document.getElementById('desktop').appendChild(win);

    this.makeDraggable(win);
  }

  close(winEl) {
    winEl.remove();
  }

  makeDraggable(win) {
    const title = win.querySelector('.title-bar');
    let isDragging = false;
    let offX, offY;

    title.addEventListener('mousedown', (e) => {
      isDragging = true;
      offX = e.offsetX;
      offY = e.offsetY;
      win.style.zIndex = ++this.zIndex;
    });

    window.addEventListener('mousemove', (e) => {
      if (isDragging) {
        win.style.left = (e.clientX - offX) + 'px';
        win.style.top = (e.clientY - offY) + 'px';
      }
    });

    window.addEventListener('mouseup', () => isDragging = false);
  }
}

OS.wm = new WindowManager();
