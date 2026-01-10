window.OS = {
    apps: {},
    wm: null,
    fs: null
};

document.addEventListener('DOMContentLoaded', () => {
    // Clock
    setInterval(() => {
        const d = new Date();
        document.getElementById('clock').innerText = d.toLocaleTimeString();
    }, 1000);

    // Start Menu
    document.getElementById('start-btn').onclick = () => {
        const menu = document.getElementById('start-menu');
        menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
    };

    // Auto-open Welcome App?
    setTimeout(() => {
        if (OS.wm && OS.apps.terminal) OS.wm.open('terminal');
    }, 500);
});
