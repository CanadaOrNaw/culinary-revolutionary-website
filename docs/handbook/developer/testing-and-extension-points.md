---
title: Testing and real extension points
description: Understand what the native checker proves and which additions require
  changes beyond data arrays.
kind: developer
source_ref:
- tests/check-site.py#L1-L80
- LAUNCH.md#L34-L45
- .github/workflows/deploy-pages.yml#L35-L59
- build-menus.py#L25-L64
- build-menus.py#L164-L178
- build-blog.py#L27-L46
- build-blog.py#L81-L90
- index.html#L546-L557
- script.js#L20-L237
---

# Testing and real extension points

## Native test entry

`python3 tests/check-site.py` is the only persisted project test program in the inspected tree. It uses standard-library parsers and current public outputs as inputs. There is no separate fixture directory, package test runner or browser-automation harness.

[The offline tutorial](../tutorials/check-the-shipped-site-offline.md) gives a reproducible run and failure interpretation. Do not import top-level builders as test libraries: both execute writes at import/top level rather than exposing a side-effect-free module API.

## Coverage and gaps

| Check | Covers | Does not cover |
|---|---|---|
| HTML parser/assertions | Local href/src existence, known ids/fragments, H1/description/canonical shape | Browser layout, JS, CSS url assets, external links |
| Article assertions | Selected BlogPosting fields, author/date/order constraints, inquiry/menu links | Editorial truth, complete schema.org validation, useful in-body links |
| Sitemap/RSS parsing | Unique existing destinations, blog canonical membership, item count | Search indexing/ranking, live HTTP state, exact feed text correctness |
| Source comparison in author audit | Five body/output matches and seven menu option matches | A persisted regression suite or full generator determinism test |
| Launch record | Historical browser response/mobile/preselection exercise | A current replayable browser fixture in this checkout |

CI source calls the portable submitted-index documentation gate before the blog builder, not this site checker or menu builder. Its executor, helper, validator, schemas, portable registry and receipt must be present and byte-matched in the complete submitted index. Working-tree acceptance cannot approve an older or missing index submission. An installed hook file or workflow command alone does not prove invocation or remote CI success. No real-index staging or application-test change was performed for this documentation update.

## Extend menu data deliberately

The builder loops arbitrary menu/course/item arrays and escapes displayed values. It does not validate ids as slugs or require uniqueness. Adding a menu also needs explicit review of:

- Static inquiry dropdown values and query preselection.
- Hardcoded seven-menu language in home/templates/metadata.
- Article links into menu anchors.
- Course selection/minimum rules and chef approval.

First-four-course chips are a display rule, not a limit on full-page courses. See [menu reference](../reference/menu-source.md).

## Extend articles through the actual pair interface

Add a valid JSON/body pair, existing approved local image and eligible UTC publication date. The builder supports these authored inputs, not plugins, a CMS endpoint, Markdown conversion, arbitrary output directories or per-post flags. Trusted body HTML must be reviewed as code-bearing content; there is no sanitizer.

An author/byline change needs care: the builder accepts the supplied author string, but the checker currently asserts Culinary Revolutionary. Supporting another author is therefore a code/test policy change, not a harmless metadata-only assumption.

## Change browser or shared chrome contracts

Keep specific DOM ids and `.open`/status classes coordinated across markup/script/styles. Both generators extract exact homepage header/footer/sprite patterns and rewrite selected href/src text. A markup change can silently defeat a string replacement or cause regex `.group(0)` failure. Review all generated chrome and the separately authored thank-you shell.

Use [maintenance](../maintenance/change-impact-and-docs-ownership.md) to map each changed interface to docs and safe tests. Product fixes and new test harnesses require their own implementation scope; this handbook does not pretend they already exist.
