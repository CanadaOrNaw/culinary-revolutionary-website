---
title: Update approved menus
description: Change menu source and review both generated pages plus manually wired
  inquiry choices.
kind: how-to
source_ref:
- README.md#L67-L78
- menus.json#L1-L15
- menus.json#L1194-L1234
- build-menus.py#L25-L64
- build-menus.py#L158-L187
- index.html#L546-L557
- CLIENT-QUESTIONS.md#L49-L91
---

# Update approved menus

Use this workflow only for an authorized content change. The commands below rewrite public products; they were not run as part of documentation authoring.

## Before editing

Read the relevant item in the repository's `CLIENT-QUESTIONS.md` and `menus.json` editorial `ambiguities`. Confirm ambiguous selection rules, dish wording or constraints with the chef rather than choosing an answer. Keep existing unrelated work intact.

Use [menu reference](../reference/menu-source.md) for fields and [source-to-artifact flow](../architecture/source-to-public-artifact.md) for write order.

## Change the source

1. Edit approved data in `menus.json`. Preserve intended course/item order. Do not hand-edit `menus.html` or homepage teaser cards.
2. If an id/menu is added or renamed, review `index.html` inquiry options, menu request preselection, article anchor links and hardcoded seven-menu wording in home/full-page templates. Array extensibility does not update those interfaces automatically.
3. Keep editorial typo/ambiguity notes consistent with actual approval. The renderer does not publish those arrays.

## Regenerate under the approved scope

From the repository root:

```bash
python3 build-menus.py menus.json
python3 tests/check-site.py
```

The first command uses the supplied JSON path, writes `menus.html`, then replaces the homepage teaser grid. It prints the page length/menu/dish counts and a teaser replacement line. No output-directory or dry-run flag exists.

The documented full content sequence also runs `python3 build-blog.py` before the menu builder. Use it when the approved change affects shared home chrome or article products; it writes more files and is not required merely to inspect menu data. See [CLI reference](../reference/generator-and-checker-cli.md).

## Review the complete impact

- Compare both full menu output and home cards against the approved JSON.
- Check course selection notes and dish restrictions, including any guest limits embedded in descriptions.
- Check every Request this menu route against the static form options without submitting.
- Review link/metadata checker output. The checker does not validate that every source dish rendered correctly or that generated files are fresh.
- Review sitemap menu modification date deliberately: the blog builder currently uses a fixed menu date, not the JSON file timestamp.

A build failure may leave `menus.html` changed before homepage replacement. Inspect both products; correct the source in scope and rerun rather than patching output.

## Finish safely

Record changed source and products together for review. Follow [maintenance](../maintenance/change-impact-and-docs-ownership.md). Do not push main or run a live inquiry test without publication/business approval. No cleanup/removal or Git staging is implied by this guide.
