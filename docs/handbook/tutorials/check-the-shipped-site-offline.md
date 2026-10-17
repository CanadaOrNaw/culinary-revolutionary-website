---
title: Check the shipped site offline
description: Get a first useful result with the existing no-write, no-network site
  checker.
kind: tutorial
source_ref:
- tests/check-site.py#L1-L80
- README.md#L3-L17
- AGENTS.md#L21-L23
---

# Check the shipped site offline

**Outcome:** check the current local HTML/XML without installing dependencies, starting a server, rebuilding pages, sending an inquiry or publishing.

## Prerequisites

- A local checkout of this project and an existing `python3` command.
- A shell in the repository root, the directory containing `tests/` and `index.html`.
- The shipped root pages, blog tree, assets, sitemap and RSS already present.

This exercise reads current products. It does not prove the generators were just run. Do not use Python's `-O` option: the checker uses `assert` statements.

## Run the native checker

```bash
python3 tests/check-site.py
```

The author run on 2026-10-17 returned exit 0 and:

```text
PASS: 9 pages, 308 internal links, article metadata, 8 sitemap URLs and RSS.
```

Counts change when the site's pages/links change. The observable success condition is an exit-0 PASS summary for the current checkout, not a hardcoded count in a test or a claim that production works.

## Understand the result

The checker parses three root pages plus every blog HTML file. It checks local href/src destinations, duplicate ids and known HTML fragments; one H1 and a description per page; canonical metadata except thank-you; selected article/home structured-data assertions; sitemap uniqueness/destinations; article sitemap membership; and RSS item count.

It skips external links and does not execute JavaScript, submit forms, inspect inboxes, validate CSS/browser rendering, verify image rights, query CI, or check search indexing. A PASS cannot establish these outcomes.

## If it fails

| First error | What to inspect |
|---|---|
| File missing or parse/JSON/XML error | Current checkout products and the named source/output; do not install packages to repair a stdlib check |
| Broken link or anchor | The named HTML link and target id; generated pages must be corrected at their owning source |
| Missing canonical/description/schema or date mismatch | Template and article metadata, not a one-off edit to generated HTML |
| RSS count or sitemap mismatch | Current article outputs versus index/feed/source; investigate stale products before any removal |

Keep the failure output. Consult [troubleshooting](../operations/verification-and-troubleshooting.md) and review any existing uncommitted work before attempting an authorized fix.

## Cleanup and next step

No cleanup is needed: this command writes nothing. Do not follow a passing check with a form submission or main push as part of this exercise.

Next, [trace one menu inquiry without submitting](trace-a-menu-inquiry.md), or read [the generator lifecycle](../architecture/source-to-public-artifact.md).
