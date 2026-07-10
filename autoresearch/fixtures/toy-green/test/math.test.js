'use strict';
const { test } = require('node:test');
const assert = require('node:assert');
const { add, sub } = require('../src/math.js');

test('add sums two numbers', () => {
  assert.strictEqual(add(2, 3), 5);
});

test('add throws TypeError on non-numbers', () => {
  assert.throws(() => add('2', 3), TypeError);
});

test('sub subtracts two numbers', () => {
  assert.strictEqual(sub(5, 3), 2);
});
