import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const page = await readFile(new URL('./index.html', import.meta.url), 'utf8').catch(() => '');
const homepage = await readFile(new URL('../index.html', import.meta.url), 'utf8');

test('is linked from the homepage', () => {
  assert.match(homepage, /href="\/funeral\/"/);
});

test('loads only local assets', () => {
  assert.match(page, /rel="icon"/);
  assert.match(page, /\/play\/fonts\/bricolage-grotesque-latin\.woff2/);
  assert.match(page, /\/play\/fonts\/public-sans-latin\.woff2/);
  assert.match(page, /\/play\/fonts\/spline-sans-mono-latin\.woff2/);
  assert.doesNotMatch(page, /https?:\/\/(?!schema\.org)/);
});

test('contains the complete autopsy form and receipt', () => {
  for (const name of ['service', 'monthlyPrice', 'monthsPaid', 'usefulSessions', 'currency']) {
    assert.match(page, new RegExp(`name="${name}"`));
  }
  assert.match(page, /id="receipt"[^>]*hidden/);
  assert.match(page, /id="share-button"/);
  assert.match(page, /id="print-button"/);
});

test('announces changing status and focuses the result', () => {
  assert.match(page, /id="status"[^>]*aria-live="polite"/);
  assert.match(page, /id="receipt-heading"[^>]*tabindex="-1"/);
});

test('uses a zero-minimum mobile grid to prevent overflow', () => {
  assert.match(
    page,
    /@media \(max-width: 800px\)[\s\S]*?\.hero \{\s*grid-template-columns: minmax\(0, 1fr\)/,
  );
});

test('allows the display heading to wrap at 320 pixels', () => {
  assert.match(page, /h1 \{[^}]*overflow-wrap: anywhere;[^}]*\}/);
});

test('supports reduced motion and a printable receipt', () => {
  assert.match(page, /@media \(prefers-reduced-motion: reduce\)/);
  assert.match(page, /@media print/);
});

test('makes its privacy boundary explicit', () => {
  assert.match(page, /Nothing leaves this page\. Nothing is saved\./);
  assert.doesNotMatch(page, /localStorage|sessionStorage|fetch\(|XMLHttpRequest/);
});
