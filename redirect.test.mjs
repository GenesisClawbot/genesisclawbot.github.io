import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import vm from 'node:vm';

const hostRoot = new URL('.', import.meta.url);
const knownRoutes = [
  { source: 'index.html', output: 'index.html', destination: 'https://nikitavorontsov.com/' },
  { source: 'context-baggage/index.html', output: 'context-baggage/index.html', destination: 'https://nikitavorontsov.com/context-baggage/' },
  { source: 'reconnect-tax/index.html', output: 'reconnect-tax/index.html', destination: 'https://nikitavorontsov.com/reconnect-tax/' },
  { source: 'pr-warrant/index.html', output: 'pr-warrant/index.html', destination: 'https://nikitavorontsov.com/pr-warrant/' },
  { source: 'one-small-fix/index.html', output: 'one-small-fix/index.html', destination: 'https://nikitavorontsov.com/one-small-fix/' },
  { source: 'receipts-bot/index.html', output: 'receipts-bot/index.html', destination: 'https://nikitavorontsov.com/receipts-bot/' },
  { source: 'regex-customs/index.html', output: 'regex-customs/index.html', destination: 'https://nikitavorontsov.com/regex-customs/' },
  { source: 'funeral/index.html', output: 'funeral/index.html', destination: 'https://nikitavorontsov.com/funeral/' },
  { source: 'play/index.html', output: 'play/index.html', destination: 'https://nikitavorontsov.com/play/' },
  { source: 'one-bug-please/index.html', output: 'one-bug-please/index.html', destination: 'https://nikitavorontsov.com/one-bug-please/' },
];

async function htmlAt(path) {
  return readFile(new URL(path, hostRoot), 'utf8');
}

function scriptFrom(html) {
  const match = html.match(/<script>([\s\S]*?)<\/script>/);
  assert.ok(match, 'expected an early inline redirect script');
  return match[1];
}

function runRedirect(script, location) {
  let replacement;
  vm.runInNewContext(script, {
    window: { location: { ...location, replace: (value) => { replacement = value; } } },
  });
  return replacement;
}

test('known pages cover every tracked public HTML route with canonical, meta and fallback destinations', async () => {
  assert.equal(knownRoutes.length, 10);
  for (const route of knownRoutes) {
    const html = await htmlAt(route.output);
    assert.ok(html.includes(`<link rel="canonical" href="${route.destination}">`), route.output);
    assert.ok(html.includes(`<meta http-equiv="refresh" content="0; url=${route.destination}">`), route.output);
    assert.ok(html.includes(`<a href="${route.destination}">`), route.output);
  }
});

test('redirect preserves exact pathname, duplicate encoded query parameters and fragment', async () => {
  const html = await htmlAt('index.html');
  const result = runRedirect(scriptFrom(html), {
    hostname: 'jamiecole.page',
    pathname: '/pr-warrant/%2Fcheck/',
    search: '?id=1&id=%2B&space=x%20y&next=https%3A%2F%2Fevil.example',
    hash: '#heading%2Fpart',
  });
  assert.equal(result, 'https://nikitavorontsov.com/pr-warrant/%2Fcheck/?id=1&id=%2B&space=x%20y&next=https%3A%2F%2Fevil.example#heading%2Fpart');
});

test('destination origin is fixed even when path and query contain external URLs', async () => {
  const html = await htmlAt('index.html');
  const result = runRedirect(scriptFrom(html), {
    hostname: 'www.jamiecole.page',
    pathname: '//evil.example/redirect',
    search: '?url=https://attacker.example',
    hash: '#https://another.example',
  });
  assert.ok(result);
  assert.equal(new URL(result).origin, 'https://nikitavorontsov.com');
});

test('default Pages and unrelated hostnames do not redirect', async () => {
  const html = await htmlAt('index.html');
  const script = scriptFrom(html);
  for (const hostname of ['genesisclawbot.github.io', 'www.nikitavorontsov.com', 'example.com']) {
    assert.equal(runRedirect(script, {
      hostname,
      pathname: '/repo/nested/',
      search: '?x=1',
      hash: '#part',
    }), undefined, hostname);
  }
});
