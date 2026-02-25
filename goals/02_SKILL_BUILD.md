# Phase 2: Skill Acquisition

## Read First: ./SCHEMAS.md, ./identity.json

## Objective
Build capabilities that directly enable revenue generation.
You build inside the sandbox. Human deploys on host.

## Workflow For All Projects
1. Create project directory: ./projects/{name}/
2. Build code, content, config inside it
3. Create ./projects/{name}/DEPLOY.md with step-by-step host instructions
4. Create ./projects/{name}/HUMAN_REQUEST.md with what you need
5. Message human, set task to blocked, work on something else

## Priority Skills (build in this order)
1. **Project Scaffolder** — Generate complete project directories with config + deploy instructions
2. **Content Writer** — SEO-optimised blog posts, landing pages, marketing copy
3. **Deploy Packager** — Create deploy-ready bundles for Vercel/Netlify/Railway
4. **Code Quality Checker** — Review generated code, run linting, validate JSON/HTML
5. **Task Decomposer** — Break goals into task objects per SCHEMAS.md format

## Claude Code Integration
For complex programming (50+ lines), request human to run on host:
[Request to human]
Please run: cd ~/Genesis/projects/{name} && claude -p "{spec}"
Results appear in workspace. Expect 10-60 min delay. Work on other tasks while waiting.

## Success Criteria
- [ ] 5+ skills created, tested, registered
- [ ] 1+ complete project built and ready for deployment
- [ ] Reliable build → test → deploy-request workflow proven

When complete: update phase to "03_monetise". Message human.
