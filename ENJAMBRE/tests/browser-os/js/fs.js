class FileSystem {
  constructor() {
    if (!localStorage.getItem('os_files')) localStorage.setItem('os_files', JSON.stringify({}));
  }

  get files() {
    return JSON.parse(localStorage.getItem('os_files'));
  }

  write(name, content) {
    const files = this.files;
    files[name] = content;
    localStorage.setItem('os_files', JSON.stringify(files));
  }

  read(name) {
    return this.files[name] || '';
  }

  list() {
    return Object.keys(this.files);
  }
}

OS.fs = new FileSystem();
