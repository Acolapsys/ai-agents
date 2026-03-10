class Logger {
  log (...args) {
    console.log(...args)
  }
  error (...args) {
    console.error(...args)
  }
  warn (...args) {
    console.warn(...args)
  }
}

export default new Logger()