---
title: Verification and troubleshooting
description: Map real failure symptoms to owning sources without using generated edits
  or live actions as blind repairs.
kind: how-to
source_ref:
- tests/check-site.py#L1-L80
- build-menus.py#L11-L14
- build-menus.py#L158-L187
- build-blog.py#L13-L46
- build-blog.py#L88-L111
- script.js#L202-L229
- .github/workflows/deploy-pages.yml#L35-L59
- LAUNCH.md#L34-L56
---

# Verification and troubleshooting

Start with the safe [offline check](../tutorials/check-the-shipped-site-offline.md) and preserve the first error. Do not turn an uncertain symptom into a provider/DNS change, broad cleanup or generated-HTML patch.

## Generator failures

| Symptom/error | Actual cause to investigate | Safe next step |
|---|---|---|
| JSON/key/iteration exception in menu builder | Malformed source or missing expected key/type | Compare [menu schema](../reference/menu-source.md); obtain approval for source correction |
| Regex `.group(0)` failure before render | Home sprite/header/footer no longer matches exact extraction pattern | Inspect authored shell and generator together; do not add a guessed fallback |
| Menu homepage substring not found | Exact menus-grid/menus-cta boundary missing or changed | Inspect both potential outputs; menu page may already be written |
| Invalid slug / modification predates publication | Metadata disagrees with filename/date rules | Correct authorized metadata, not generated URL/date text |
| Missing eligible body/image | Pair incomplete or image not local existing file | Review [article schema](../reference/article-source-and-metadata.md), rights and path |
| No published post | UTC gate excludes everything or inputs absent | Check truthful publication dates; do not change date just to silence a build |
| Home blog markers missing/duplicated | Replacement region count not exactly one | Inspect all article/index outputs already written before failure |
| Removed source but old URL remains | Builder does not prune output dirs | Use [retirement review](../how-to/change-or-retire-article-source.md); no automatic deletion |

Both generators can leave partial products. A nonzero command does not mean a clean no-change result. Protect unrelated work and inspect the full write set.

## Checker failures

Duplicate id, missing H1/description/canonical, broken href/src/fragment, article schema/date/author mismatch and sitemap/RSS inconsistency are explicit assertions. Read the named target and current template/input. The checker uses current public products and normal `assert`; disabled assertions invalidate its usefulness.

External links are skipped. CSS url references, browser JavaScript, layout, accessibility, exact content freshness, image rights, production HTTP and inbox receipt are outside this check. The [testing guide](../developer/testing-and-extension-points.md) distinguishes each evidence class.

## Inquiry symptoms

| Observation | What code says | Limit |
|---|---|---|
| Button says Open email to send | Hidden routing missing/blank/exact placeholder | Draft still needs user send; mail handler may be absent |
| Enhanced submission remains pending | Fetch has no custom timeout/retry | Do not claim it was delivered or repeatedly resubmit automatically |
| Error contact fallback | Fetch/HTTP/JSON/explicit success gate failed | Preserve error; owner's approved live test is separate |
| Thank-you page visible | Navigation occurred or URL opened directly | Not an inbox receipt |
| Menu not preselected | Unknown value or missing matching static option | Compare id/route/options without submitting |

The historical automation preflight rejection in `LAUNCH.md` did not establish customer-browser failure. A subsequent owner confirmation is dated September 10. Do not buy a plan, switch providers or access the mailbox to settle a documentation question.

## Release and schedule symptoms

Workflow source is not a current CI result. It rebuilds only blog content and does not run the site checker. The portable documentation gate can fail on missing/nonregular/changed indexed policy, receipt inventory mismatch, stale or changes-required review, or source/docs disagreement. It checks the complete submitted index; an unstaged repair cannot approve old submitted bytes. Parent owns generated-bundle refresh and integration, so do not hand-edit copied executors, change tests/pins, stage files or spoof acceptance to hide a failure.

The weekly authoring workflow is outside this repository. A missing date/article does not prove job failure. Obtain evidence through the owning business workflow without copying private job/billing/account records here.

See [publication review](../how-to/review-publication-and-domain-evidence.md), [current status](../status.md), and [maintenance](../maintenance/change-impact-and-docs-ownership.md) before handoff.
