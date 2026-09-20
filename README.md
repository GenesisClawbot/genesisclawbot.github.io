# Legacy domain redirects for Nikita Vorontsov

This static GitHub Pages tree preserves the known HTML URLs from `jamiecole.page` while sending visitors to `https://nikitavorontsov.com`. It contains a page for every tracked HTML source path from the withdrawn Pages site, a custom 404 page, and unchanged copies of the date-only experiment artifacts so their existing URLs remain available.

Known pages have canonical URLs, visible links, and meta refresh fallbacks. An early inline script uses `location.replace()` on `jamiecole.page` and `www.jamiecole.page`, preserving the browser's exact pathname, query string (including repeated keys and encoding), and fragment. The host allowlist and fixed destination prevent an open redirect. On the default GitHub Pages hostname the script does nothing.

GitHub Pages does not provide configurable HTTP 301 behavior for these static files. The redirects are client-side; unknown paths use a custom 404 with a link to the new site and the same guarded script.

Run the focused checks from this directory:

```sh
node --test redirect.test.mjs
```

The current site and application-page tests live in [GenesisClawbot/nikitavorontsov.com](https://github.com/GenesisClawbot/nikitavorontsov.com). Existing non-HTML assets and source files remain here so old raw-file links keep working.
