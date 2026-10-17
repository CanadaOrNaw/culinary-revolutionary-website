---
title: Source to public artifact
description: Trace generator order, shared homepage regions, date gating and partial-write
  failures.
kind: concept
source_ref:
- build-menus.py#L11-L22
- build-menus.py#L158-L187
- build-blog.py#L27-L46
- build-blog.py#L78-L111
- .github/workflows/deploy-pages.yml#L38-L59
- README.md#L89-L108
---

# Source to public artifact

## Menu lifecycle

1. Read the JSON file's `menus` array. A supplied input path may be outside the script directory, but outputs always go beside the script.
2. Extract sprite, header and footer from `index.html`. Rewrite selected navigation anchors for the full menu page.
3. Render every menu/course/item and overwrite `menus.html`.
4. Build homepage cards using the first four course names as chips.
5. Locate the exact menus-grid opening substring and following menus-cta paragraph. Replace that region in `index.html`.

Menu ids become both page anchors and `index.html?menu=ID#inquiry` request links. They must also exist in the manually maintained inquiry options. The generator does not update those options or the hardcoded seven-menu prose.

## Article lifecycle

1. Enumerate `content/blog/*.json` in filename order. Parse metadata and validate slug and dates.
2. Skip a publication date later than **today in UTC**. This occurs before reading that post's HTML body and image.
3. Load eligible same-stem HTML, confirm the image file exists, estimate reading time and sort by publication date then slug descending.
4. Require at least one eligible post. Write each article and the blog index.
5. Replace exactly one homepage BLOG-PREVIEW start/end region with the newest article card.
6. Write the sitemap and RSS feed.

The body is inserted as trusted HTML; there is no sanitizer. The table of contents comes from the exact h2/id pattern described in [article reference](../reference/article-source-and-metadata.md).

## A failed build can still change files

Neither script writes transactionally. A menu run can write `menus.html` before failing to find homepage boundaries. A blog run can write article pages and the index before rejecting missing or duplicate homepage preview markers. Feed/sitemap writes come later.

A nonzero result means **inspect every potential output**, not “nothing changed.” Preserve unrelated work. Do not repair an incomplete run by hand-editing products; correct the authorized source change and rerun only within its approved scope.

## Dates are selection rules, not a scheduler

A future date does not create a timed deployment. A later build/deploy must happen. The external weekly content workflow recorded in the README is not implemented by this repository's Actions trigger.

Deleting or future-dating source does not prune an old generated article directory. The workflow copies the whole blog tree. An old directory can therefore remain publicly reachable even when absent from a new index/feed/sitemap. Use the explicit owner-approved retirement review in [change or retire an article](../how-to/change-or-retire-article-source.md).

Sitemap page dates also contain constants: home uses the maximum article modification date or `2026-09-22`; menus uses `2026-09-10`. A menu edit does not automatically change that date. These are source choices, not an accuracy guarantee.

## Release lifecycle

The workflow triggers on main push or manual dispatch, checks the private handbook snapshot, rebuilds the blog, stages public files and deploys Pages. It does not regenerate menus. Locally approved source and generated products must be reviewed together before publishing.

See [CLI effects and failures](../reference/generator-and-checker-cli.md), [publication review](../how-to/review-publication-and-domain-evidence.md), and [troubleshooting](../operations/verification-and-troubleshooting.md).
