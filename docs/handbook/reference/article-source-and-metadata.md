---
title: Article source and metadata
description: Look up metadata fields, trusted HTML conventions, date/image validation
  and generated SEO/feed fields.
kind: reference
source_ref:
- content/blog/planning-private-chef-dinner-south-florida-gulf-coast.json#L1-L13
- content/blog/planning-private-chef-dinner-south-florida-gulf-coast.html#L1-L52
- build-blog.py#L27-L46
- build-blog.py#L48-L110
- tests/check-site.py#L49-L80
- content/blog/choosing-a-private-dinner-menu-for-different-preferences.html#L1-L57
- content/blog/choosing-a-private-dinner-menu-for-different-preferences.json#L1-L13
- content/blog/in-home-cooking-classes-planning-hands-on-experience.html#L1-L23
- content/blog/in-home-cooking-classes-planning-hands-on-experience.json#L1-L13
- content/blog/private-chef-dinner-or-event-catering-how-to-choose.html#L1-L22
- content/blog/private-chef-dinner-or-event-catering-how-to-choose.json#L1-L13
- content/blog/what-to-discuss-before-booking-weekly-meal-preparation.html#L1-L26
- content/blog/what-to-discuss-before-booking-weekly-meal-preparation.json#L1-L13
---









# Article source and metadata

Each article is a JSON metadata file plus a same-stem HTML body in `content/blog/`. There is no Markdown converter, CMS API or formal JSON Schema. The builder derives its contract from direct field access and a few explicit checks.

## Metadata fields

All listed fields are required for an eligible post and intended to be strings. Missing keys raise ordinary exceptions; most text types are not explicitly checked.

| Field | Meaning and constraint |
|---|---|
| `slug` | Lowercase alphanumeric segments joined by single hyphens; must equal JSON filename stem |
| `title` | Visible article/card heading and schema headline |
| `seo_title` | Document title and social title for article page |
| `description` | Meta/social/schema description |
| `date_published` | ISO date parsed by Python; UTC date gate and ordering |
| `date_modified` | ISO date; cannot precede publication; schema/social/sitemap modification |
| `category` | Visible category label |
| `author` | Visible byline and Organization author name; checker requires Culinary Revolutionary |
| `image` | Existing local file path; current sources use root-relative public assets |
| `image_alt` | Visible article image alternative text |
| `excerpt` | Lede/card text and RSS description |

The existing planning-private-chef article pair is the concrete source example. Use true dates, approved copy and rights-cleared imagery, not placeholder facts.

## Explicit validation and errors

| Rule | Failure/selection |
|---|---|
| Slug full-match and filename agreement | `Invalid slug in NAME` |
| Date parse | Python date parsing exception for invalid ISO date |
| Modified before published | `Modification predates publication: NAME` |
| Publication after current UTC date | Skip this post before body/image loading |
| Eligible body missing | File-read exception on same-stem `.html` |
| Image path not a file | `Missing image: PATH` |
| No eligible posts | `At least one published post is required` |
| Home preview marker replacement count not exactly one | `Homepage blog preview markers missing or duplicated` after earlier output writes |

Image validation is existence only. The builder does not confine traversal to approved assets, verify licenses, validate alt-text truth, restrict author choices or check all required types up front. Approved inputs and review supply that boundary.

## Body HTML and contents

The body is trusted HTML inserted without sanitization. Use ordinary reviewed headings, paragraphs, lists and links, not scripts, account data or copied customer records. Metadata is escaped, but that does not sanitize body markup.

Contents extraction matches h2 tags with a double-quoted id in the exact pattern; a simple example is:

```html
<h2 id="occasion">Start with the occasion</h2>
```

Different attributes/spacing, missing ids, or multiline patterns may not appear in contents. Heading text is reused in that navigation. Keep ids unique and test local fragments. There is no supported Markdown-heading conversion.

## Generated metadata and feeds

| Output | Fields/rules |
|---|---|
| Article HTML | Canonical URL, description, Open Graph, Twitter card, publication/modification tags |
| JSON-LD | BlogPosting plus BreadcrumbList, Organization author/publisher, image, dates, language and blog membership |
| Blog index | Blog JSON-LD and cards sorted newest publication, slug descending |
| Homepage preview | Single newest post card, heading level adapted for home |
| Sitemap | Home/menu/blog index and eligible article URLs; menu date fixed in source |
| RSS 2 | Item title/link/permalink guid, publication at UTC midnight, excerpt description |

`BASE` is hardcoded to the canonical business origin. Home lastmod uses max(article modification date, `2026-09-22`); menu lastmod is `2026-09-10`. These constants need deliberate maintenance when facts change.

JSON-LD escapes `<` in serialized schema. This is not a general body sanitizer. The checker verifies selected metadata/links, not complete schema conformance or indexing/rich-result eligibility.

## Revision and removal

A date gate is not a scheduler. Old generated directories are not pruned. See [article maintenance](../how-to/write-and-rebuild-an-article.md) and [revision/retirement](../how-to/change-or-retire-article-source.md) before changing live URL eligibility.
