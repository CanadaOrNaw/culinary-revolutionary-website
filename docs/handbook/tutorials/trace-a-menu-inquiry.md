---
title: Trace a menu inquiry without sending
description: Connect one real menu id, generated request route and browser preselection
  through source only.
kind: tutorial
source_ref:
- menus.json#L4-L15
- build-menus.py#L25-L64
- build-menus.py#L162-L187
- index.html#L546-L557
- script.js#L99-L109
- script.js#L142-L229
---

# Trace a menu inquiry without sending

**Outcome:** explain why an Italian Feast request selects the right inquiry option. This is a source-reading exercise, not a browser or delivery acceptance test.

## Prerequisites and safety

Use the local checkout and a text reader. Do not start a server, run a generator, copy the form routing value, click a contact link or submit anything. The files needed are public sample-menu code/data, not customer inquiries.

## Follow one stable id

1. In `menus.json`, find the first menu's `id`: `italian-feast`. Its title is Italian Feast and the first course is Antipasti.
2. In `build-menus.py`, follow `mid` from that id into the full menu article anchor and request link. The expected request route is:

```text
index.html?menu=italian-feast#inquiry
```

3. In the current generated menu page, find that route. No request is sent by reading it.
4. In `index.html`, find the `menu-interest` select. It has an option whose value is `italian-feast`.
5. In `script.js`, follow `URLSearchParams(...).get("menu")`. The script compares lowercased option values, and sets the select only when there is a match. Unknown values are ignored; the fragment simply targets the inquiry section.

## Observe the contract

All seven source menu ids currently match static form options. That correspondence is a source comparison, not something `build-menus.py` creates automatically. Adding a menu without updating the form options would generate a request link that cannot preselect its new value.

Continue in `script.js` from submit to the enhanced payload and response gate. `menu` becomes `menu_of_interest`; success requires an OK response and JSON `success` exactly `true`. Without JavaScript the native form uses the original `menu` name. Read [inquiry dataflow](../architecture/inquiry-and-personal-data.md) for the full distinction.

## Failure and recovery

If the id, link or option differs, record each source location and stop. A documentation exercise does not authorize editing public copy or regenerating output. The maintainer uses [menu editing](../how-to/update-menus.md) to coordinate all affected sources under approval.

No cleanup is needed. For exact DOM ids, options and request fields, use [browser reference](../reference/browser-contracts-and-form.md).
