#!/usr/bin/env python3
"""Package projects for deployment to Vercel, Netlify, Railway"""
import json, sys
from pathlib import Path

def detect_type(path):
    p = Path(path)
    if (p / "package.json").exists():
        pkg = json.loads((p / "package.json").read_text())
        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        if "next" in deps: return "nextjs"
        if "express" in deps or "fastify" in deps: return "node-api"
        return "static"
    if (p / "requirements.txt").exists(): return "python"
    if (p / "index.html").exists(): return "static"
    return "unknown"

def package(project_path, platform):
    path = Path(project_path)
    if not path.exists(): print(f"Not found: {project_path}"); sys.exit(1)
    ptype = detect_type(project_path)
    print(f"Project type: {ptype}")
    cmds = {"vercel": f"vercel --prod", "netlify": f"netlify deploy --prod", "railway": "railway up"}
    cmd = cmds.get(platform, "vercel --prod")
    (path / "HUMAN_REQUEST.md").write_text(
        f"# Deploy Request: {path.name}\n\nPlatform: {platform}\nType: {ptype}\n\n```bash\ncd projects/{path.name}\n{cmd}\n```\n\nPlease run and share the deployed URL.\n"
    )
    print(f"✓ Packaged for {platform}. See HUMAN_REQUEST.md")

def main():
    if len(sys.argv) < 3: print("Usage: python3 package.py <path> <platform>"); sys.exit(1)
    package(sys.argv[1], sys.argv[2])

if __name__ == '__main__': main()
