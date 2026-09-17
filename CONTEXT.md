# culinary-revolutionary: what this workspace is

Dependency-free static website for Culinary Revolutionary. No build step, no framework.

## Inputs

- **Reference (stable):** the files listed in `CLAUDE.md`
- **Working:** whatever the current task touches

## Process

Read `CLAUDE.md` first: it routes and holds no content. Change the source, not generated output.

## Outputs

| What | Where |
|---|---|
| the site; menus are generated, never hand-edited | `index.html / menus.html` |
| source content the generators read | `content/` |
| generators — run these, don't edit output | `build-menus.py / build-blog.py` |

## Human check

Publishing is an outward-facing action: drafted and approved, never posted autonomously.
