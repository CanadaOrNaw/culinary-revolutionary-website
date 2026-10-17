# Culinary Revolutionary - source and generated site views

## Inputs

| Source | File / location | Section / scope | Why |
|---|---|---|---|
| Entry/design | `CLAUDE.md`, `DESIGN.md` | Task route; applicable design decision | Canonical owner and design reference |
| Menu source | `menus.json` | Selected menu/course/item | `build-menus.py` reads this data |
| Article source | `content/blog/SLUG.json`, `content/blog/SLUG.html` | Requested article only | Metadata/body before generation |
| Generators | `build-menus.py`, `build-blog.py` | Selected input/output path | Derived page behavior |
| Site components | `index.html`, `script.js` and task-named assets/styles | Changed component only | Rendering, form and common page fragments |
| Native task guide | `docs/handbook/index.md` | Selected menu/article/preview/test route | Existing safe checks and dependency instructions |

## Process

1. Identify the task's canonical menu/article/component and the requested reader outcome before editing.
2. Draft against current client-approved facts/design. Old generated output is an artifact, not the authority for future content.
3. Run the applicable generator/check in the documented authorized scope; inspect derived pages and actual failures.
4. Independently review source/docs and intended submitted bytes. Public push/deploy remains an outward-facing approval gate.

## Outputs

| Artifact | Location | Format |
|---|---|---|
| Authored data/content | `menus.json`, selected `content/blog/` source, existing component files | JSON, HTML, CSS, JS |
| Derived views | `menus.html`, homepage teaser, `blog/`, sitemap | Existing generator-owned files |
| Explanation/review | `docs/handbook/`, `docs/verification/` | Markdown and private exact review JSON |

## Checkpoints

| After step | Agent presents | Human decides |
|---|---|---|
| Menu/article/public UI draft | Intended customer use, source claims and preview | Client/Zack approval or correction before publication |

## Audit

| Check | Pass condition |
|---|---|
| Value | Preview answers the task's agreed customer question/action, not an invented marketing goal |
| Source | Generator reads actual menu/article authority; shared fragments/design remain canonical |
| Quality/privacy | Applicable native checks pass, rights/claims are reviewed, no private data exposed |
