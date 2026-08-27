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

test('carries the release marker, boot id, versioned module, and explicit favicon', () => {
  assert.match(html, /one-bug-please-20260827-01/);
  assert.match(html, /data-boot-id="one-bug-please-20260827-01"/);
  assert.match(html, /\.\/main\.mjs\?v=one-bug-please-20260827-01/);
  assert.match(html, /<link rel="icon" href="data:,">/);
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

const imageNames = Array.from({ length: 4 }, (_, index) => `machine-stage-${index}.webp`);
const soundNames = ['approve.mp3', 'reject.mp3', 'ship.mp3'];

test('bundles production image and optional sound files locally', async () => {
  for (const name of imageNames) {
    const bytes = await readFile(new URL(`assets/${name}`, route));
    assert.ok(bytes.length > 10_000, `${name} is too small to be a production image`);
    assert.ok(bytes.length <= 450_000, `${name} exceeds the route image budget`);
    assert.equal(bytes.subarray(0, 4).toString('ascii'), 'RIFF');
    assert.equal(bytes.subarray(8, 12).toString('ascii'), 'WEBP');
  }
  for (const name of soundNames) {
    const bytes = await readFile(new URL(`assets/${name}`, route));
    assert.ok(bytes.length > 1_000, `${name} is too small to be a production cue`);
    assert.ok(bytes.length <= 80_000, `${name} exceeds the cue budget`);
  }
});

test('references every machine image and sound cue from local source', () => {
  const source = `${html}\n${main}`;
  for (const name of [...imageNames, ...soundNames]) {
    assert.match(source, new RegExp(`\\.\\/assets\\/${name.replace('.', '\\.')}`));
  }
});

test('controller versions its pure import and handles seed URL replacement', () => {
  assert.match(main, /from '\.\/game\.mjs\?v=one-bug-please-20260827-01'/);
  assert.match(main, /crypto\.getRandomValues/);
  assert.match(main, /history\.replaceState/);
  assert.match(main, /searchParams\.get\('seed'\)/);
});

test('controller binds decisions, ship, shortcuts, focus, and live output', () => {
  assert.match(main, /addEventListener\('click'/);
  assert.match(main, /addEventListener\('keydown'/);
  assert.match(main, /case 'a':/i);
  assert.match(main, /case 'r':/i);
  assert.match(main, /case 's':/i);
  assert.match(main, /case 'Enter':/);
  assert.match(main, /\.focus\(\)/);
  assert.match(main, /requestAnimationFrame/);
});

test('controller guards stale builds and blocked storage', () => {
  assert.match(main, /one-bug-please-boot-id/);
  assert.match(main, /localStorage/);
  assert.match(main, /addEventListener\('storage'/);
  assert.match(main, /catch \{/);
});

test('controller handles reduced motion and all four machine assets', () => {
  assert.match(main, /matchMedia\('\(prefers-reduced-motion: reduce\)'\)/);
  assert.match(main, /addEventListener\('change'/);
  for (const name of imageNames) assert.match(main, new RegExp(`\\.\\/assets\\/${name.replace('.', '\\.')}`));
});

test('sound starts off and fails back to silence', () => {
  assert.match(html, /id="sound"[^>]*aria-pressed="false"/);
  assert.match(main, /new Audio\('\.\/assets\/approve\.mp3'\)/);
  assert.match(main, /new Audio\('\.\/assets\/reject\.mp3'\)/);
  assert.match(main, /new Audio\('\.\/assets\/ship\.mp3'\)/);
  assert.match(main, /\.play\(\)\.catch/);
  assert.match(main, /Sound unavailable\. Continuing in silence\./);
});

test('sharing uses Web Share, clipboard fallback, cancellation, and selectable URL', () => {
  assert.match(main, /navigator\.share/);
  assert.match(main, /navigator\.clipboard\.writeText/);
  assert.match(main, /Share sheet opened\. Nothing is sent until you choose a destination\./);
  assert.match(main, /Share cancelled\./);
  assert.match(main, /challengeFallback\.hidden = false/);
  assert.match(main, /challengeUrl\.select\(\)/);
});

test('new ticket removes the old seed before canonical boot', () => {
  assert.match(main, /searchParams\.delete\('seed'\)/);
  assert.match(main, /location\.assign/);
});
