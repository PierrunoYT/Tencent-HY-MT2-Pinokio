const assert = require('node:assert/strict');
const test = require('node:test');
const launcher = require('../pinokio.js');

const info = (installed, running = '', url) => ({
  exists: path => installed && path === 'app/env',
  running: path => path === running,
  local: () => ({url}),
});

test('menu follows install and server lifecycle', async () => {
  for (const [installed, running, url, expected] of [
    [false, '', undefined, 'Install'],
    [false, 'install.js', undefined, 'Installing'],
    [true, '', undefined, 'Start'],
    [true, 'start.js', undefined, 'Terminal'],
    [true, 'start.js', 'http://127.0.0.1:7860', 'Open Web UI'],
    [true, 'update.js', undefined, 'Updating'],
    [true, 'reset.js', undefined, 'Resetting'],
    [true, 'link.js', undefined, 'Deduplicating'],
  ]) {
    const menu = await launcher.menu({}, info(installed, running, url));
    assert.equal(menu[0].text, expected);
    assert.equal(menu[0].default, true);
  }
});

test('maintenance targets the installed environment and reuses installation', () => {
  assert.equal(require('../reset.js').run[0].params.path, 'app/env');
  assert.equal(require('../link.js').run[0].params.venv, 'app/env');
  assert.equal(require('../update.js').run[1].params.uri, 'install.js');
});

test('server URL capture supplies the first capture group', () => {
  const start = require('../start.js');
  const pattern = start.run[0].params.on[0].event;
  const match = 'Running on local URL:  http://127.0.0.1:7861'.match(new RegExp(pattern.slice(1, -1)));
  assert.equal(match[1], 'http://127.0.0.1:7861');
  assert.equal(start.run[1].params.url, '{{input.event[1]}}');
});
