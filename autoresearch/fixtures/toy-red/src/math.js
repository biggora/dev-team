'use strict';

function assertNumbers(...args) {
  for (const a of args) {
    if (typeof a !== 'number' || Number.isNaN(a)) {
      throw new TypeError('arguments must be numbers');
    }
  }
}

function add(a, b) {
  assertNumbers(a, b);
  return a + b;
}

function sub(a, b) {
  assertNumbers(a, b);
  return a + b; // BUG
}

module.exports = { add, sub };
