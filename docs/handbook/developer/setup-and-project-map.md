---
title: Setup and repository map
description: Find actual maintenance requirements, authored inputs, generated products
  and private boundaries.
kind: developer
source_ref:
- README.md#L3-L23
- build-blog.py#L3-L25
- build-menus.py#L3-L14
- .github/workflows/deploy-pages.yml#L27-L59
- script.js#L99-L109
- styles.css#L419-L575
- docs/CONTEXT.md#L1-L5
---

# Setup and repository map

## Requirements by task

| Task | What the files actually require |
|---|---|
| Read source or static copy | A local checkout and text/browser tools; no install step |
| Run the safe site checker | Existing `python3`; standard library only |
| Regenerate approved menus/articles | Existing `python3`; standard library only; writes repository products |
| Browser preview | A local HTTP origin for root-relative article/feed/asset paths; optional documented Python loopback preview |
| Domain diagnostic | Bash supporting uppercase expansion, `curl`, `jq`, `dig`, `tr`, and network authorization |
| Submitted-index documentation check | CI Python 3.12 plus pinned documentation parsers; generated shared policy bundle, not business-site dependencies |

There is no `package.json`, `pyproject.toml`, requirements file, virtual environment or application installer in the inspected project. CI selects Python 3.12, but the generators do not declare a minimum local Python version. Do not install packages to make a source audit pass.

The public site requests Google Fonts with local font fallbacks and uses Web3Forms for submissions. Static does **not** mean fully offline. Modern browser features include `fetch`, `FormData`, `URLSearchParams`, optional chaining, grid, `clamp`, `svh` and `color-mix`. No tested browser-version support matrix is declared.

## File ownership

| Source/path | Owns | Result or constraint |
|---|---|---|
| `index.html` | Home copy, form markup/options, shared sprite/header/footer | Authored shell plus two generator-owned regions |
| `styles.css`, `script.js` | Layout and browser interactions | Shared by root and generated pages |
| `thank-you.html` | Confirmation copy/layout | Authored separately; not proof of delivery |
| `menus.json`, `build-menus.py` | Menu data and rendering | `menus.html` plus homepage teaser grid |
| `content/blog/`, `build-blog.py` | Article metadata/body and rendering | Article pages, index, homepage latest card, RSS, sitemap |
| `tests/check-site.py` | Offline markup/link/metadata assertions | Reads current public products; writes nothing |
| `.github/workflows/deploy-pages.yml` | Release trigger and public staging | `_site` is created on the CI runner |
| `ops/verify-domain.sh` | Optional RDAP/DNS/HTTP observations | Network diagnostic, not local health assertion |
| `ASSET-SOURCES.json`, `DESIGN.md` | Asset provenance and historical design notes | Not public site content; rights still need approval |
| `LAUNCH.md`, `CLIENT-QUESTIONS.md` | Dated launch authority and unresolved copy questions | Do not turn historical records into current live claims |
| `docs/handbook/` | This private reader documentation | Never copied into the public business artifact |
| `docs/verification/` | Source/page/interface map and review evidence | Not reader-site input or business-site content |
| `.docs-check/`, `.githooks/docs-pre-commit` | Derived portable CI policy and shared local enforcement call | Shared owner regenerates policy; copied executors are not hand-authored culinary source |

The audit also classified binary public assets, ignored historical previews, ignored scrape responses, opaque domain-verification materials and old generated private handbook views. They are not hidden app modules. Do not mistake a screenshot, cache response or generated receipt for current behavior proof.

## First useful result

From the repository root, follow [the offline-check tutorial](../tutorials/check-the-shipped-site-offline.md). It needs no install, server, generator or submission.

For visual work, [preview deliberately](../how-to/preview-and-review-interactions.md). Opening the home file alone does not reproduce all root-relative blog routes. A preview serves the repository directory, not the release allowlist; keep it loopback-only and stop it afterwards.

## Next

Read [architecture](../architecture.md) before changing shared chrome. Use [testing and extension points](testing-and-extension-points.md) before assuming a new menu or article is fully wired.
