const EventEmitter = require('events')

class Queue extends EventEmitter {
  constructor(basePath, baseIndex, concurrent = 5) {
    super()
    this.q = []
    this.paused = false
    this.inFlightCntr = 0
    this.fileCntr = baseIndex
    this.maxConcurrent = concurrent
  }

  // add item to the queue and write (if not already writing)
  add(data) {
    this.q.push(data)
    write()
  }

  // write next block from the queue (if not already writing)
  write() {
    while (!paused && this.q.length && this.inFlightCntr < this.maxConcurrent) {
      this.inFlightCntr++;
      let buf = this.q.shift();
      try {
        fs.writeFile(basePath + this.fileCntr++, buf, err => {
          this.inFlightCntr--
          if (err) {
            this.err(err);
          } else {
            // write more data
            this.write();
          }
        })
      } catch(e) {
        this.err(e);
      }
    }
  }

  err(e) {
    this.pause();
    this.emit('error', e)
  }

  pause() {
    this.paused = true;
  }

  resume() {
    this.paused = false;
    this.write();
  }
}

module.exports = { Queue }
