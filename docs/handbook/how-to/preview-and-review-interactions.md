---
title: Preview without sending inquiries
description: Review layout and navigation deliberately while keeping local preview
  separate from publishing and delivery tests.
kind: how-to
source_ref:
- README.md#L19-L23
- script.js#L20-L56
- script.js#L99-L109
- index.html#L546-L600
- styles.css#L419-L575
- styles.css#L1168-L1175
---

# Preview without sending inquiries

A visual review needs an HTTP origin because blog, feed and asset links can begin at `/`. Opening `index.html` as a file is not the full routing environment.

## Start only an approved temporary preview

The existing README command, from repository root, is:

```bash
python3 -m http.server 8096 --bind 127.0.0.1
```

This starts a loopback server; it was **not run** for this author snapshot. It serves the repository directory, not the workflow's allowlist. Do not bind it to all interfaces, expose it remotely or leave it running. A port conflict is a preview problem, not permission to change services.

Use your own browser to open the loopback origin on port 8096. Do not let an agent control an account/browser against the launch owner's explicit boundary.

## Review without external actions

- Inspect home, menu and article layouts at desktop and narrow widths. The stylesheet has distinct navigation, content and journal breakpoints; do not infer support from one screenshot.
- Open the mobile menu; follow a local anchor; open it again and press Escape. The menu should close, set `aria-expanded` false and return focus to its toggle on Escape.
- An outside click dismisses the open menu. Resizing beyond 1200 pixels closes it.
- Open the local Italian Feast request route and confirm the menu option. Do not submit; the endpoint still points at the real external provider.
- Review labels, keyboard focus, skip link, error/pending presentation and confirmation-page contrast. The offline parser does not prove these.
- Do not activate telephone, email, social or submit links as part of a layout check. Google Fonts may still make network requests; a local preview is not necessarily offline.

## No-JavaScript limits

Native form POST remains a separate path, but the narrow primary navigation relies on JavaScript to reveal it. Do not claim full no-JavaScript accessibility based only on a native form action. Do not exercise either inquiry path without explicit business acceptance approval.

## Stop and record

Stop the foreground server with Ctrl-C. Record viewport/browser and observed behavior, including failures, rather than labeling it universally accessible. No source or generated file cleanup should be needed.

For an entirely offline first result use [the checker tutorial](../tutorials/check-the-shipped-site-offline.md). For the real form contract use [browser reference](../reference/browser-contracts-and-form.md).
