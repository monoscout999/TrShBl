OS.apps.terminal = {
    title: 'Terminal',
    init: (el) => {
        el.style.background = 'black';
        el.style.color = 'lime';
        el.style.fontFamily = 'monospace';
        el.style.padding = '5px';
        el.innerHTML = `
            <div id='out'>Welcome to BrowserOS 3000<br>Type 'help' for commands.</div>
            <div style='display:flex'>
                <span>> </span>
                <input style='background:black;color:lime;border:none;flex:1;outline:none;font-family:monospace' 
                onkeydown='if(event.key==="Enter"){ OS.apps.terminal.run(this.value, this.parentElement.previousElementSibling); this.value=""; }' autofocus>
            </div>`;
        setTimeout(() => el.querySelector('input').focus(), 100);
    },
    run: (cmd, out) => {
        const args = cmd.trim().split(' ');
        const c = args[0];
        let res = '';

        if (c === 'help') res = 'cmds: ls, echo, clear, help';
        else if (c === 'ls') res = OS.fs.list().join('   ');
        else if (c === 'echo') res = args.slice(1).join(' ');
        else if (c === 'clear') { out.innerHTML = ''; return; }
        else if (c === '') return;
        else res = 'Unknown command: ' + c;

        out.innerHTML += `<div>> ${cmd}</div><div>${res}</div>`;
        out.scrollTop = out.scrollHeight;
    }
};
