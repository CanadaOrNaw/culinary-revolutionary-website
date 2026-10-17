---
title: Revise or retire an article
description: Handle date changes and stale generated article directories without assuming
  the builder prunes.
kind: how-to
source_ref:
- build-blog.py#L27-L46
- build-blog.py#L78-L111
- README.md#L92-L108
- .github/workflows/deploy-pages.yml#L38-L56
---

# Revise or retire an article

## Revise an existing article

Keep its stable slug unless an approved URL migration is planned. Change the authored metadata/body, use a truthful modification date, and follow [article rebuild review](write-and-rebuild-an-article.md). The builder writes canonical/structured/social dates and sitemap dates from metadata; RSS publication dates remain publication dates.

Changing a publication date affects index/card ordering and UTC eligibility. It is not a way to hide a previously generated URL. The builder neither implements redirects nor records a URL migration history.

## Retire or withhold a previously generated article

The builder only creates/overwrites eligible output. It does not scan for obsolete output directories and delete them. If source is removed or future-dated, an old `blog/SLUG/index.html` can remain on disk. The workflow recursively copies the blog tree, so stale content can still ship even when it disappears from new feeds or indexes.

Under a specific owner-approved change:

1. Identify the authored pair, generated directory, body links, homepage preview, index, sitemap and RSS impact.
2. Decide whether the public URL should remain, be redirected, be replaced or be removed. The current generator provides no redirect/prune command.
3. Have the owning maintainer explicitly handle any approved output removal; do not run a broad cleanup or assume a later build removes it.
4. Rebuild affected products under that approval and review the entire public staging tree.
5. Run the offline checker and inspect remaining inbound links. A checker failure is evidence to investigate, not a deletion instruction.

No removal command is provided as a safe quickstart. Deleting output or publishing URL changes is beyond a read-only exercise.

## Understand external scheduling

The README records a separately owned weekly publishing cron and reminder. The repository workflow has only main-push/manual triggers. The absence of a source file for a date does not diagnose a scheduled-job failure. Ask the business owner for current job evidence rather than making a new scheduler or reading private operational records.

See [source lifecycle](../architecture/source-to-public-artifact.md), [publication review](review-publication-and-domain-evidence.md), and [status](../status.md).
