# Culinary Revolutionary — website

A dependency-free static site. No build step, no framework: open `index.html` and it runs.

- `index.html` — home (hero, services, service area, menu teasers, about, inquiry form)
- `menus.html` — all seven sample menus, 240 dishes, generated from the chef's Word doc
- `thank-you.html` — post-submission confirmation
- `styles.css`, `script.js` — the site
- `robots.txt`, `sitemap.xml` — crawl control
- `blog/` — generated public blog index, articles and RSS feed
- `content/blog/` — one JSON metadata file and matching HTML article per post
- `build-blog.py` — builds blog pages, homepage preview, RSS and sitemap
- `public/assets/` — locally copied imagery (`ASSET-SOURCES.json` records provenance)
- `DESIGN.md` — extracted design system

`ASSET-SOURCES.json`, `DESIGN.md` and `README.md` are **build notes, not site content**, and
the deploy workflow deliberately excludes them from the published artifact.

## Preview locally

```bash
python3 -m http.server 8096 --bind 127.0.0.1
```

## Inquiry form

The form POSTs to **Web3Forms**, which relays the submission to the destination inbox.
There is no application server or site database. Web3Forms currently says free-plan
submissions may be retained for 30 days, so the form discloses the provider rather than
implying a direct browser-to-inbox connection.

**The access key is the only thing to configure**, and it lives in exactly one place —
the hidden input at the top of the form in `index.html`:

```html
<input type="hidden" name="access_key" value="PASTE_WEB3FORMS_ACCESS_KEY_HERE" />
```

Until a real key is pasted there, `script.js` detects the placeholder and falls back to
opening a pre-filled email draft, so the button is never dead.

How it behaves once the key is set:

1. `script.js` intercepts submit and POSTs JSON to `api.web3forms.com`.
2. On success the visitor lands on `thank-you.html`.
3. On failure the form shows the phone number and email rather than losing the inquiry.
4. If JavaScript never loads, the plain HTML `POST` still works — the hidden
   `access_key`, `subject` and `redirect` inputs carry it.

**Destination inbox:** `chef@culinary-revolutionary.com` (Namecheap Private Email).
The mailbox is created and the Web3Forms key is installed. The user confirmed the
live inquiry test worked on 2026-09-10. DKIM DNS publication is verified; reply-to
behavior has not been separately confirmed.

**To change the destination inbox:** request a
new key at <https://web3forms.com> against the new address and replace that one value.
Nothing else changes — no DNS, no SPF/DKIM, because Web3Forms sends *to* the address, not
*as* the domain. Note that the new address must already be able to *receive* mail (i.e. the
domain needs working MX records) before a key can be issued against it.

### Production domain

The live canonical URL is `https://culinary-revolutionary.com/`; `www` redirects
there. HTTPS is enforced. The hidden form redirect uses
`https://culinary-revolutionary.com/thank-you.html`, including without JavaScript.

## Regenerating the menus

`menus.html` and the homepage teaser cards are generated from `menus.json` rather than
hand-edited, so the chef's 240 dishes stay consistent between the two.

```bash
python3 build-menus.py menus.json
```

Edit `menus.json` and re-run, rather than editing `menus.html` directly — a hand edit is
lost the next time the generator runs. `build-menus.py` and `menus.json` are excluded from
the deployed artifact.

## Weekly blog publishing

Add a matching `content/blog/slug.json` and `content/blog/slug.html`, following the
first article's fields. Use the real publication and modification dates, an
existing licensed local image, a useful descriptive title, a unique description,
and links to relevant menus and the inquiry form. Use Culinary Revolutionary as
the organization author unless the chef actually authors or approves a personal
byline. Do not invent service cities, prices, reviews, awards or event stories.

Run `python3 build-blog.py` and `python3 build-menus.py`, then check local links,
mobile navigation, article metadata and the inquiry route. Commit the sources and
generated pages together. The Pages workflow also rebuilds the blog before staging.
Drafts dated in the future are excluded; date-gating is not an automatic publishing
schedule. A future publication still needs a build/deploy. Removing an already
published article requires explicitly removing its generated directory as well.

Articles have crawlable HTML, canonical URLs, social metadata, BlogPosting and
breadcrumb structured data, and inclusion in the sitemap and RSS feed. No ranking
or rich-result guarantee is made. Guidance:
https://developers.google.com/search/docs/appearance/structured-data/article

Billing, weekly task dates and GBP access/verification notes are private operations
records outside this repository. No invoices or customer account files are staged
on the public site. Since September 10, 2026, Aegis has an owner-authorized external
cron to write, validate and publish a weekly article on Thursdays at 09:00
America/Toronto, beginning September 17. That task follows the private Aegis
workflow; it is not a GitHub scheduled content generator. An independent Telegram
reminder announces the run, followed by a verified live-link or failure report.
Invoice sending remains manual. Routine articles must still pass the checks above.

## Deployment workflow

Pushes to `main` deploy to GitHub Pages via `.github/workflows/deploy-pages.yml`. The
workflow stages only the shipping files into `_site/` — it does not upload the repo root.

Because publishing uses **GitHub Actions** (not branch-based publishing), the custom domain
is set in **Settings → Pages**, and any `CNAME` file in the repo is ignored. Do not rely on
a `CNAME` file to set the domain.

## Source and confirmation notes

The biography claims in the About section are taken from the client's existing live
About page and are independently repeated on the chef's Airbnb service listing. They
are client-supplied claims, not additions made by this redesign.

The former draft inferred a six-city service area and Naples address from the 239 phone
number. That inference has been removed. The site now uses the broader, publicly listed
"South Florida Gulf Coast" service area and asks each lead for a city or ZIP. Add city
landing copy only after the chef confirms the exact travel area.

**Missing, and worth adding** (these help higher-value bookings):
- Food-safety certification (ServSafe or Florida food handler) — not currently claimed.
- Liability insurance and whether a certificate can be issued to a venue. Corporate and
  wedding clients frequently cannot book without one.
- Any pricing floor at all ("dinners from $X per guest"). There is currently none.

**Menu questions raised by the source document** — see the chef-questions list handed over
with this build (duplicate "French toast" in Brunch, whether Bagels/Lox/Cream cheese are
one item or three, the Paella Valenciana 4–8 guest limit, and the per-course selection
rules for Brunch and Spanish Tapas).


## 🤖 The part that runs on a schedule

The **weekly blog publishing** flow documented above is one of the recurring business jobs the automation stack is expected to take over. Two properties to preserve when it moves:

1. **Publishing is an outward-facing action.** In the Agrippa design it gets drafted and approved rather than posted autonomously — the same class as sending email or messaging anyone who isn't Zack.
2. **The generator is deterministic.** Menus are regenerated from source rather than hand-edited, which means a bad run can be re-run instead of repaired by hand. Keep that property; it is what makes the job safe to automate at all.

The reminder that drives it lives in [`scripts`](http://127.0.0.1:3000/zack/scripts) as `aegis_culinary_blog_reminder.py`.


---

## 🔗 Where this fits

| Repo | What it holds |
|---|---|
| **[fleet-index](http://127.0.0.1:3000/zack/fleet-index)** | every device, every path, every git history — and what happens to each in the refresh |
| **[agrippa](http://127.0.0.1:3000/zack/agrippa)** | the private AI system being built on top: the OS, the harness, the runtime |

<sub>Mirrored to Gitea by <code>~/.local/bin/gitstack_sync.sh</code>. Index checked against reality daily at 05:45 by <code>icm-fidelity.sh</code>.</sub>
