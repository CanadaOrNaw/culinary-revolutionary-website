#!/usr/bin/env python3
"""Render menus.html and the homepage teaser grid from menus.json."""
import json, html, sys, re, pathlib

REPO = pathlib.Path(__file__).resolve().parent
DATA = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else REPO / "menus.json")
menus = json.loads(DATA.read_text())["menus"]

e = lambda s: html.escape(str(s or ""), quote=True)

SPRITE = (REPO / "index.html").read_text()
sprite = re.search(r'  <!-- Icon sprite.*?</svg>\n', SPRITE, re.S).group(0)
header = re.search(r'  <header class="site-header">.*?</header>\n', SPRITE, re.S).group(0)
footer = re.search(r'  <footer class="site-footer">.*?</footer>\n', SPRITE, re.S).group(0)

# On menus.html the nav must point back at index.html anchors.
nav = header
for frag in ("home", "services", "service-area", "about", "inquiry"):
    nav = nav.replace(f'href="#{frag}"', f'href="index.html#{frag}"')
nav = nav.replace('href="#sample-menus"', 'href="menus.html"')
nav = nav.replace('<li><a href="menus.html">Sample Menus</a></li>',
                  '<li><a href="menus.html" aria-current="page">Sample Menus</a></li>')

blocks, toc = [], []
for m in menus:
    mid = e(m["id"])
    toc.append(f'      <li><a href="#{mid}">{e(m["title"])}</a></li>')
    courses = []
    for c in m["courses"]:
        note = (f'<span class="course-note">{e(c["note"])}</span>'
                if c.get("note") else "")
        items = []
        for it in c["items"]:
            desc = (f'\n              <span class="dish-desc">{e(it["description"])}</span>'
                    if it.get("description") else "")
            items.append(
                '            <li>\n'
                f'              <span class="dish-name">{e(it["name"])}</span>{desc}\n'
                '            </li>'
            )
        courses.append(
            '        <div class="course">\n'
            '          <div class="course-head">\n'
            f'            <h3>{e(c["name"])}</h3>{note}\n'
            '          </div>\n'
            '          <ul class="dish-list">\n'
            + "\n".join(items) + "\n"
            '          </ul>\n'
            '        </div>'
        )
    sel = (f'\n          <p class="menu-selection-note">{e(m["selectionNote"])}</p>'
           if m.get("selectionNote") else "")
    blocks.append(
        f'      <article class="menu-block" id="{mid}">\n'
        '        <div class="menu-block-head">\n'
        f'          <h2>{e(m["title"])}</h2>\n'
        f'          <p class="menu-blurb">{e(m["blurb"])}</p>{sel}\n'
        '        </div>\n'
        + "\n".join(courses) + "\n"
        '        <div class="menu-block-cta">\n'
        f'          <a class="button primary" href="index.html?menu={mid}#inquiry">Request this menu</a>\n'
        '        </div>\n'
        '      </article>'
    )

page = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Private Chef Sample Menus | Culinary Revolutionary</title>
  <meta
    name="description"
    content="Explore seven customizable private chef menus for dinners and events on South Florida's Gulf Coast: Italian, brunch, Spanish, Key West, wild game, tapas and vegetarian."
  />
  <meta name="theme-color" content="#0a1f44" />
  <link rel="canonical" href="https://culinary-revolutionary.com/menus.html" />

  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="Culinary Revolutionary" />
  <meta property="og:title" content="Private Chef Sample Menus | Culinary Revolutionary" />
  <meta property="og:description" content="Seven customizable sample menus from a private chef serving South Florida's Gulf Coast." />
  <meta property="og:image" content="https://culinary-revolutionary.com/public/assets/hero.jpg" />
  <meta property="og:url" content="https://culinary-revolutionary.com/menus.html" />
  <meta name="twitter:card" content="summary_large_image" />

  <link rel="icon" href="favicon.ico" sizes="any" />
  <link rel="apple-touch-icon" href="public/assets/apple-touch-icon.png" />

  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link
    href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Inter:wght@400;500;700&display=swap"
    rel="stylesheet"
    media="print"
    onload="this.media='all'"
  />
  <noscript>
    <link
      href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Inter:wght@400;500;700&display=swap"
      rel="stylesheet"
    />
  </noscript>
  <style>
    .icon-sprite {{ position: absolute; width: 0; height: 0; overflow: hidden; }}
    .social-links {{ display: flex; align-items: center; gap: 0.15rem; margin: 0; padding: 0; list-style: none; }}
    .social-links a {{ display: inline-flex; align-items: center; justify-content: center; width: 2.4rem; height: 2.4rem; }}
    .social-links svg {{ display: block; width: 20px; height: 20px; fill: currentColor; }}
  </style>
  <link rel="stylesheet" href="styles.css?v=20260910-blog" />
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>

{sprite}
{nav}
  <main id="main" tabindex="-1">
    <section class="section" id="menus">
      <div class="container">
        <p class="eyebrow">Sample Menus</p>
        <h1>Seven starting points, all of them yours to change</h1>
        <p class="section-intro">
          These are the menus guests ask for most. Treat them as a starting point rather
          than a fixed list — courses, dishes, and portion styles are all adjustable, and
          dietary needs are planned in from the start. Pricing depends on the number of
          courses, the dishes you choose, and your guest count, so every quote is built
          for your event.
        </p>
        <nav aria-label="Jump to a menu">
          <ul class="menu-toc">
{chr(10).join(toc)}
          </ul>
        </nav>
      </div>
    </section>

    <div class="container">
{chr(10).join(blocks)}

      <section class="menus-outro">
        <h2>Not seeing quite the right thing?</h2>
        <p>
          Most events end up as a blend — a few dishes from one menu, a course from
          another, something built around a family recipe. Tell me the occasion and the
          guest list and I will draft a menu for it.
        </p>
        <a class="button primary" href="index.html#inquiry">Start an inquiry</a>
      </section>
    </div>
  </main>

{footer}
  <script src="script.js?v=20260910-blog"></script>
</body>
</html>
'''

(REPO / "menus.html").write_text(page)
print(f"menus.html written: {len(page)} bytes, {len(menus)} menus, "
      f"{sum(len(c['items']) for m in menus for c in m['courses'])} dishes")

# ---- homepage teaser grid ----
cards = []
for m in menus:
    mid, courses = e(m["id"]), m["courses"]
    chips = "\n".join(
        f'              <li>{e(c["name"])}</li>' for c in courses[:4]
    )
    cards.append(
        '          <article class="menu-card">\n'
        f'            <h3>{e(m["title"])}</h3>\n'
        f'            <p class="menu-teaser">{e(m["blurb"])}</p>\n'
        '            <ul class="menu-courses">\n'
        + chips + "\n"
        '            </ul>\n'
        f'            <a class="text-link" href="menus.html#{mid}">See the full menu →</a>\n'
        '          </article>'
    )

idx = (REPO / "index.html").read_text()
start = idx.index('        <div class="menus-grid">')
end = idx.index('        <p class="menus-cta">', start)
idx = (idx[:start]
       + '        <div class="menus-grid">\n' + "\n".join(cards) + '\n        </div>\n'
       + idx[end:])
(REPO / "index.html").write_text(idx)
print("index.html teaser grid replaced")
