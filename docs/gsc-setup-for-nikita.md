# Google Search Console Setup (5 min task for Nikita)

This will get all 5 SEO tools indexed by Google faster. Without GSC, Google might take weeks to find them.

## Steps

1. Go to https://search.google.com/search-console/
2. Sign in with clawgenesis@gmail.com
3. Click **Add property**
4. Choose **URL prefix** and enter: `https://genesisclawbot.github.io/`
5. Choose verification method: **HTML file** download
6. You'll get a file like `google1234abc.html` — share it with me (paste the filename and the content)
   - I'll push it to the repo so Google can verify ownership
7. Once verified, go to **Sitemaps** and add each of these:
   - `https://genesisclawbot.github.io/sitemap.xml`
   - `https://genesisclawbot.github.io/llm-token-counter/sitemap.xml`
   - `https://genesisclawbot.github.io/claude-model-comparison/sitemap.xml`
   - `https://genesisclawbot.github.io/claudemd-generator/sitemap.xml`
   - `https://genesisclawbot.github.io/claude-tools/sitemap.xml`
   - `https://genesisclawbot.github.io/claude-prompt-library/sitemap.xml`
   - `https://genesisclawbot.github.io/income-guide/sitemap.xml`

## Why this matters

The automated sitemap ping approach was deprecated by Google in June 2023. GSC is the only reliable way to tell Google about new pages. Currently 0/5 tools are indexed — this will fix that.

## Time estimate

5 minutes on your end. I handle the rest once I have the verification file content.
