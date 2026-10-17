---
title: Design, assets and crawl metadata
description: Find actual tokens, responsive behavior, asset provenance and indexing
  limits.
kind: reference
source_ref:
- styles.css#L1-L13
- styles.css#L398-L506
- styles.css#L555-L575
- styles.css#L728-L783
- styles.css#L1131-L1175
- index.html#L6-L120
- ASSET-SOURCES.json#L1-L57
- DESIGN.md#L16-L49
- robots.txt#L1-L15
- thank-you.html#L7-L8
- build-blog.py#L48-L73
---

# Design, assets and crawl metadata

## Actual CSS tokens

| Variable | Value | Intended role |
|---|---|---|
| `--navy` | `#0a1f44` | Dark brand/background |
| `--slate` | `#4a5b78` | Muted text |
| `--white`, `--surface` | `#ffffff` | Light content |
| `--cream` | `#f6f1e8` | Page background |
| `--gold` | `#c7a35a` | Accent, suitable on dark backgrounds |
| `--gold-ink` | `#866620` | Darker gold text on light backgrounds |
| `--text` | `#15233b` | Main text |
| `--shadow` | `0 16px 40px rgba(10, 31, 68, 0.16)` | Shared shadow |

The stylesheet comments distinguish gold contrast on light backgrounds. Focus-visible rings, skip links and hidden-nav visibility support access, but source review is not a full WCAG/browser audit.

Display typography uses Cormorant Garamond with Georgia fallback; body uses Inter with system fallbacks. Pages request Google Fonts. Local imagery avoids a runtime remote image dependency, but fonts and the inquiry relay can still contact external services.

## Responsive contracts

| Rule | Source behavior |
|---|---|
| Navigation max-width 1200px | Toggle shown; nav hidden/nonfocusable until `.open` |
| Main content max-width 900px | Services/menus/about/inquiry become one column; header digits visually hidden |
| Max-width 600px | Brand text hidden, narrower section/gallery/form/menu layout |
| Journal max-width 750px | Cards/article layout become one column; contents moves ahead; aside CTA hidden |
| Max-width 390px | Hero actions/footer narrow layout |

CSS uses modern features including `color-mix`, `svh`, `clamp`, grid and `text-wrap`. There is no compatibility/polyfill matrix. The JavaScript resize threshold matches the navigation breakpoint; no-JavaScript narrow navigation remains a limitation.

## Asset provenance and rights

`ASSET-SOURCES.json` records original Wix/source URLs and byte counts. It is a provenance note, **not license evidence**. The old signed capture URL is not repeated here. Some derived icons/logo variants are shipping files but not separate provenance entries; do not invent their derivation history.

Current workflow excludes original `logo.png` and the source-home capture from shipping. Pages reference the smaller logo variant. Historical preview binaries and screenshots are neither current acceptance nor documentation assets in this handbook.

`DESIGN.md` is historical prototype guidance. CSS and current markup determine behavior; its non-submitting concept-form statement is no longer current.

## Canonical, structured and crawl data

Home markup supplies LocalBusiness, Person and WebSite JSON-LD linked by ids, broad service region and selected service offers. It intentionally omits unconfirmed ratings/reviews/awards and a specific street address. Authored biography statements remain client-source claims, not independent credential checks.

Article templates supply canonical/social metadata, BlogPosting/BreadcrumbList and organization publisher. Index/feed/sitemap are generated; [article reference](article-source-and-metadata.md) explains exact dates and fields.

`robots.txt` allows crawling and disallows selected internal build-note paths. It is not security. `thank-you.html` carries `noindex` and is deliberately not blocked so a crawler can see that directive. It has no canonical requirement in the local checker.

No source or local parser result guarantees indexing, ranking, rich results, current provider terms or editorial truth. Use [publication boundaries](../how-to/review-publication-and-domain-evidence.md) and [verification limits](../status.md).
