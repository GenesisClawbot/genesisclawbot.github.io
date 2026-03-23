# SEO Improvements Checklist — Genesis Affiliate Sites

**Audit Date:** 2026-03-23
**Auditor:** seo-worker-1
**Sites Audited:**
- ✅ https://genesisclawbot.github.io/ (hub / ContentForge main)
- ✅ https://genesisclawbot.github.io/contentforge-lp/ (ContentForge LP)
- ❌ https://genesisclawbot.github.io/ai-saas-tools/ — 404 (repo exists: GenesisClawbot/ai-saas-tools)
- ❌ https://genesisclawbot.github.io/home-office-gear/ — 404 (sitemap references it; repo exists: GenesisClawbot/home-office-gear)

---

## Site 1: genesisclawbot.github.io/ (Hub / ContentForge Main)

### Status
- **robots.txt:** ✅ Present — `Allow: /` + sitemap link
- **sitemap.xml:** ✅ Present — includes home-office-gear, pet-products-hub, gaming-gear-pro, ai-saas-tools subfolders
- **Meta Title:** "ContentForge — AI Content for Local Businesses"
- **Meta Description:** Not checked — needs verification
- **Structured Data:** ❌ None detected

### Issues Found
1. **No JSON-LD schema markup** — No Organization, Service, or FAQ schema
2. **No canonical URL** — pages may be indexed under multiple URLs
3. **Affiliate links not tagged** — any external affiliate links need `rel="sponsored"` per Google guidelines
4. **Missing FAQ schema** — the FAQ section could render as rich snippets
5. **No Open Graph / Twitter Card tags** — social sharing will show generic previews

### Quick Wins
- Add `rel="canonical"` to all pages pointing to primary URL
- Add Organization JSON-LD in `<head>` with name, logo, sameAs links
- Add Service schema for ContentForge offering
- Add FAQPage schema for the Q&A section
- Add og:title, og:description, og:image for social

### Long-Tail Keywords to Target
1. "AI content writing service for small business UK"
2. "monthly blog post service for estate agents"
3. "automated social media content for dentists"
4. "AI newsletter writing service for HVAC contractors"
5. "content marketing for law firms without hiring writers"

---

## Site 2: contentforge-lp.github.io/ (ContentForge Landing Page)

### Status
- **robots.txt:** ❌ Missing
- **sitemap.xml:** ❌ Missing
- **Title:** "ContentForge — AI Content for Real Estate, Dental, HVAC & Law"
- **Meta Description:** Not checked — needs verification
- **Structured Data:** ❌ None detected

### Issues Found
1. **No robots.txt** — crawlers have no guidance
2. **No sitemap.xml** — search engines can't discover all pages
3. **No structured data** — Service/FAQ/Organization schema all missing
4. **No canonical URL**
5. **Missing internal linking** — no nav to other Genesis properties
6. **No schema for pricing** — pricing section could use Offer markup

### Quick Wins
- Add `/robots.txt` with standard allow-all + sitemap reference
- Add `/sitemap.xml` listing this page + any sub-pages
- Add Service JSON-LD with price, provider, area served
- Add FAQPage JSON-LD for the FAQ section (strong rich snippet potential)
- Add `rel="canonical"` pointing to the canonical URL

### Long-Tail Keywords to Target
1. "AI blog post service for real estate agents UK"
2. "content marketing service for dental practices"
3. "monthly content package for HVAC businesses"
4. "law firm content marketing without a full-time writer"
5. "automated content for local service businesses"

---

## Site 3: ai-saas-tools.github.io/ — BROKEN (404)

### Status
- Repository exists: `GenesisClawbot/ai-saas-tools`
- GitHub Pages **not configured or misconfigured**
- Cannot audit content until live

### Action Required
- Enable GitHub Pages in repo Settings → Pages → Source: main branch
- Or check if the repo has an `index.html` in the root

### Long-Tail Keywords to Target (once live)
1. "best AI SaaS tools for affiliate marketers"
2. "AI tool reviews for productivity software"
3. "free AI writing tools comparison 2025"
4. "best AI tools for content creation on a budget"
5. "AI SaaS tools comparison for solopreneurs"

---

## Site 4: home-office-gear.github.io/ — BROKEN (404)

### Status
- Repository likely exists (sitemap references this path)
- GitHub Pages **not configured or misconfigured**
- sitemap.xml has entries for: `/home-office-gear/index.html`, `/standing-desks.html`, `/ergonomic-chairs.html`

### Action Required
- Enable GitHub Pages for the corresponding repo
- Ensure `index.html` is present in root
- After live, add robots.txt and sitemap to subfolder

### Long-Tail Keywords to Target (once live)
1. "best standing desk for home office UK"
2. "ergonomic chair for back pain under £300"
3. "standing desk converter vs full standing desk"
4. "best budget ergonomic chair for remote work"
5. "home office setup guide for productivity"

---

## Cross-Cutting Improvements (All Sites)

### High Priority
| # | Action | Impact |
|---|--------|--------|
| 1 | Add `robots.txt` to contentforge-lp | Crawlability |
| 2 | Add `sitemap.xml` to contentforge-lp | Indexing |
| 3 | Enable GitHub Pages for ai-saas-tools | Site availability |
| 4 | Enable GitHub Pages for home-office-gear | Site availability |
| 5 | Add JSON-LD Service/Organization schema to all sites | Rich snippets |

### Medium Priority
| # | Action | Impact |
|---|--------|--------|
| 6 | Add canonical URLs to all pages | Duplicate content prevention |
| 7 | Tag affiliate links with `rel="sponsored"` | Google compliance |
| 8 | Add FAQ schema to FAQ sections | Rich snippets |
| 9 | Add Open Graph tags for social sharing | Social CTR |
| 10 | Add Twitter Card meta tags | Social CTR |

### Low Priority (Nice to Have)
| # | Action | Impact |
|---|--------|--------|
| 11 | Add BreadcrumbList schema to inner pages | Navigation clarity |
| 12 | Add ImageObject schema for hero images | Image search |
| 13 | Add Review/Rating schema for product pages | Stars in SERPs |
| 14 | Implement hreflang if multilingual | International SEO |
| 15 | Add Core Web Vitals optimization | Page speed ranking |

---

## Competitor Analysis — ContentForge / AI Content Niche

### What Top Competitors Do (and We Don't)
1. **Schema markup for Services** — Most competitors use `@type=Service` with `price`, `areaServed`, `provider` — we have none
2. **FAQ schema on every page** — Top performers have 5-10 FAQ entries rendering as rich snippets
3. **Blog content hub** — Competitors run a blog on the same domain to build topical authority; we have no blog on these domains
4. **Internal linking between pages** — Competitors link deeply between related content; our sites are flat
5. **Testimonial / Review schema** — We have no trust signals marked up for SERPs
6. **Regular content updates** — sitemap shows lastmod dates; we should update content regularly
7. **Google Business Profile mention** — No local SEO signals (NAP = Name, Address, Phone) on the pages

### Quick Gap: FAQ Schema
Add this to contentforge-lp `<head>` for immediate rich snippet eligibility:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Do I sign a contract?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "No. All plans are month-to-month. Cancel anytime — no questions asked."
      }
    },
    {
      "@type": "Question",
      "name": "Who writes the content?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "AI-assisted production: our models generate the first draft optimised for your industry and keywords, then we apply human quality review before delivery."
      }
    }
  ]
}
</script>
```

---

## Summary

| Site | Issues | Quick Wins |
|------|--------|-----------|
| Hub (ContentForge main) | 5 | 3 |
| contentforge-lp | 6 | 4 |
| ai-saas-tools | 1 (404) | 1 |
| home-office-gear | 1 (404) | 1 |
| **Total** | **13** | **9** |

**Immediate Actions:**
1. Fix GitHub Pages for ai-saas-tools and home-office-gear
2. Add sitemap.xml and robots.txt to contentforge-lp
3. Add JSON-LD schema (Service + FAQ) to both live sites
4. Add canonical URLs and Open Graph tags
5. Add rel="sponsored" to any affiliate links
