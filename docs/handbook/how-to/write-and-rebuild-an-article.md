---
title: Write and rebuild an approved article
description: Prepare a real metadata/body pair and review every generated artifact
  before publication.
kind: how-to
source_ref:
- README.md#L80-L108
- build-blog.py#L27-L46
- build-blog.py#L75-L111
- content/blog/planning-private-chef-dinner-south-florida-gulf-coast.json#L1-L13
- content/blog/planning-private-chef-dinner-south-florida-gulf-coast.html#L1-L52
---

# Write and rebuild an approved article

This is a maintenance workflow, not an automatic publishing authorization. Keep billing, account details, private job notes and customer stories outside source and output. Do not invent cities, prices, reviews, awards, event stories or a chef's personal byline.

## Prepare the pair

1. Inspect the existing `planning-private-chef-dinner-south-florida-gulf-coast` metadata/body pair under `content/blog/` as the concrete field/layout example.
2. Choose an approved lowercase hyphenated slug. Metadata filename stem and `slug` must match.
3. Add the `.json` metadata and same-stem `.html` article body. Use actual publication/modification dates; modification must not predate publication.
4. Use an existing approved local image and descriptive alt text. File existence is all the builder checks; it does not establish licensing or truth of the image description.
5. Write trusted HTML paragraphs/headings/lists/links. Use the exact h2/id convention in [article reference](../reference/article-source-and-metadata.md) for the contents navigation.
6. Include useful links to relevant sample-menu anchors and the inquiry route. Generated sidebar links alone are not a substitute for useful body copy.

Use Culinary Revolutionary as the organization author unless the chef truly authors or approves a personal byline. The current offline checker explicitly requires the organization name, so a byline change also needs a deliberate code/test decision outside ordinary article copy editing.

## Build and check only after approval

The existing project sequence from repository root is:

```bash
python3 build-blog.py
python3 build-menus.py
python3 tests/check-site.py
```

Both builders rewrite repository products. They were not executed during this documentation authorship. The checker is safe/offline; its author result is in [status](../status.md).

Expected blog success prints the count of eligible articles and says it built the index, RSS, homepage preview and sitemap. Check the complete diff, not just that message:

- New/changed `blog/SLUG/index.html` with body, canonical and social/schema dates.
- Blog index order and organization attribution.
- Homepage latest-card preview (newest publication, slug tie-break descending).
- RSS item and sitemap destination/date.
- All relevant local links and article contents anchors.

Reading time is a rough stripped-HTML word estimate at 200 words/minute, rounded with a minimum of one minute. It is not a tracked reading metric.

## Dates, revisions and failures

Future publication dates are skipped using the current UTC date. Skipped drafts do not test body/image completeness yet. A future date does not schedule a build/deploy. Removing or future-dating an old source does not delete its generated directory.

If the builder rejects slug/date/image or homepage markers, preserve the error and inspect all outputs: article/index writes may already have happened. Use [troubleshooting](../operations/verification-and-troubleshooting.md); never fix generated HTML alone.

For revisions or removal, follow [change or retire an article](change-or-retire-article-source.md). For any main push/manual deployment, first follow [publication review](review-publication-and-domain-evidence.md).
