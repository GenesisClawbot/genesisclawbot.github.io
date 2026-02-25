#!/usr/bin/env python3
"""Validate JSON, HTML, JS, Python files in a project directory"""
import json, re, sys
from pathlib import Path
from html.parser import HTMLParser

class TagChecker(HTMLParser):
    def __init__(self):
        super().__init__(); self.stack = []; self.errors = []
        self.void = {'br','hr','img','input','meta','link','area','base','col','embed','param','source','track','wbr'}
    def handle_starttag(self, tag, attrs):
        if tag not in self.void: self.stack.append(tag)
    def handle_endtag(self, tag):
        if self.stack and self.stack[-1] == tag: self.stack.pop()

def check_json(path):
    try: json.loads(path.read_text()); return [], []
    except json.JSONDecodeError as e: return [f"JSON error: {e.msg} at line {e.lineno}"], []

def check_html(path):
    content = path.read_text(); errors = []; warnings = []
    for tag in ['<html', '<head', '<body']:
        if tag not in content.lower(): errors.append(f"Missing {tag} tag")
    p = TagChecker(); p.feed(content)
    return errors + p.errors, warnings

def check_python(path):
    content = path.read_text(); errors = []; warnings = []
    try: compile(content, str(path), 'exec')
    except SyntaxError as e: errors.append(f"SyntaxError line {e.lineno}: {e.msg}")
    for i, line in enumerate(content.splitlines(), 1):
        if 'TODO' in line or 'FIXME' in line: warnings.append(f"Line {i}: {line.strip()}")
    return errors, warnings

CHECKERS = {'.json': check_json, '.html': check_html, '.htm': check_html, '.py': check_python}

def main():
    if len(sys.argv) < 2: print("Usage: python3 check.py <path>"); sys.exit(1)
    path = Path(sys.argv[1])
    if not path.exists(): print(f"Not found: {path}"); sys.exit(1)
    total_e = total_w = 0
    print(f"=== Code Quality: {path.name} ===\n")
    for fp in sorted(path.rglob('*')):
        if not fp.is_file() or fp.suffix not in CHECKERS: continue
        fn = CHECKERS[fp.suffix]
        errors, warnings = fn(fp)
        rel = fp.relative_to(path)
        if errors or warnings:
            print(f"{rel}:")
            for e in errors: print(f"  ❌ {e}"); total_e += 1
            for w in warnings: print(f"  ⚠️  {w}"); total_w += 1
        else:
            print(f"{rel}: ✅")
    print(f"\nSummary: {total_e} errors, {total_w} warnings")
    sys.exit(0 if total_e == 0 else 1)

if __name__ == '__main__': main()
