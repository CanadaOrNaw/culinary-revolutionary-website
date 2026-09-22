#!/usr/bin/env python3
"""Build crawlable blog pages, RSS, homepage preview and sitemap. Standard library only."""
import datetime as dt
import email.utils
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
BASE = "https://culinary-revolutionary.com"
e = lambda value: html.escape(str(value), quote=True)
home = (ROOT / "index.html").read_text()
sprite = re.search(r'  <!-- Icon sprite.*?</svg>\n', home, re.S).group(0)
header = re.search(r'  <header class="site-header">.*?</header>\n', home, re.S).group(0)
footer = re.search(r'  <footer class="site-footer">.*?</footer>\n', home, re.S).group(0)

def chrome(value):
    value = re.sub(r'href="#(home|services|service-area|about|inquiry)"', r'href="/#\1"', value)
    value = value.replace('href="#sample-menus"', 'href="/menus.html"')
    value = value.replace('src="public/', 'src="/public/')
    return value

header, footer = chrome(header), chrome(footer)
header = header.replace('href="/blog/"', 'href="/blog/" aria-current="page"')
posts = []
for path in sorted((ROOT / "content/blog").glob("*.json")):
    post = json.loads(path.read_text())
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", post["slug"]) or path.stem != post["slug"]:
        raise ValueError(f"Invalid slug in {path.name}")
    published = dt.date.fromisoformat(post["date_published"])
    modified = dt.date.fromisoformat(post["date_modified"])
    if modified < published:
        raise ValueError(f"Modification predates publication: {path.name}")
    if published > dt.datetime.now(dt.timezone.utc).date():
        continue  # Drafts dated in the future are not published early.
    post["body"] = path.with_suffix(".html").read_text()
    post["url"] = f'/blog/{post["slug"]}/'
    post["date_label"] = published.strftime("%B %d, %Y").replace(" 0", " ")
    post["minutes"] = max(1, round(len(re.sub(r"<[^>]+>", " ", post["body"]).split()) / 200))
    if not (ROOT / post["image"].lstrip("/")).is_file():
        raise ValueError(f"Missing image: {post['image']}")
    posts.append(post)
posts.sort(key=lambda post: (post["date_published"], post["slug"]), reverse=True)
if not posts:
    raise ValueError("At least one published post is required")

def page(title, description, path, body, schema, image, article=None):
    social = ""
    if article:
        social = f'<meta property="article:published_time" content="{e(article["date_published"])}" />\n<meta property="article:modified_time" content="{e(article["date_modified"])}" />'
    return f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{e(title)}</title><meta name="description" content="{e(description)}" />
<meta name="theme-color" content="#0a1f44" /><link rel="canonical" href="{BASE}{e(path)}" />
<meta property="og:type" content="{'article' if article else 'website'}" />
<meta property="og:site_name" content="Culinary Revolutionary" /><meta property="og:title" content="{e(title)}" />
<meta property="og:description" content="{e(description)}" /><meta property="og:url" content="{BASE}{e(path)}" />
<meta property="og:image" content="{BASE}{e(image)}" /><meta name="twitter:card" content="summary_large_image" />
{social}
<link rel="icon" href="/favicon.ico" sizes="any" /><link rel="apple-touch-icon" href="/public/assets/apple-touch-icon.png" />
<link rel="alternate" type="application/rss+xml" title="Culinary Revolutionary Blog" href="/blog/feed.xml" />
<link rel="preconnect" href="https://fonts.googleapis.com" /><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&amp;family=Inter:wght@400;500;700&amp;display=swap" rel="stylesheet" />
<link rel="stylesheet" href="/styles.css?v=20260910-blog" />
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False).replace('<', chr(92) + 'u003c')}</script>
</head><body>
<a class="skip-link" href="#main">Skip to content</a>
{sprite}{header}
<main id="main" tabindex="-1">{body}</main>
{footer}<script src="/script.js?v=20260910-blog"></script>
</body></html>'''

def card(post):
    return f'''<article class="journal-card"><a class="journal-card-image" href="{post['url']}" tabindex="-1" aria-hidden="true"><img src="{e(post['image'])}" alt="" width="465" height="311" loading="lazy" /></a><div class="journal-card-copy"><p class="eyebrow">{e(post['category'])}</p><h2><a href="{post['url']}">{e(post['title'])}</a></h2><p class="journal-meta"><time datetime="{post['date_published']}">{post['date_label']}</time> · {post['minutes']} min read</p><p>{e(post['excerpt'])}</p><a class="text-link" href="{post['url']}">Read the planning guide <span aria-hidden="true">→</span></a></div></article>'''

blog_dir = ROOT / "blog"
blog_dir.mkdir(exist_ok=True)
for post in posts:
    headings = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', post["body"])
    contents = '<nav class="article-contents" aria-label="In this guide"><h2>In this guide</h2><ul>' + ''.join(f'<li><a href="#{e(anchor)}">{title}</a></li>' for anchor, title in headings) + '</ul></nav>'
    body = f'''<article class="section journal-article"><div class="container"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><a href="/blog/">Blog</a><span aria-hidden="true">/</span><span>{e(post['title'])}</span></nav><header class="article-heading"><p class="eyebrow">{e(post['category'])}</p><h1>{e(post['title'])}</h1><p class="journal-meta">By <a href="/#about">{e(post['author'])}</a> · <time datetime="{post['date_published']}">{post['date_label']}</time> · {post['minutes']} min read</p><p class="article-lede">{e(post['excerpt'])}</p></header><div class="article-layout"><div class="article-body"><figure class="article-image"><img src="{e(post['image'])}" alt="{e(post['image_alt'])}" width="465" height="311" fetchpriority="high" /><figcaption>Private-dining inspiration; illustrative image.</figcaption></figure>{post['body']}</div><aside>{contents}<div class="article-aside-cta"><p class="eyebrow">Make it personal</p><h2>Tell us about your evening</h2><p>Share your date, city or ZIP, guest count and menu ideas with Chef JB.</p><a class="button primary" href="/#inquiry">Plan your dinner</a><a class="text-link" href="/menus.html">Explore sample menus</a></div></aside></div><div class="article-bottom"><a class="text-link" href="/blog/">← All planning guides</a></div></div></article>'''
    schema = {"@context":"https://schema.org", "@graph":[
        {"@type":"BlogPosting", "@id":BASE+post["url"]+"#article", "headline":post["title"], "description":post["description"], "url":BASE+post["url"], "mainEntityOfPage":BASE+post["url"], "datePublished":post["date_published"], "dateModified":post["date_modified"], "image":[BASE+post["image"]], "author":{"@type":"Organization","name":post["author"],"url":BASE+"/#about"}, "publisher":{"@type":"Organization","name":"Culinary Revolutionary","url":BASE+"/","logo":{"@type":"ImageObject","url":BASE+"/public/assets/logo-256.png"}}, "inLanguage":"en-US", "isPartOf":{"@id":BASE+"/blog/#blog"}},
        {"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":BASE+"/"},{"@type":"ListItem","position":2,"name":"Blog","item":BASE+"/blog/"},{"@type":"ListItem","position":3,"name":post["title"],"item":BASE+post["url"]}]}
    ]}
    directory = blog_dir / post["slug"]
    directory.mkdir(exist_ok=True)
    (directory / "index.html").write_text(page(post["seo_title"], post["description"], post["url"], body, schema, post["image"], post))

body = '<section class="section journal-intro"><div class="container"><p class="eyebrow">The Culinary Revolutionary journal</p><h1>Good food starts with a good plan.</h1><p class="article-lede">Private dining ideas, menu inspiration and practical hosting guides for life on South Florida’s Gulf Coast.</p></div></section><section class="section journal-list" aria-label="Latest articles"><div class="container">' + ''.join(card(post) for post in posts) + '</div></section>'
schema = {"@context":"https://schema.org","@type":"Blog","@id":BASE+"/blog/#blog","url":BASE+"/blog/","name":"Culinary Revolutionary Blog","description":"Private dining ideas, menus and hosting guides for South Florida’s Gulf Coast.","blogPost":[{"@type":"BlogPosting","headline":post["title"],"url":BASE+post["url"],"datePublished":post["date_published"]} for post in posts]}
(blog_dir / "index.html").write_text(page("Private Chef & Hosting Blog | Culinary Revolutionary", "Explore private chef dinner planning, menu ideas and hosting tips from Culinary Revolutionary, serving South Florida’s Gulf Coast.", "/blog/", body, schema, posts[0]["image"]))
preview = '<!-- BLOG-PREVIEW:START -->\n    <section class="section alt" aria-labelledby="journal-heading"><div class="container"><p class="eyebrow">From the journal</p><h2 id="journal-heading">A little inspiration for your next gathering</h2><div class="home-journal">' + card(posts[0]).replace('<h2>', '<h3>').replace('</h2>', '</h3>') + '</div><p><a class="text-link" href="/blog/">Browse all planning guides →</a></p></div></section>\n    <!-- BLOG-PREVIEW:END -->'
home, count = re.subn(r'<!-- BLOG-PREVIEW:START -->.*?<!-- BLOG-PREVIEW:END -->', lambda _: preview, home, flags=re.S)
if count != 1:
    raise ValueError("Homepage blog preview markers missing or duplicated")
(ROOT / "index.html").write_text(home)
lastmod = max(post["date_modified"] for post in posts)
# Update these dates only when the corresponding page changes meaningfully.
# A new blog post does not, by itself, change the menus page.
homepage_lastmod = max(lastmod, "2026-09-22")
urls = [("/",homepage_lastmod),("/menus.html","2026-09-10"),("/blog/",lastmod)] + [(post["url"],post["date_modified"]) for post in posts]
(ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{BASE}{e(url)}</loc><lastmod>{date}</lastmod></url>\n' for url,date in urls) + '</urlset>\n')
items = []
for post in posts:
    published = dt.datetime.fromisoformat(post["date_published"]).replace(tzinfo=dt.timezone.utc)
    items.append(f'<item><title>{e(post["title"])}</title><link>{BASE}{post["url"]}</link><guid isPermaLink="true">{BASE}{post["url"]}</guid><pubDate>{email.utils.format_datetime(published)}</pubDate><description>{e(post["excerpt"])}</description></item>')
(blog_dir / "feed.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>Culinary Revolutionary Blog</title><link>'+BASE+'/blog/</link><description>Private dining, menu inspiration and hosting guides.</description><language>en-us</language><atom:link href="'+BASE+'/blog/feed.xml" rel="self" type="application/rss+xml" />'+''.join(items)+'</channel></rss>\n')
print(f"Built blog index, {len(posts)} article(s), RSS, homepage preview and sitemap.")
