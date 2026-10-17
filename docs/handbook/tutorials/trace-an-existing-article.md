---
title: Trace an existing article to its products
description: Read a real metadata/body pair and identify all affected generated artifacts
  without running a builder.
kind: tutorial
source_ref:
- content/blog/planning-private-chef-dinner-south-florida-gulf-coast.json#L1-L13
- content/blog/planning-private-chef-dinner-south-florida-gulf-coast.html#L1-L52
- build-blog.py#L27-L46
- build-blog.py#L78-L111
---

# Trace an existing article to its products

**Outcome:** identify the complete impact of an article edit before authorizing writes. This exercise reads local source and products only.

## Prerequisites

Use the checkout and a text reader. Do not run the builder, start a server or open external links. The existing planning-private-chef-dinner-south-florida-gulf-coast pair is published business advice, not a customer record.

## Read the pair

1. Read that slug's JSON under `content/blog/`. Find title, SEO title, description, publication/modification dates, category, organization author, local image, alt text and excerpt.
2. Read its same-stem HTML. It starts with introductory paragraphs, uses h2 ids such as `occasion`, and links to menus/inquiry.
3. Trace the builder's slug/date checks and UTC future gate. This source's September 10 date is eligible in the reviewed October 17 snapshot.
4. Inspect the generated `blog/SLUG/index.html` as text and locate the same authored body. Follow the surrounding template's metadata, image, byline, contents and sidebar.
5. List every write after article rendering: blog index, homepage latest card, sitemap and RSS. This older sample is not necessarily the latest homepage card.

## Observable result

You should be able to name all five output groups and explain the difference between title and SEO title, publication ordering and modification dates. The author audit found five complete pairs, five corresponding article directories and exact body text in each counterpart; that is a comparison at one snapshot, not a builder-freshness guarantee.

The newest source in the reviewed snapshot is dated October 8. This alone says nothing about an October 15 external job. No scheduler inspection is part of the exercise.

## Failure and recovery

A missing pair member, missing image, changed slug or unexpected stale output is a finding to preserve. Use [article reference](../reference/article-source-and-metadata.md) and [retirement review](../how-to/change-or-retire-article-source.md), not a guessed rebuild/removal. No cleanup is needed.

Next, read [write and rebuild an approved article](../how-to/write-and-rebuild-an-article.md) for the separate authorized maintenance workflow.
