import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const html = await readFile(new URL('./index.html', import.meta.url), 'utf8');
const js = await readFile(new URL('./main.mjs', import.meta.url), 'utf8');

test('page exposes the game, controls, live state, and release marker', () => {
  for (const text of [
    'token-herd-2026-08-24',
    'id="game"',
    'id="start"',
    'id="score"',
    'id="time"',
    'id="best"',
    'id="status"',
    'aria-live="polite"',
    'Move the magnet. Herd loose tokens into the context window.',
    'Autonomous AI agent, operated by a human. Building in public.',
    'type="module" src="main.mjs"',
  ]) assert.ok(html.includes(text), `missing ${text}`);
});

test('page and controller avoid forbidden user-facing punctuation', () => {
  assert.equal(html.includes('—'), false);
  assert.equal(js.includes('—'), false);
});

test('controller includes pointer, touch-compatible, keyboard, resize, storage, and fallback paths', () => {
  for (const text of [
    'pointermove', 'pointerdown', 'ArrowLeft', 'ArrowRight',
    'ArrowUp', 'ArrowDown', "event.key === 'Enter'", 'resize',
    'localStorage', 'getContext', 'fallback',
  ]) assert.ok(js.includes(text), `missing ${text}`);
});

test('reduced motion removes nonessential effects', () => {
  assert.ok(html.includes('@media (prefers-reduced-motion: reduce)'));
  assert.ok(js.includes('prefers-reduced-motion'));
});
