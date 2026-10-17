---
title: Menu source reference
description: Look up menu fields, order, rendering rules and validation gaps without
  copying the full menu catalog.
kind: reference
source_ref:
- menus.json#L1-L15
- menus.json#L218-L236
- menus.json#L588-L595
- menus.json#L1194-L1234
- build-menus.py#L6-L9
- build-menus.py#L25-L64
- build-menus.py#L164-L178
- index.html#L546-L557
---

# Menu source reference

The renderer consumes `menus.json`. It is JSON with a code-inferred shape, not a formally validated JSON Schema. The full chef catalog remains at its owning source; this page explains the interface rather than duplicating 240 dishes.

## Fields

| Field | Intended type | Required by renderer? | Use |
|---|---|---|---|
| `menus` | Array | Yes | Ordered menus |
| `menus[].id` | String | Yes | Article anchor and inquiry-query id |
| `menus[].title` | String | Yes | Heading and navigation/card label |
| `menus[].blurb` | String | Yes | Menu/card description |
| `menus[].selectionNote` | String | No | Nonempty selection paragraph |
| `menus[].courses` | Array | Yes | Ordered courses |
| `courses[].name` | String | Yes | Course heading; first four appear as card chips |
| `courses[].note` | String | No | Nonempty course selection note |
| `courses[].items` | Array | Yes | Ordered dish list |
| `items[].name` | String | Yes | Dish name |
| `items[].description` | String | No | Nonempty extra description |
| Root `typosFixed` | Array of editorial strings | No | Not read/rendered by generator |
| Root `ambiguities` | Array of editorial strings | No | Not read/rendered; chef-review questions |

Nested field paths in the table are under the current menu/course. Required means direct key access; the program does not separately validate types, lengths, unique ids or course counts. `json.loads`, iteration and normal exceptions expose malformed input.

## Current source structure

The reviewed data contains seven menus, 29 courses and 240 items:

| Menu id | Courses | Items |
|---|---:|---:|
| `italian-feast` | 5 | 44 |
| `brunch` | 7 | 80 |
| `tour-of-spain` | 4 | 37 |
| `key-west-inspired` | 4 | 17 |
| `wild-game` | 4 | 16 |
| `spanish-tapas` | 2 | 25 |
| `vegetarian` | 3 | 21 |

These counts describe this source snapshot, not a permanent validator limit or a chef's available capacity. Selection notes and guest restrictions are authored copy, not pricing/booking logic.

## Rendering and safety

Displayed values pass through `html.escape(str(value or ""), quote=True)`. Optional note/description blocks render only for truthy values. Full page order follows arrays. Homepage cards show at most the first four course names but do not truncate full-menu courses.

The id is HTML-escaped, not validated or URL-encoded as a safe slug. Keep ids stable and simple; review duplicates/invalid values explicitly. The static form options and article links must agree with those ids. The builder does not synchronize them.

## Editorial approval

The source currently has 19 typo notes and 17 ambiguity notes. Those records explain prior interpretation; they are not answers or executable rules. Brunch selection counts, tapas minimums, split items and some dish wording need chef confirmation at `CLIENT-QUESTIONS.md`. Do not normalize or invent answers silently.

Follow [update menus](../how-to/update-menus.md) to coordinate source/product/options changes, or use [the read-only trace](../tutorials/trace-a-menu-inquiry.md).
