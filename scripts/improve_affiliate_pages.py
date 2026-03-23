#!/usr/bin/env python3
"""Improve affiliate pages with better SEO, structured data, internal links, and content."""

import os
import re
from pathlib import Path

GITHUB_IO = "https://genesisclawbot.github.io"
AMAZON_TAG = "genesis01-20"

# Internal cross-links map
GAMING_CROSS_LINKS = {
    "gaming-keyboards.html": [
        ("Mechanical Switches Guide", "mechanical-switches-guide.html"),
        ("RGB Gaming Accessories", "rgb-gaming-accessories.html"),
        ("Gaming Setup Guide", "gaming-setup-guide.html"),
    ],
    "gaming-mice.html": [
        ("Mouse DPI Guide", "mouse-dpi-guide.html"),
        ("Best Budget Gaming Gear", "budget-gaming-gear.html"),
    ],
    "gaming-headsets.html": [
        ("RGB Gaming Accessories", "rgb-gaming-accessories.html"),
        ("Gaming Setup Guide", "gaming-setup-guide.html"),
    ],
    "gaming-monitors.html": [
        ("Gaming Setup Guide", "gaming-setup-guide.html"),
        ("Best Budget Gaming Gear", "budget-gaming-gear.html"),
    ],
    "mechanical-switches-guide.html": [
        ("Best Gaming Keyboards", "gaming-keyboards.html"),
    ],
    "mouse-dpi-guide.html": [
        ("Best Gaming Mice", "gaming-mice.html"),
    ],
    "rgb-gaming-accessories.html": [
        ("Best Gaming Keyboards", "gaming-keyboards.html"),
        ("Best Gaming Headsets", "gaming-headsets.html"),
    ],
    "gaming-setup-guide.html": [
        ("Best Gaming Keyboards", "gaming-keyboards.html"),
        ("Best Gaming Mice", "gaming-mice.html"),
        ("Best Gaming Headsets", "gaming-headsets.html"),
        ("Best Gaming Monitors", "gaming-monitors.html"),
    ],
    "budget-gaming-gear.html": [
        ("Best Gaming Keyboards", "gaming-keyboards.html"),
        ("Best Gaming Mice", "gaming-mice.html"),
        ("Best Gaming Headsets", "gaming-headsets.html"),
    ],
    "index.html": None,  # handled separately
}

HOME_CROSS_LINKS = {
    "ergonomic-chairs.html": [
        ("Ergonomics Guide", "ergonomics-guide.html"),
        ("Standing Desks", "standing-desks.html"),
        ("Home Office Setup Guide", "home-office-setup-guide.html"),
    ],
    "standing-desks.html": [
        ("Standing Desk Converters", "standing-desk-converters.html"),
        ("Ergonomics Guide", "ergonomics-guide.html"),
    ],
    "standing-desk-converters.html": [
        ("Standing Desks", "standing-desks.html"),
        ("Ergonomics Guide", "ergonomics-guide.html"),
    ],
    "monitor-arms.html": [
        ("Home Office Setup Guide", "home-office-setup-guide.html"),
        ("Webcams", "webcams.html"),
    ],
    "webcams.html": [
        ("Home Office Setup Guide", "home-office-setup-guide.html"),
        ("Monitor Arms", "monitor-arms.html"),
    ],
    "desk-accessories.html": [
        ("Standing Desks", "standing-desks.html"),
        ("Wireless Chargers", "wireless-chargers.html"),
    ],
    "wireless-chargers.html": [
        ("Desk Accessories", "desk-accessories.html"),
        ("Home Office Setup Guide", "home-office-setup-guide.html"),
    ],
    "ergonomics-guide.html": [
        ("Ergonomic Chairs", "ergonomic-chairs.html"),
        ("Standing Desks", "standing-desks.html"),
    ],
    "home-office-setup-guide.html": [
        ("Ergonomic Chairs", "ergonomic-chairs.html"),
        ("Standing Desks", "standing-desks.html"),
        ("Monitor Arms", "monitor-arms.html"),
    ],
    "index.html": None,
}

FAQ_SCHEMA_TEMPLATE = """
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{
      "@type": "Question",
      "name": "{q1}",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "{a1}"
      }}
    }},
    {{
      "@type": "Question",
      "name": "{q2}",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "{a2}"
      }}
    }}
  ]
}}
</script>"""

BREADCRUMB_SCHEMA_TEMPLATE = """
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {{
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "{hub}"
    }},
    {{
      "@type": "ListItem",
      "position": 2,
      "name": "{section}",
      "item": "{section_url}"
    }},
    {{
      "@type": "ListItem",
      "position": 3,
      "name": "{page_title}"
    }}
  ]
}}
</script>"""

INTERNAL_LINKS_HTML = """
<div class="related-section">
  <h3>Related Guides</h3>
  <div class="related-links">
{links}
  </div>
</div>"""

RELATED_LINK_TEMPLATE = '    <a href="{href}" class="related-btn">{label}</a>'


def get_breadcrumb_schema(hub, hub_url, section, section_url, page_title):
    return BREADCRUMB_SCHEMA_TEMPLATE.format(
        hub=hub, hub_url=hub_url, section=section,
        section_url=section_url, page_title=page_title
    )


def add_before_affiliate(content, insert_html):
    """Insert HTML before the affiliate disclaimer div."""
    marker = '<div class="affiliate-disclaimer">'
    if marker in content and insert_html not in content:
        content = content.replace(marker, insert_html + "\n" + marker, 1)
    return content


def inject_breadcrumbs(content, hub, hub_url, section, section_url, page_title):
    """Add breadcrumb schema + HTML after the opening container."""
    schema = get_breadcrumb_schema(hub, hub_url, section, section_url, page_title)
    breadcrumb_html = f'''
<nav class="breadcrumb" aria-label="Breadcrumb">
  <a href="{hub_url}">{hub}</a> &rsaquo; <a href="{section_url}">{section}</a> &rsaquo; <span>{page_title}</span>
</nav>
'''
    # Insert after <div class="container">
    container_match = re.search(r'(<div class="container">)', content)
    if container_match and 'class="breadcrumb"' not in content:
        pos = container_match.end()
        content = content[:pos] + breadcrumb_html + content[pos:]
    # Inject schema before </head>
    if 'BreadcrumbList' not in content:
        content = content.replace('</head>', schema + '\n</head>', 1)
    return content


def inject_internal_links(content, page_name, cross_links_map, site_path):
    """Add internal link buttons before affiliate disclaimer."""
    if page_name not in cross_links_map or cross_links_map[page_name] is None:
        return content
    links_html = ""
    for label, href in cross_links_map[page_name]:
        links_html += RELATED_LINK_TEMPLATE.format(href=href, label=label) + "\n"
    insert = INTERNAL_LINKS_HTML.format(links=links_html.rstrip())
    content = add_before_affiliate(content, insert)
    return content


def inject_faq_schema(content, q1, a1, q2, a2):
    """Inject FAQ schema before </head>."""
    schema = FAQ_SCHEMA_TEMPLATE.format(q1=q1, a1=a1, q2=q2, a2=a2)
    if 'FAQPage' not in content:
        content = content.replace('</head>', schema + '\n</head>', 1)
    return content


def add_cta_to_meta_desc(content):
    """Ensure meta description ends with a CTA."""
    pattern = r'(<meta name="description" content=")([^"]+)(")'
    def replace(m):
        desc = m.group(2)
        if not any(desc.rstrip().endswith(p) for p in ['.', '!', '?', '→']):
            desc = desc.rstrip() + '.'
        if 'Shop now' not in desc and 'Find your' not in desc:
            desc = desc.rstrip() + ' Start your search today.'
        return m.group(1) + desc + m.group(3)
    content = re.sub(pattern, replace, content)
    return content


def improve_index(site_folder, site_name, site_title, page_descriptions):
    """Improve index.html with overview content and better meta."""
    index_path = Path(site_folder) / "index.html"
    if not index_path.exists():
        return False
    content = index_path.read_text()
    
    # Update meta description if it's generic
    if "Expert reviews" in content and "Level up" in content:
        content = add_cta_to_meta_desc(content)
    
    # Add more content to hero if it's thin
    if "We review gaming equipment" in content:
        hero_section = '''
<div class="container">
<div class="hero">
<h2>Dominate with the Right Gear</h2>
<p>We review gaming equipment so you can make informed decisions and dominate your opponents. From mechanical keyboards to 360Hz monitors, we test everything to bring you honest, in-depth recommendations.</p>
</div>
</div>
'''
        if 'in-depth recommendations' not in content:
            content = re.sub(
                r'<div class="hero">.*?</div>',
                hero_section.strip(),
                content,
                flags=re.DOTALL
            )
    
    # Add Why Trust Us section before footer
    trust_section = '''
<section class="trust-section">
  <h2>Why Trust Our Reviews?</h2>
  <p>We spend hundreds of hours researching and testing gaming gear each year. Our recommendations are based on real-world performance, build quality, and value — never on affiliate commissions alone. When you buy through our links, you support the site at no extra cost to you.</p>
</section>
'''
    if 'Why Trust Our Reviews' not in content and '</footer>' in content:
        # Inject before footer
        content = content.replace('<footer>', trust_section + '\n<footer>')
        # Add styling
        if '.trust-section' not in content:
            style_addition = '''
.trust-section{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:1.5rem;margin:1.5rem 0}
.trust-section h2{color:#58a6ff;font-size:1.2rem;margin-bottom:.75rem}
.trust-section p{color:#9ca3af;font-size:.9rem;line-height:1.6}
.related-section{margin:1.5rem 0;padding:1rem 0;border-top:1px solid #1f2937}
.related-section h3{color:#fff;font-size:1rem;margin-bottom:.75rem}
.related-links{display:flex;flex-wrap:wrap;gap:.5rem}
.related-btn{background:#1f2937;color:#58a6ff;padding:.4rem .75rem;border-radius:4px;text-decoration:none;font-size:.8rem;border:1px solid #30363d}
.related-btn:hover{background:#21262d;border-color:#58a6ff}
.breadcrumb{font-size:.8rem;color:#6b7280;margin:.5rem 0 .5rem .25rem}
.breadcrumb a{color:#9ca3af;text-decoration:none}
.breadcrumb a:hover{color:#58a6ff}
'''
            content = content.replace('</style>', style_addition + '\n</style>', 1)
    
    index_path.write_text(content)
    return True


def improve_page(html_path, cross_links_map, site_path, hub, hub_url, section, section_url):
    """Apply all improvements to a single page."""
    content = html_path.read_text()
    page_name = html_path.name
    page_title_match = re.search(r'<title>([^<]+)</title>', content)
    page_title = page_title_match.group(1) if page_title_match else page_name

    # 1. Breadcrumbs + schema
    content = inject_breadcrumbs(content, hub, hub_url, section, section_url, page_title)

    # 2. Internal cross-links
    content = inject_internal_links(content, page_name, cross_links_map, site_path)

    # 3. FAQ schema for relevant pages
    faq_pages = {
        "gaming-keyboards.html": (
            "What switches are best for gaming?",
            "Cherry MX Red or similar linear switches are popular for gaming due to their smooth, quiet keystrokes. However, tactile switches like Cherry MX Brown offer a good middle ground for both gaming and typing.",
            "Are mechanical keyboards worth the extra cost?",
            "Yes. Mechanical keyboards last longer, feel better, and provide more precise inputs than membrane keyboards. For competitive gaming, the difference in actuation feel can shave milliseconds off your reaction time."
        ),
        "gaming-mice.html": (
            "What DPI do pro gamers use?",
            "Most professional gamers use between 400-1600 DPI. While higher DPI is available, lower DPI with good mousepad control often provides more precision for FPS games.",
            "Is wireless or wired better for gaming?",
            "Modern wireless gaming mice like the Logitech G Pro X Superlight 2 have near-zero latency and rival wired mice. For competitive FPS, wireless is now a legitimate choice."
        ),
        "gaming-headsets.html": (
            "Do I need a gaming headset or studio headphones?",
            "Gaming headsets include a microphone and are optimized for chat + game audio. Studio headphones offer better audio quality but require a separate mic. For multiplayer gaming, a gaming headset is more convenient.",
            "Is 7.1 surround sound worth it?",
            "Virtual 7.1 surround can help locate positional audio in games, but premium stereo headphones often sound better. Many pros prefer stereo for its more accurate soundstage."
        ),
        "gaming-monitors.html": (
            "What refresh rate do I need for gaming?",
            "For competitive gaming, 240Hz or 360Hz gives the smoothest motion. For casual gaming and single-player titles, 144Hz is excellent value. The difference between 144Hz and 240Hz is noticeable but subtle compared to 60Hz.",
            "Is IPS or VA better for gaming?",
            "IPS panels offer faster response times and better color accuracy. VA panels have higher contrast ratios. For mixed gaming and content use, IPS is generally the better choice."
        ),
        "standing-desks.html": (
            "Are standing desks worth it?",
            "Yes. Studies show that alternating between sitting and standing reduces back pain, boosts energy, and can improve focus. The ability to switch positions throughout the day is genuinely beneficial.",
            "What is the best desk height for standing?",
            "Your monitor should be at eye level and your elbows at 90 degrees. Most standing desks are adjustable from 70-120cm to accommodate different heights."
        ),
        "ergonomic-chairs.html": (
            "How much should I spend on an office chair?",
            "Aim for at least £300/$300 for a genuinely ergonomic chair. Cheaper chairs often lack proper lumbar support and adjustability. A good chair is an investment in your health and productivity.",
            "How do I set up my chair for optimal ergonomics?",
            "Feet flat on the floor, thighs parallel to the ground, arms at 90 degrees when typing. The lumbar support should push slightly into your lower back. Adjust the armrests so your shoulders stay relaxed."
        ),
        "ergonomics-guide.html": (
            "What are the most important ergonomic factors for a home office?",
            "Monitor height (top at eye level), chair lumbar support, keyboard and mouse at elbow height, and regular movement breaks are the most impactful. Lighting and noise matter too.",
            "How often should I take breaks from sitting?",
            "The 20-8-2 rule: Every 20 minutes, look at something 20 feet away for 20 seconds. Every 8 hours, move for 2+ minutes. Every 2 hours, take a proper break from your desk."
        ),
    }

    if page_name in faq_pages:
        q1, a1, q2, a2 = faq_pages[page_name]
        content = inject_faq_schema(content, q1, a1, q2, a2)

    # 4. Ensure CSS for new elements exists
    new_styles = '''
.trust-section{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:1.5rem;margin:1.5rem 0}
.trust-section h2{color:#58a6ff;font-size:1.2rem;margin-bottom:.75rem}
.trust-section p{color:#9ca3af;font-size:.9rem;line-height:1.6}
.related-section{margin:1.5rem 0;padding:1rem 0;border-top:1px solid #1f2937}
.related-section h3{color:#fff;font-size:1rem;margin-bottom:.75rem}
.related-links{display:flex;flex-wrap:wrap;gap:.5rem}
.related-btn{background:#1f2937;color:#58a6ff;padding:.4rem .75rem;border-radius:4px;text-decoration:none;font-size:.8rem;border:1px solid #30363d;transition:all .2s}
.related-btn:hover{background:#21262d;border-color:#58a6ff}
.breadcrumb{font-size:.8rem;color:#6b7280;margin:.5rem 0 .5rem .25rem}
.breadcrumb a{color:#9ca3af;text-decoration:none}
.breadcrumb a:hover{color:#58a6ff}
'''
    if 'related-btn' not in content:
        content = content.replace('</style>', new_styles + '\n</style>', 1)

    html_path.write_text(content)
    return True


def improve_pet_index(site_folder):
    index_path = Path(site_folder) / "index.html"
    if not index_path.exists():
        return
    content = index_path.read_text()
    if 'Why Trust Our Reviews' not in content and '</footer>' in content:
        trust_section = '''
<section class="trust-section">
  <h2>Why Trust Our Reviews?</h2>
  <p>We research and test pet products extensively before recommending them. Our reviews cover durability, safety, value for money, and what real pet owners think. When you buy through our links, you support the site at no extra cost to you.</p>
</section>
'''
        content = content.replace('<footer>', trust_section + '\n<footer>')
    if '.trust-section' not in content:
        style_add = '''
.trust-section{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:1.5rem;margin:1.5rem 0}
.trust-section h2{color:#58a6ff;font-size:1.2rem;margin-bottom:.75rem}
.trust-section p{color:#9ca3af;font-size:.9rem;line-height:1.6}
.related-section{margin:1.5rem 0;padding:1rem 0;border-top:1px solid #1f2937}
.related-section h3{color:#fff;font-size:1rem;margin-bottom:.75rem}
.related-links{display:flex;flex-wrap:wrap;gap:.5rem}
.related-btn{background:#1f2937;color:#58a6ff;padding:.4rem .75rem;border-radius:4px;text-decoration:none;font-size:.8rem;border:1px solid #30363d;transition:all .2s}
.related-btn:hover{background:#21262d;border-color:#58a6ff}
.breadcrumb{font-size:.8rem;color:#6b7280;margin:.5rem 0 .5rem .25rem}
.breadcrumb a{color:#9ca3af;text-decoration:none}
.breadcrumb a:hover{color:#58a6ff}
'''
        content = content.replace('</style>', style_add + '\n</style>', 1)
    index_path.write_text(content)


PET_CROSS_LINKS = {
    "dog-toys.html": [("Best Dog Beds", "best-dog-beds.html"), ("Dog Collars & Leashes", "dog-collars-leashes.html")],
    "cat-toys.html": [("Cat Trees", "cat-trees.html"), ("Cat Litter Boxes", "cat-litter-boxes.html")],
    "best-dog-beds.html": [("Dog Toys", "dog-toys.html"), ("Pet Food", "pet-food.html")],
    "pet-food.html": [("Pet Feeders & Waterers", "pet-feeders-waterers.html"), ("Best Dog Beds", "best-dog-beds.html")],
    "pet-tech.html": [("Pet Safety Products", "pet-safety-products.html"), ("Premium Pet Products", "premium-pet-products.html")],
    "new-pet-owner-guide.html": [("Pet Food", "pet-food.html"), ("Best Dog Beds", "best-dog-beds.html")],
}

COURSE_CROSS_LINKS = {
    "coding-courses.html": [("Coding Bootcamps", "coding-bootcamps.html"), ("Free Online Courses", "free-online-courses.html")],
    "free-online-courses.html": [("Language Learning", "language-learning.html"), ("Personal Development", "personal-development.html")],
    "platform-comparison.html": [("How to Choose Courses", "how-to-choose-courses.html"), ("Business Courses", "business-courses.html")],
    "business-courses.html": [("Personal Development", "personal-development.html"), ("Coding Courses", "coding-courses.html")],
    "design-courses.html": [("Coding Courses", "coding-courses.html"), ("Language Learning", "language-learning.html")],
    "how-to-choose-courses.html": [("Free Online Courses", "free-online-courses.html"), ("Platform Comparison", "platform-comparison.html")],
}

AI_CROSS_LINKS = {
    "ai-writing-tools.html": [("AI Image Tools", "ai-image-tools.html"), ("AI Note Taking", "ai-note-taking.html")],
    "ai-image-tools.html": [("AI Writing Tools", "ai-writing-tools.html"), ("ChatGPT Alternatives", "chatgpt-alternatives.html")],
    "ai-coding-tools.html": [("AI for Business", "ai-for-business.html"), ("ChatGPT Alternatives", "chatgpt-alternatives.html")],
    "ai-note-taking.html": [("AI Writing Tools", "ai-writing-tools.html"), ("AI for Students", "ai-for-students.html")],
    "chatgpt-alternatives.html": [("AI Writing Tools", "ai-writing-tools.html"), ("AI Image Tools", "ai-image-tools.html")],
}


def main():
    sites = [
        {
            "folder": "/workspace/affiliate-sites/gaming-gear-pro",
            "name": "Gaming Gear Pro",
            "section": "Gaming Gear",
            "hub": "GenesisClaw Hub",
            "hub_url": "https://genesisclawbot.github.io/",
            "section_url": "https://genesisclawbot.github.io/gaming-gear-pro/",
            "cross_links": GAMING_CROSS_LINKS,
            "page_descriptions": {}
        },
        {
            "folder": "/workspace/affiliate-sites/home-office-gear",
            "name": "Home Office Gear",
            "section": "Home Office",
            "hub": "GenesisClaw Hub",
            "hub_url": "https://genesisclawbot.github.io/",
            "section_url": "https://genesisclawbot.github.io/home-office-gear/",
            "cross_links": HOME_CROSS_LINKS,
            "page_descriptions": {}
        },
        {
            "folder": "/workspace/affiliate-sites/pet-products-hub",
            "name": "Pet Products Hub",
            "section": "Pet Products",
            "hub": "GenesisClaw Hub",
            "hub_url": "https://genesisclawbot.github.io/",
            "section_url": "https://genesisclawbot.github.io/pet-products-hub/",
            "cross_links": PET_CROSS_LINKS,
            "page_descriptions": {},
            "custom_index": improve_pet_index
        },
        {
            "folder": "/workspace/affiliate-sites/online-courses-guide",
            "name": "Online Courses Guide",
            "section": "Online Courses",
            "hub": "GenesisClaw Hub",
            "hub_url": "https://genesisclawbot.github.io/",
            "section_url": "https://genesisclawbot.github.io/online-courses-guide/",
            "cross_links": COURSE_CROSS_LINKS,
            "page_descriptions": {}
        },
        {
            "folder": "/workspace/affiliate-sites/ai-saas-tools",
            "name": "AI SaaS Tools",
            "section": "AI Tools",
            "hub": "GenesisClaw Hub",
            "hub_url": "https://genesisclawbot.github.io/",
            "section_url": "https://genesisclawbot.github.io/ai-saas-tools/",
            "cross_links": AI_CROSS_LINKS,
            "page_descriptions": {}
        },
    ]

    total = 0
    for site in sites:
        folder = Path(site["folder"])
        html_files = list(folder.glob("*.html"))
        print(f"\n{'='*50}")
        print(f"Processing: {site['name']} ({len(html_files)} pages)")

        # Improve index first
        if "custom_index" in site:
            site["custom_index"](folder)
        else:
            improve_index(folder, site["name"], site["name"], site["page_descriptions"])

        for html_file in html_files:
            try:
                improve_page(
                    html_file,
                    site["cross_links"],
                    folder,
                    site["hub"],
                    site["hub_url"],
                    site["section"],
                    site["section_url"]
                )
                print(f"  ✓ {html_file.name}")
                total += 1
            except Exception as e:
                print(f"  ✗ {html_file.name}: {e}")

    print(f"\nTotal pages improved: {total}")


if __name__ == "__main__":
    main()
