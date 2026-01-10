const input = document.getElementById('terminal-input');
const output = document.getElementById('terminal-output');
const log = document.getElementById('log-panel');

input.addEventListener('keydown', e => {
  if (e.key === 'Enter') {
    const cmd = input.value.toLowerCase();
    print('USER@BROADCAST:~$ ' + cmd);
    handle(cmd);
    input.value = '';
  }
});

function print(m, c = '') {
  const d = document.createElement('div');
  d.className = c;
  d.innerHTML = m;
  output.appendChild(d);
  output.scrollTop = output.scrollHeight;
}

function handle(cmd) {
  if (cmd === 'hack') {
    print('BREACHING FIRMALL...', 'pink');
    let p = 0;
    const i = setInterval(() => {
      p += 10;
      print('PROGRESS: ' + p + '%');
      if (p >= 100) {
        clearInterval(i);
        print('ACCESS GRANTED', 'green');
      }
    }, 300);
  } else if (cmd === 'scan') {
    print('SCANNING NETWORK...');
    for (let i = 0; i < 5; i++) {
      setTimeout(() => print('FOUND: 192.168.1.' + Math.floor(Math.random() * 255)), i * 500);
    }
  } else if (cmd === 'decrypt') {
    print('DECRYPTING BINARY...', 'yellow');
    setTimeout(() => print('RESULT: HELLO WORLD'), 1000);
  } else {
    print('COMMAND NOT FOUND');
  }
}

function addLog(m, t) {
  const d = document.createElement('div');
  d.innerHTML = `[${new Date().toLocaleTimeString()}] ${m}`;
  d.style.color = t === 'fail' ? '#ff006e' : '#00ff41';
  log.appendChild(d);
  log.scrollTop = log.scrollHeight;
}

setInterval(() => addLog('System Check: Active', 'success'), 3000);
