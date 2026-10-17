---
title: Review publication and domain evidence
description: Check the actual Pages exposure boundary and keep dated launch evidence
  separate from live acceptance.
kind: how-to
source_ref:
- .github/workflows/deploy-pages.yml#L1-L71
- README.md#L101-L117
- LAUNCH.md#L32-L91
- ops/verify-domain.sh#L1-L28
- robots.txt#L1-L15
---

# Review publication and domain evidence

A push to main or manual workflow dispatch deploys the public business site. Neither is a routine documentation check. The launch owner retains approval of publication, accounts, DNS and live inquiry tests.

## Review the actual workflow

| Stage | Current implementation | Consequence |
|---|---|---|
| Trigger | Main push or manual dispatch | No GitHub scheduled writing trigger |
| Runner | Ubuntu latest; Python 3.12 selected | Native local Python minimum still undeclared |
| Gate | Portable submitted-index documentation check | Requires reviewed source/docs and exact submitted policy bytes; not business acceptance |
| Generation | Blog builder only | Menus must already have been regenerated/reviewed locally |
| Staging | Explicit root-file copies plus blog/assets trees | Never upload repository root |
| Deployment | GitHub Pages environment/actions | Remote run state not observed here |

The workflow does not run `tests/check-site.py`. Run safe local checks deliberately; do not infer them from a deployment job's existence. The generated shared docs gate validates the complete submitted snapshot and policy bundle, not just the working tree. It cannot invent independent correctness review. A present local bundle is not proof those seven files reached a clean CI checkout; actual index/submission and remote run evidence remain separate.

## Public artifact boundary

Shipping includes home/menu/thank-you HTML, CSS/JS, favicon, robots, sitemap, two public verification materials, blog tree, `.nojekyll`, optional `CNAME`, and public assets except the large original logo and historical source-home capture.

Excluded roots include authored article/menu sources, generators, tests, ops, private handbook/verification, copied docs checker, README/design/provenance notes, caches and previews. Recursive `blog/` and asset copying means a new private file placed there could still leak. Inspect those contents rather than relying only on the root allowlist.

`robots.txt` disallow lines are crawl hints, not access control. Private material must not enter the artifact at all.

## Domain and email authority

The README assigns the Actions-based custom domain to Pages settings, not reliance on a `CNAME` file. Current workflow code still conditionally copies that file. Source can show both facts without claiming remote Pages settings were checked.

`LAUNCH.md` records September 10 production/DNS/mailbox and inquiry confirmations, remaining reply-to/DMARC/contact-verification uncertainty, and established registrar/mailbox/hosting decisions. Read its dates. Do not restore old nameservers or switch providers because a historical automation-only preflight failed.

The optional command is:

```bash
bash ops/verify-domain.sh
```

It was not run here. It makes external RDAP/DNS/HTTP requests and prints observations; exit 0 does not assert expected records or inbox delivery. See [CLI reference](../reference/generator-and-checker-cli.md#domain-diagnostic).

## Release checklist under approval

1. Resolve relevant chef approvals and inspect approved source/product changes together.
2. Run the offline site checker; review browser behavior separately if in scope.
3. Review private/public staging boundaries and stale blog directories.
4. Have the business owner authorize the exact publish action and obtain current CI/live evidence if required.
5. Keep provider acceptance, inbox delivery and reply-to tests separately labeled. Preserve errors and dates.

No push, dispatch, DNS change, mailbox access or live form submission is authorized merely by this guide. [Status](../status.md) and [collaboration](../collaboration.md) explain current evidence ownership.
