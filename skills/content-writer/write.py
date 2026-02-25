#!/usr/bin/env python3
"""Generate SEO-optimised content: blog posts, landing pages, product copy"""
import re, sys
from pathlib import Path

def slugify(t): return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')

def blog_post(topic):
    return f"""---
title: {topic}
description: A comprehensive guide to {topic}.
---

# {topic}

Understanding {topic} is essential in today's fast-moving world. This guide covers what you need to know.

## Why {topic} Matters

Many people overlook {topic}, but it's one of the highest-leverage things you can focus on. Here's why.

## Key Benefits

- Save time and reduce effort
- Achieve better results consistently
- Stay ahead of the competition
- Build skills that compound over time

## Getting Started

Start with the basics. Pick one aspect of {topic} and master it before expanding. Consistency beats intensity.

## Conclusion

{topic} doesn't have to be complicated. Start small, stay consistent, and the results will follow.
"""

def landing_page(topic):
    return f"""# {topic}

**Transform how you work with {topic}.**

## The Problem

Struggling with {topic}? You're not alone.

## Our Solution

We make {topic} simple, fast, and reliable.

## Key Features

- **Easy setup** — Get started in minutes
- **Powerful** — Handles everything you need
- **Affordable** — Plans from £9/month

## Get Started

Sign up free. No credit card required.
"""

GENERATORS = {"blog-post": blog_post, "landing-page": landing_page}

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 write.py <type> <topic>"); sys.exit(1)
    ctype, topic = sys.argv[1], sys.argv[2]
    if ctype not in GENERATORS:
        print(f"Unknown type. Available: {', '.join(GENERATORS)}"); sys.exit(1)
    slug = slugify(topic)
    out = Path(f"./projects/content/{slug}")
    out.mkdir(parents=True, exist_ok=True)
    content = GENERATORS[ctype](topic)
    (out / f"{ctype}.md").write_text(content)
    print(f"Created: {out}/{ctype}.md ({len(content.split())} words)")

if __name__ == '__main__': main()
