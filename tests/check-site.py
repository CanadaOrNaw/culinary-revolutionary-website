#!/usr/bin/env python3
"""Validate the shipped HTML links, metadata, sitemap and RSS without network calls."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self, content):
        super().__init__(); self.ids = set(); self.links = []; self.h1s = 0
        self.canonical = []; self.description = []; self.schemas = []; self.in_schema = False
        self.feed(content)
    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, f"Duplicate id {attrs['id']}"
            self.ids.add(attrs['id'])
        if tag == 'h1': self.h1s += 1
        for attr in ('href', 'src'):
            if attrs.get(attr): self.links.append(attrs[attr])
        if tag == 'link' and attrs.get('rel') == 'canonical': self.canonical.append(attrs['href'])
        if tag == 'meta' and attrs.get('name') == 'description': self.description.append(attrs['content'])
        if tag == 'script' and attrs.get('type') == 'application/ld+json': self.in_schema = True
    def handle_endtag(self, tag):
        if tag == 'script': self.in_schema = False
    def handle_data(self, value):
        if self.in_schema: self.schemas.append(json.loads(value))

files = [ROOT/name for name in ('index.html', 'menus.html', 'thank-you.html')] + list((ROOT/'blog').rglob('*.html'))
pages = {path: Page(path.read_text()) for path in files}
checks = 0
for path, page in pages.items():
    assert page.h1s == 1, f"Expected one H1: {path}"
    assert len(page.description) == 1 and page.description[0], f"Missing description: {path}"
    if path.name != 'thank-you.html':
        assert len(page.canonical) == 1, f"Missing canonical: {path}"
    for link in page.links:
        parsed = urlsplit(link)
        if parsed.scheme or parsed.netloc: continue
        target = ((ROOT/parsed.path.lstrip('/')) if parsed.path.startswith('/') else (path.parent/parsed.path)) if parsed.path else path
        if target.is_dir(): target = target/'index.html'
        target = target.resolve()
        assert target.exists(), f"Broken link {link} in {path.relative_to(ROOT)}"
        if parsed.fragment and target in pages:
            assert unquote(parsed.fragment) in pages[target].ids, f"Broken anchor {link} in {path}"
        checks += 1
    if path.parent != ROOT and path.parent != ROOT/'blog':
        schema = page.schemas[0]['@graph'][0]
        assert schema['@type'] == 'BlogPosting'
        assert schema['url'] == page.canonical[0]
        assert schema['author']['name'] == 'Culinary Revolutionary'
        assert schema['dateModified'] >= schema['datePublished']
        assert '/#inquiry' in page.links
        assert '/menus.html' in page.links
        assert 'noindex' not in path.read_text()

# Keep the public service-area answers and factual business identity crawlable.
home_text = (ROOT/'index.html').read_text()
home_graph = pages[ROOT/'index.html'].schemas[0]['@graph']
by_type = {node['@type']: node for node in home_graph}
assert {'LocalBusiness', 'Person', 'WebSite'} <= by_type.keys(), 'Missing factual business schema'
assert by_type['WebSite']['publisher']['@id'] == by_type['LocalBusiness']['@id']
assert 'How do I check if you can cook at my location?' in home_text
assert 'Can you adapt a private dinner menu for different guests?' in home_text
assert 'South Florida' in home_text

sitemap = ET.parse(ROOT/'sitemap.xml')
locations = [x.text for x in sitemap.findall('.//{*}loc')]
assert len(locations) == len(set(locations))
for url in locations:
    target = ROOT / urlsplit(url).path.lstrip('/')
    if target.is_dir(): target /= 'index.html'
    assert target.exists(), f"Missing sitemap destination: {url}"
for path in files:
    if path.parent != ROOT: assert pages[path].canonical[0] in locations
rss = ET.parse(ROOT/'blog/feed.xml')
assert len(rss.findall('.//item')) == len(files)-4
print(f'PASS: {len(files)} pages, {checks} internal links, article metadata, {len(locations)} sitemap URLs and RSS.')
