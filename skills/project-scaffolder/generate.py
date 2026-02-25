#!/usr/bin/env python3
"""Generate complete project directories with config + deploy instructions"""
import json, sys
from pathlib import Path

TEMPLATES = {
    "static": {"index.html": "<!DOCTYPE html>\n<html lang='en'>\n<head><meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1.0'><title>PROJECT_NAME</title></head>\n<body><h1>PROJECT_NAME</h1></body>\n</html>\n", "README.md": "# PROJECT_NAME\n"},
    "node-api": {"package.json": '{\n  "name": "PROJECT_NAME",\n  "version": "1.0.0",\n  "type": "module",\n  "scripts": {"start": "node server.js"},\n  "dependencies": {"express": "^4.18.2"}\n}', "server.js": "import express from 'express';\nconst app = express();\napp.get('/', (req, res) => res.json({message: 'Hello from PROJECT_NAME'}));\napp.listen(process.env.PORT || 3000);\n", "vercel.json": '{"builds":[{"src":"server.js","use":"@vercel/node"}],"routes":[{"src":"/(.*)","dest":"server.js"}]}', "README.md": "# PROJECT_NAME\n"},
    "python-api": {"requirements.txt": "flask>=2.3.0\n", "app.py": "from flask import Flask, jsonify\napp = Flask(__name__)\n@app.route('/')\ndef index(): return jsonify({'message': 'Hello from PROJECT_NAME'})\nif __name__ == '__main__': app.run(host='0.0.0.0', port=5000)\n", "vercel.json": '{"builds":[{"src":"app.py","use":"@vercel/python"}],"routes":[{"src":"/.*(","dest":"app.py"}]}', "README.md": "# PROJECT_NAME\n"},
}

def generate(name, ptype):
    if ptype not in TEMPLATES:
        print(f"Unknown type '{ptype}'. Available: {', '.join(TEMPLATES)}"); sys.exit(1)
    path = Path(f"./projects/{name}")
    path.mkdir(parents=True, exist_ok=True)
    created = []
    for fn, content in TEMPLATES[ptype].items():
        fp = path / fn
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(content.replace("PROJECT_NAME", name))
        created.append(str(fp))
    (path / "DEPLOY.md").write_text(f"# Deploy {name}\n\n```bash\nnpm i -g vercel && cd {name} && vercel\n```\n")
    (path / "HUMAN_REQUEST.md").write_text(f"# Deploy Request: {name}\n\nType: {ptype}\nLocation: ./projects/{name}/\n\nPlease deploy to Vercel and share the URL.\n")
    return path, created

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 generate.py <name> <type>"); sys.exit(1)
    path, files = generate(sys.argv[1], sys.argv[2])
    print(f"Created: {path}"); [print(f"  {f}") for f in files]

if __name__ == '__main__': main()
