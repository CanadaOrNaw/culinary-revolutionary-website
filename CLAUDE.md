# culinary-revolutionary

Static website source for Culinary Revolutionary. Existing Python generators produce menus and articles; no frontend framework.

## Where things live

| Path | Holds |
|---|---|
| `index.html / menus.html` | the site; menus are generated, never hand-edited |
| `menus.json` | menu data read by `build-menus.py` |
| `content/blog/` | article metadata/body sources read by `build-blog.py` |
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
- `~/Projects/fleet-index/08_retirement/target-architecture.md` - Agrippa history, not a live dependency

Read [handbook](docs/handbook/index.md) and its status before work. Before handoff, follow the [living-docs contract](file:///home/zack/Projects/fleet-index/_system/documentation/POLICY.md): review evidence, refresh canonical pages/status, rebuild views and pass working/staged checks.
