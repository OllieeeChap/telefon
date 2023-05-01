var EventEmitter = require('events').EventEmitter;

// temps max entre deux nombres
const PULSE_TIMEOUT = 1000;

// temps avant de déclencher l'évenement final avec le numéro complet
const COMPOSE_TIMEOUT = 3000;

const PULSE_VALUES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0];

class Rotary extends EventEmitter {
  constructor() {
    super()
    this.value = '';
    this.pulseCount = 0;
  }
  onPulse() {
    // reception d'une impulsion
    if (this.pulseCount === 0) {
      this.emit('compositionstart');
    }
    this.pulseCount++;
    if (this.pulseTimeout) {
      clearTimeout(this.pulseTimeout);
    }
    if (this.composeTimeout) {
      clearTimeout(this.composeTimeout);
    }
    this.pulseTimeout = setTimeout(this.onPulseTimeout.bind(this), PULSE_TIMEOUT)
  }
  onPulseTimeout() {
    // last pulse received - store number
    const num = PULSE_VALUES[this.pulseCount - 1];
    this.value += num;
    this.pulseCount = 0;
    this.composeTimeout = setTimeout(this.onComposeTimeout.bind(this), COMPOSE_TIMEOUT)
  }
  onComposeTimeout() {
    // composition timeout
    this.emit('compositionend', this.value);
    this.value = '';
    this.pulseCount = 0;
  }
}

module.exports = Rotary