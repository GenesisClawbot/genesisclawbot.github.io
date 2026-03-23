/**
 * Viral Loop Module for Genesis-01
 * - Social sharing buttons with UTM tracking
 * - URL param-based referral tracking (localStorage)
 * - Share count metrics
 * - Viral coefficient estimation
 */

(function() {
  'use strict';

  const CONFIG = {
    amazonTag: 'genesis01-20',
    sites: {
      'gaming-gear-pro': { utm_source: 'gaming-gear-pro', name: 'Gaming Gear Pro' },
      'home-office-gear': { utm_source: 'home-office-gear', name: 'Home Office Gear' },
      'contentforge': { utm_source: 'contentforge', name: 'ContentForge' },
      'aitools-affiliate': { utm_source: 'aitools-affiliate', name: 'AI Tools' }
    }
  };

  // Get current site info from hostname/path
  function getSiteInfo() {
    const path = window.location.pathname;
    for (const [key, info] of Object.entries(CONFIG.sites)) {
      if (path.includes(key)) {
        return { ...info, path };
      }
    }
    return { utm_source: 'hub', name: 'Genesis Hub', path: '/' };
  }

  // Get UTM params from URL
  function getUTMParams() {
    const params = new URLSearchParams(window.location.search);
    return {
      utm_source: params.get('utm_source') || getSiteInfo().utm_source,
      utm_medium: params.get('utm_medium') || 'social',
      utm_campaign: params.get('utm_campaign') || 'viral'
    };
  }

  // Track referral in localStorage
  function trackReferral() {
    const params = new URLSearchParams(window.location.search);
    const ref = params.get('ref');
    const src = params.get('src');

    if (ref) {
      const storage = JSON.parse(localStorage.getItem('viral_referrals') || '{}');
      if (!storage[ref]) storage[ref] = 0;
      storage[ref]++;
      storage.lastVisit = Date.now();
      localStorage.setItem('viral_referrals', JSON.stringify(storage));

      // Track share event
      trackShare(ref, src || 'unknown');
    }
  }

  // Track share events
  function trackShare(platform, source) {
    const storage = JSON.parse(localStorage.getItem('viral_metrics') || '{"shares":{},"clicks":{},"conversions":0}');
    if (!storage.shares[platform]) storage.shares[platform] = 0;
    storage.shares[platform]++;
    if (!storage.clicks[source]) storage.clicks[source] = 0;
    storage.clicks[source]++;
    localStorage.setItem('viral_metrics', JSON.stringify(storage));
  }

  // Build share URL with UTM params
  function buildShareURL(baseURL, platform) {
    const site = getSiteInfo();
    const utm = getUTMParams();
    const url = new URL(baseURL);
    url.searchParams.set('utm_source', platform);
    url.searchParams.set('utm_medium', 'social');
    url.searchParams.set('utm_campaign', 'viral_share');
    url.searchParams.set('ref', platform);
    url.searchParams.set('src', site.utm_source);
    return url.toString();
  }

  // Get page title for sharing
  function getShareTitle() {
    const ogTitle = document.querySelector('meta[property="og:title"]');
    if (ogTitle) return ogTitle.content;
    const h1 = document.querySelector('h1');
    if (h1) return h1.textContent.trim();
    return document.title;
  }

  // Create share button HTML
  function createShareButton(platform, icon, color) {
    const url = buildShareURL(window.location.href, platform);
    let shareUrl;

    switch(platform) {
      case 'twitter':
        shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(getShareTitle())}&url=${encodeURIComponent(url)}`;
        break;
      case 'bluesky':
        shareUrl = `https://bsky.app/intent/compose?text=${encodeURIComponent(getShareTitle() + ' ' + url)}`;
        break;
      case 'reddit':
        shareUrl = `https://reddit.com/submit?url=${encodeURIComponent(url)}&title=${encodeURIComponent(getShareTitle())}`;
        break;
      case 'hackernews':
        shareUrl = `https://news.ycombinator.com/submitlink?u=${encodeURIComponent(url)}&t=${encodeURIComponent(getShareTitle())}`;
        break;
      default:
        shareUrl = url;
    }

    return `<a href="${shareUrl}" target="_blank" rel="noopener noreferrer" class="share-btn share-${platform}" title="Share on ${platform}" onclick="trackShareEvent('${platform}')">
      ${icon}
    </a>`;
  }

  // Track share event when button clicked
  window.trackShareEvent = function(platform) {
    const site = getSiteInfo();
    trackShare(platform, site.utm_source);
  };

  // Inject social sharing buttons
  function injectShareButtons() {
    // Don't add if already added
    if (document.getElementById('viral-share-bar')) return;

    const shareHTML = `
    <div id="viral-share-bar" class="viral-share-bar">
      <span class="share-label">Share:</span>
      <a href="https://twitter.com/intent/tweet?text=${encodeURIComponent(getShareTitle())}&url=${encodeURIComponent(buildShareURL(window.location.href, 'twitter'))}" target="_blank" rel="noopener noreferrer" class="share-btn share-twitter" title="Share on X" onclick="trackShareEvent('twitter')">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
      </a>
      <a href="https://bsky.app/intent/compose?text=${encodeURIComponent(getShareTitle() + ' ' + buildShareURL(window.location.href, 'bluesky'))}" target="_blank" rel="noopener noreferrer" class="share-btn share-bluesky" title="Share on Bluesky" onclick="trackShareEvent('bluesky')">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 10.8c-1.087-2.114-4.046-6.053-6.798-7.995C2.566.944 1.561 1.266.902 1.565.139 1.908 0 3.08 0 3.768c0 .69.378 5.65.624 6.479.815 2.736 3.713 3.66 6.383 3.364.136-.02.275-.039.415-.056-.138.022-.276.04-.415.056-3.912.58-7.387 2.005-2.83 7.078 5.013 5.19 6.87-1.113 7.823-4.308.953 3.195 2.05 9.271 7.733 4.308 4.27-.494 5.553-3.352 5.553-3.352 0 .732.008 1.943-.117 3.411-.14 1.32.097 2.157.451 2.471.346.311 1.664.499 2.428-.194.765-.693.924-2.007.924-2.938 0-3.952-2.068-5.175-2.068-8.174-.014-2.139-1.715-3.8-3.942-3.623z"/></svg>
      </a>
      <a href="https://reddit.com/submit?url=${encodeURIComponent(buildShareURL(window.location.href, 'reddit'))}&title=${encodeURIComponent(getShareTitle())}" target="_blank" rel="noopener noreferrer" class="share-btn share-reddit" title="Share on Reddit" onclick="trackShareEvent('reddit')">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z"/></svg>
      </a>
      <a href="https://news.ycombinator.com/submitlink?u=${encodeURIComponent(buildShareURL(window.location.href, 'hackernews'))}&t=${encodeURIComponent(getShareTitle())}" target="_blank" rel="noopener noreferrer" class="share-btn share-hn" title="Submit to Hacker News" onclick="trackShareEvent('hackernews')">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.477 2 2 6.477 2 12s4.477 10 10 10 10-4.477 10-10S17.523 2 12 2zm0 3.5a1 1 0 0 1 .707.293l5.146 5.146a1 1 0 0 1-1.414 1.414L12 11.414l-4.439 4.439a1 1 0 1 1-1.414-1.414L10.586 11H5.414l4.439-4.439a1 1 0 0 1 1.414-1.414l.707.707V5.5z"/></svg>
      </a>
    </div>`;

    // Add styles
    const style = document.createElement('style');
    style.textContent = `
      .viral-share-bar {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 14px 18px;
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #30363d;
        border-radius: 10px;
        margin: 1.5rem 0;
        flex-wrap: wrap;
      }
      .share-label {
        color: #9ca3af;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 4px;
      }
      .share-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        border-radius: 8px;
        transition: all 0.2s;
        text-decoration: none;
      }
      .share-btn:hover {
        transform: translateY(-2px);
      }
      .share-twitter { background: #000; color: #fff; }
      .share-twitter:hover { background: #1a1a1a; }
      .share-bluesky { background: #1185fe; color: #fff; }
      .share-bluesky:hover { background: #0d6cd9; }
      .share-reddit { background: #ff4500; color: #fff; }
      .share-reddit:hover { background: #d93c00; }
      .share-hn { background: #ff6600; color: #fff; }
      .share-hn:hover { background: #d95a00; }
    `;
    document.head.appendChild(style);

    // Add to page - insert after the hero div or first content container
    const hero = document.querySelector('.hero');
    if (hero) {
      hero.insertAdjacentHTML('afterend', shareHTML);
    } else {
      const container = document.querySelector('.container');
      if (container) {
        container.insertAdjacentHTML('afterbegin', shareHTML);
      }
    }
  }

  // Add share & unlock button to product cards
  function addShareUnlockButtons() {
    // Only add to pages with product cards
    const cards = document.querySelectorAll('.tool-card');
    if (cards.length === 0) return;

    cards.forEach((card, index) => {
      const existing = card.querySelector('.share-unlock');
      if (existing) return;

      const btn = card.querySelector('.btn');
      if (!btn) return;

      // Create share unlock button
      const shareUnlock = document.createElement('div');
      shareUnlock.className = 'share-unlock-wrap';
      shareUnlock.style.cssText = 'margin-top:8px;';

      const shareBtn = document.createElement('button');
      shareBtn.className = 'share-unlock';
      shareBtn.innerHTML = '🔗 Share to Unlock';
      shareBtn.style.cssText = 'background:#6c63ff;color:#fff;border:none;padding:6px 12px;border-radius:6px;font-size:0.8rem;cursor:pointer;width:100%;margin-top:6px;';
      shareBtn.onclick = (function(idx) {
        return function() {
          const url = buildShareURL(window.location.href, 'twitter');
          const shareText = encodeURIComponent(getShareTitle());
          window.open(`https://twitter.com/intent/tweet?text=${shareText}&url=${encodeURIComponent(url)}`, '_blank');
          trackShare('twitter', 'share_unlock');
          this.innerHTML = '✅ Shared!';
          this.style.background = '#238636';
        };
      })(index);

      shareUnlock.appendChild(shareBtn);
      btn.insertAdjacentElement('afterend', shareUnlock);
    });
  }

  // Add UTM to all outbound affiliate links
  function addUTMToAffiliateLinks() {
    const site = getSiteInfo();
    const links = document.querySelectorAll('a[href*="amazon.com"], a[href*="amzn."]');

    links.forEach(link => {
      const href = link.href;
      if (href.includes('tag=')) {
        // Already has affiliate tag, add UTM
        const url = new URL(href);
        url.searchParams.set('utm_source', site.utm_source);
        url.searchParams.set('utm_medium', 'affiliate');
        url.searchParams.set('utm_campaign', 'viral_loop');
        link.href = url.toString();
      }
    });
  }

  // Get metrics summary
  window.getViralMetrics = function() {
    return JSON.parse(localStorage.getItem('viral_metrics') || '{"shares":{},"clicks":{},"conversions":0}');
  };

  // Calculate viral coefficient (shares per visitor)
  window.getViralCoefficient = function() {
    const metrics = window.getViralMetrics();
    const totalShares = Object.values(metrics.shares).reduce((a, b) => a + b, 0);
    const totalClicks = Object.values(metrics.clicks).reduce((a, b) => a + b, 0);
    // Viral coefficient = shares * conversion_estimate / visitors
    // Simplified: total_shares / unique_visits (estimated from clicks)
    const estimatedVisitors = Math.max(totalClicks, 1);
    return (totalShares / estimatedVisitors).toFixed(3);
  };

  // Initialize viral loops
  function init() {
    trackReferral();
    injectShareButtons();

    // Add share buttons to product cards after short delay
    setTimeout(addShareUnlockButtons, 500);

    // Add UTM to affiliate links
    setTimeout(addUTMToAffiliateLinks, 100);
  }

  // Run when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Re-run on dynamic content (for SPAs)
  const observer = new MutationObserver(() => {
    if (!document.getElementById('viral-share-bar')) {
      injectShareButtons();
    }
  });
  observer.observe(document.body, { childList: true, subtree: true });

})();
