# culinary-revolutionary

Dependency-free static website for Culinary Revolutionary. No build step, no framework.

## Where things live

| Path | Holds |
|---|---|
| `index.html / menus.html` | the site; menus are generated, never hand-edited |
| `content/` | source content the generators read |
| `build-menus.py / build-blog.py` | generators — run these, don't edit output |
| `blog/` | generated weekly posts |
| `DESIGN.md` | design decisions |

## Note

Publishing is an outward-facing action: drafted and approved, never posted autonomously.

## Rules

- One home per fact: link to the file that owns a fact instead of copying it.
- Never commit secret values. Record where they live.
- `_generated/` and build output are script-owned: change the script, not the file.
- Mirrored to Gitea by `~/.local/bin/gitstack_sync.sh`.

## Related

- `~/Projects/fleet-index` — every device, path and git history, and what happens to each
- `~/Projects/agrippa` — the AI system being built on top
