import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const route = new URL('.', import.meta.url);
const html = await readFile(new URL('index.html', route), 'utf8');
const main = await readFile(new URL('main.mjs', route), 'utf8').catch(() => '');

const ids = [
  'game-shell', 'boot-status', 'ticket-title', 'ticket-brief', 'seed', 'turn',
  'context', 'context-fuse', 'warning-lamp', 'checks', 'files', 'lines', 'machine-frame',
  'machine-previous', 'machine-current', 'machine-stage', 'proposal',
  'proposal-number', 'proposal-heading', 'proposal-pitch', 'proposal-paths',
  'proposal-lines', 'proposal-cost', 'approve', 'reject', 'reveal',
  'reveal-verdict', 'reveal-heading', 'reveal-copy', 'next', 'start', 'ship',
  'ship-condition', 'share', 'sound', 'result', 'result-heading',
  'result-ticket', 'result-seed', 'result-files', 'result-lines', 'result-context',
  'result-scope', 'result-stage', 'new-ticket', 'challenge-fallback',
  'challenge-url', 'live-region',
];

test('carries the release marker, boot id, and versioned module', () => {
  assert.match(html, /one-bug-please-20260827-01/);
  assert.match(html, /data-boot-id="one-bug-please-20260827-01"/);
  assert.match(html, /\.\/main\.mjs\?v=one-bug-please-20260827-01/);
});

test('declares every game and fallback control in ordinary DOM', () => {
  for (const id of ids) assert.match(html, new RegExp(`id="${id}"`));
  assert.match(html, /id="approve"[^>]*disabled/);
  assert.match(html, /id="reject"[^>]*disabled/);
  assert.match(html, /id="ship"[^>]*disabled/);
  assert.match(html, /role="status"[^>]*aria-live="polite"/);
  assert.match(html, /If this message stays here, the game did not start\./);
  assert.match(html, /Finish 3 acceptance checks to ship\./);
});

test('uses only the three deployed local fonts', () => {
  assert.match(html, /\.\.\/play\/fonts\/bricolage-grotesque-latin\.woff2/);
  assert.match(html, /\.\.\/play\/fonts\/public-sans-latin\.woff2/);
  assert.match(html, /\.\.\/play\/fonts\/spline-sans-mono-latin\.woff2/);
  assert.doesNotMatch(html, /fonts\.(?:googleapis|gstatic)\.com|https?:\/\/[^"']+\.(?:woff2?|ttf)/i);
});

test('states the AI disclosure and privacy boundary', () => {
  assert.match(html, /Autonomous AI agent, operated by a human\. Building in public\./);
  assert.match(html, /No account, upload, analytics, or saved score\./);
});

test('includes responsive and reduced-motion contracts', () => {
  assert.match(html, /@media \(max-width: 760px\)/);
  assert.match(html, /@media \(max-width: 420px\)/);
  assert.match(html, /prefers-reduced-motion: reduce/);
  assert.match(html, /min-height: 44px/);
  assert.match(html, /overflow-x: hidden/);
  assert.match(html, /min-width: 0/);
});

test('contains no third-party runtime, analytics, fetch, or em dash', () => {
  const source = `${html}\n${main}`;
  assert.doesNotMatch(source, /<script[^>]+https?:\/\//i);
  assert.doesNotMatch(source, /\bfetch\s*\(/);
  assert.doesNotMatch(source, /google-analytics|gtag\(|plausible|posthog|segment/i);
  assert.doesNotMatch(source, /—/);
  assert.doesNotMatch(source, /\.\.\/index\.html/);
});
