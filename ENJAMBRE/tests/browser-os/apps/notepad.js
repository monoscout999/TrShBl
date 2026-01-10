OS.apps.notepad = {
    title: 'Notepad',
    init: (el) => {
        el.innerHTML = `
            <div style='display:flex;height:100%;flex-direction:column'>
                <div style='padding:5px;background:#C0C0C0;border-bottom:1px solid gray;display:flex;gap:5px'>
                    <input placeholder='Filename' id='note-name' style='flex:1'>
                    <button onclick='OS.apps.notepad.save(this)'>Save</button>
                    <button onclick='OS.apps.notepad.load(this)'>Load</button>
                </div>
                <textarea style='flex:1;resize:none;padding:5px;font-family:monospace' id='note-content'></textarea>
            </div>`;
    },
    save: (btn) => {
        const root = btn.closest('.window');
        const name = root.querySelector('#note-name').value;
        const content = root.querySelector('#note-content').value;
        if (name) {
            OS.fs.write(name, content);
            alert('Saved ' + name);
        } else {
            alert('Please enter a filename');
        }
    },
    load: (btn) => {
        const root = btn.closest('.window');
        const name = root.querySelector('#note-name').value;
        if (name) {
            const content = OS.fs.read(name);
            if (content !== undefined) {
                root.querySelector('#note-content').value = content;
            } else {
                alert('File not found');
            }
        }
    }
};
