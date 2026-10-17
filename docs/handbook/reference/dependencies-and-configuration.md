---
title: Dependencies and configuration
description: Separate static-site dependencies, maintenance tools, source constants
  and submitted-index documentation checks.
kind: reference
source_ref:
- build-blog.py#L3-L16
- build-blog.py#L100-L110
- build-menus.py#L3-L14
- tests/check-site.py#L3-L9
- script.js#L12-L14
- script.js#L65-L80
- .github/workflows/deploy-pages.yml#L1-L71
- ops/verify-domain.sh#L5-L28
- .gitignore#L1-L21
- .nojekyll
- CNAME#L1
- robots.txt#L1-L15
---


# Dependencies and configuration

## No application environment interface

The generators, checker and browser script do not read application environment variables. There is no `.env` setup, package install or configuration precedence stack. Do not invent API-key environment variables, an app port, a database URL or framework flags.

The diagnostic's `DOMAIN` is a hardcoded shell variable, not an inherited app setting. The workflow's shell working directory is CI context, not culinary configuration.

## Configuration owners

| Setting | Actual owner/default | Effect |
|---|---|---|
| Menu input | Optional first menu-builder argument; else script-adjacent `menus.json` | Only input location changes; output root does not |
| Blog root/origin | Script directory; canonical business origin in `BASE` | Output/canonical/social/schema/feed/sitemap URLs |
| Article eligibility | Current UTC date | Skip future publications; no scheduler/date override |
| Reading speed | 200 words/minute, rounded, minimum 1 | Display estimate only |
| Home/menu sitemap floors | `2026-09-22` home minimum, `2026-09-10` menu constant | Deliberate source maintenance, not automatic file timestamps |
| Enhanced form endpoint/routing | HTML action and trimmed hidden value | Missing/blank/exact placeholder selects draft mode |
| Fallback recipient/JS target | `script.js` constants | Public contact fallback and relative thank-you route |
| Native redirect | Hidden HTML absolute canonical thank-you URL | Provider/native path, independent of JS redirect |
| Domain file | `CNAME` | Workflow copies conditionally; README says Pages settings own Actions custom domain |
| Crawl | `robots.txt`; thank-you noindex | Crawler guidance, never confidentiality |

There is no universal “one value changes everything” contract. Mailbox/domain changes require consistency review of contact copy, fallback constant, native redirect, canonical/origin/schema/feed/sitemap and remote settings under owner approval. Do not reproduce routing values.

## Native and browser dependencies

| Area | Dependencies |
|---|---|
| Menu generator | Python `json`, `html`, `sys`, `re`, `pathlib` |
| Blog generator | Python `datetime`, `email.utils`, `html`, `json`, `pathlib`, `re` |
| Offline checker | Python `html.parser`, `pathlib`, `urllib.parse`, `json`, `xml.etree.ElementTree` |
| Browser | HTML/CSS plus modern DOM, FormData, URLSearchParams, fetch/async/optional chaining |
| Network presentation | Google Fonts with declared serif/system fallbacks |
| Inquiry delivery | Web3Forms plus separately managed mailbox/DNS; no local store |
| Domain diagnostic | Bash, curl, jq, dig, tr and authorized network |

No local minimum Python/browser matrix is declared. CI selects Python 3.12. “Standard library only” applies to content builders/checker, not every documentation tool in the checkout.

## Workflow and copied documentation dependencies

The inspected Actions file uses checkout v7, setup-python v5, configure-pages v6, upload-pages-artifact v5 and deploy-pages v5. It selects Ubuntu latest, grants contents read/pages write/id-token write, and uses concurrency group pages without cancellation-in-progress. These source declarations are not evidence of a successful remote run.

CI still installs `markdown-it-py==4.2.0` and `PyYAML==6.0.3` under setup-python 3.12. The migrated submitted-index checker uses these documentation parsers through its shared validator. The portable validation bundle contains no ReportLab renderer or DejaVu font requirement. These are CI documentation dependencies, not the static business site or its standard-library content builders; no installer, pin change or repair was run here.

The public stage also uses ordinary copy/rsync tools on the runner. `.nojekyll` is an empty shipping marker. `.gitignore` retains the scrape-response, preview, historical source-home capture and platform-metadata rules.

The documentation rules ignore all new `docs/verification/` outputs except the exact canonical `manifest.json` and `review.json` paths. Other private check evidence is not automatically eligible for Git. Handbook assets stay ignored. The documentation tree recursively ignores directories named `_generated`, `.generated`, `build`, `node_modules` and `.fixture`. Within the handbook, recursive patterns ignore names beginning `.env`, files ending `.env`, names beginning `credentials`, and files ending `.log` or `.db`. The copied `.docs-check/` tree also stays ignored. No documentation assets are currently approved here.

These rules govern Git's treatment of untracked files; they neither remove an already tracked product nor change the workflow's public allowlist. Ignore status is not confidentiality or publication control. Existing tracked legacy files stay tracked until a separately approved index change; do not stage, untrack or clean them merely to satisfy documentation review.

See [CLI reference](generator-and-checker-cli.md), [publication review](../how-to/review-publication-and-domain-evidence.md) and [maintenance](../maintenance/change-impact-and-docs-ownership.md).
