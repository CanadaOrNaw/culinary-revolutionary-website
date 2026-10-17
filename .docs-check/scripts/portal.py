#!/usr/bin/env python3
"""Validate independently reviewed project manuals and stage only exact accepted inputs."""
import argparse
import fnmatch
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt
import yaml

KINDS = {"overview", "tutorial", "how-to", "concept", "developer", "reference", "status"}
GENERATED = {".git", ".venv", "node_modules", "_generated", ".generated", "build", "dist", "__pycache__"}
BLOCKED = GENERATED | {"private", "secrets", "runtime", "logs", "vendor"}
PRIVATE = re.compile(r"(^|[._/-])(secrets?|tokens?|passwords?|credentials?|private|\.env)([._/-]|$)", re.I)
SAFE_SOURCE_NAMES = {"_system/scripts/secret-scan.sh", ".env.example", "test_auto_git_commit_secret_guard.sh"}
EXECUTABLE = re.compile(r'(?im)^\s*(?:import\s+.+\s+from\s+[\'"]|export\s+|(?:!include|\{\{<|#include)\s+)|<\s*[A-Z][a-zA-Z0-9]*\b|<\s*(?:script|iframe|object|embed|link|img)\b|\bon\w+\s*=|\b(?:require\s*\(|import\s*\()')
SECRET_TEXT = re.compile(r"(?im)\b(?:password|secret|api[_-]?key|access[_-]?token)\s*[:=]\s*[^\s#]{5,}")


READER_ABSOLUTE = re.compile(r"(?<![A-Za-z0-9._-])/(?:home|Users|root|tmp|var|etc|opt|run|private)/[^\\\s\'\"<>`(),;:]*", re.I)
READER_CREDENTIAL_URL = re.compile(r"(?i)[a-z][a-z0-9+.-]*://[^\s\'\"<>/@]+:[^\s\'\"<>/@]+@")
READER_WINDOWS_MACHINE_PATH = re.compile(r"(?i)\b[A-Z]:\\(?:Users|Windows|Documents)\\")


def valid_public_reader_literal(value):
    if not isinstance(value, str) or not value.startswith("/") or value in ("/home", "/tmp", "/var", "/etc", "/opt", "/run", "/root", "/private", "/Users"):
        return False
    if any(c in value for c in "*?[\\#?\'\"<>` \t\r\n") or "//" in value:
        return False
    parts = PurePosixPath(value).parts
    if any(part in (".", "..") for part in parts) or len(parts) < 3:
        return False
    if any(part.startswith(".") or re.search(r"(?i)(^|[._-])(secrets?|tokens?|passwords?|credentials?|private)([._-]|$)", part) for part in parts):
        return False
    if value.startswith(("/home/zack", "/tmp/build", "/tmp/docs", "/tmp/portal")):
        return False
    return True


def _decoded_string_literals(text):
    # Decode string literals only; never evaluate JavaScript or transform source output.
    for match in re.finditer(r"\"((?:\\.|[^\"\\])*)\"|'((?:\\.|[^'\\])*)'", text):
        raw = match.group(1) if match.group(1) is not None else match.group(2)
        decoded = raw
        for _ in range(3):
            next_value = re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), decoded)
            next_value = re.sub(r"\\([\\/\"'])", r"\1", next_value)
            next_value = re.sub(r"\\([nrtbf])", lambda m: {"n":"\n","r":"\r","t":"\t","b":"\b","f":"\f"}[m.group(1)], next_value)
            if next_value == decoded: break
            decoded = next_value
        yield decoded


def _private_reader_scan(text, approved, *, secret_assignments=True):
    if (secret_assignments and SECRET_TEXT.search(text)) or re.search(r"(?i)file://", text) or READER_CREDENTIAL_URL.search(text) or READER_WINDOWS_MACHINE_PATH.search(text): return True
    return any(match.group() not in approved for match in READER_ABSOLUTE.finditer(text))


def private_reader_text(text, approved_literals=(), *, text_kind="plain"):
    if not isinstance(text, str) or text_kind not in ("plain", "js", "json"): return True
    if text_kind != "plain":
        from html import unescape
        text = unescape(text)
    approved = set(approved_literals)
    if any(not valid_public_reader_literal(value) for value in approved): return True
    raw_scan = text if text_kind == "plain" else re.sub(r"\\(?=[\'\"])", "", text)
    if _private_reader_scan(raw_scan, approved, secret_assignments=text_kind == "plain"): return True
    quoted_secret = r"(?i)\b(?:password|secret|api[_-]?key|access[_-]?token)[\'\"]?\s*[:=]\s*[\'\"]"
    if text_kind != "plain" and re.search(quoted_secret, raw_scan): return True
    if text_kind != "plain":
        for decoded in _decoded_string_literals(text):
            if re.search(quoted_secret, decoded) or _private_reader_scan(decoded, approved, secret_assignments=False): return True
    return False


class PortalError(ValueError):
    pass


def fail(message):
    raise PortalError(message)


def public_exception_allowed(path):
    parts = PurePosixPath(path).parts
    if not parts or any(part in BLOCKED or part.startswith(".") or PRIVATE.search(part) for part in parts[:-1]): return False
    name = parts[-1]
    return not name.startswith(".") and not re.search(r"(^|[._-])(secrets?|tokens?|passwords?|credentials?|\.env)([._-]|$)", name, re.I)


def allowed_source(value, public_sources=()):
    path = value.split("#", 1)[0]
    return not PRIVATE.search(value) or path in SAFE_SOURCE_NAMES or (path in public_sources and public_exception_allowed(path))


def shipped_dist_file(path):
    parts = PurePosixPath(path).parts
    return "dist" in parts and not path.endswith("/") and all(part not in BLOCKED - {"dist"} for part in parts)


def permitted_declaration(path):
    parts = PurePosixPath(path).parts
    if any(part in BLOCKED - {"dist"} for part in parts): return False
    return "dist" not in parts or shipped_dist_file(path)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(safe_bytes(path).decode("utf-8"))


def validate_shape(value, schema, root_schema, label="input"):
    if "$ref" in schema:
        schema = root_schema["$defs"][schema["$ref"].split("/")[-1]]
    kind = schema.get("type")
    valid = {"object": lambda v:isinstance(v,dict), "array":lambda v:isinstance(v,list), "string":lambda v:isinstance(v,str), "integer":lambda v:type(v) is int}
    if kind in valid and not valid[kind](value): fail(f"{label} must be {kind}")
    if "const" in schema and value != schema["const"]: fail(f"invalid {label}")
    if "enum" in schema and value not in schema["enum"]: fail(f"invalid {label}")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0) or (schema.get("pattern") and not re.fullmatch(schema["pattern"], value)):
            fail(f"invalid {label}")
    if isinstance(value, dict):
        for field in schema.get("required", []):
            if field not in value: fail(f"missing {label}.{field}")
        if schema.get("additionalProperties") is False and set(value) - set(schema.get("properties", {})):
            fail(f"unsupported {label} fields")
        for field, member in value.items():
            member_schema = schema.get("properties", {}).get(field, schema.get("additionalProperties"))
            if isinstance(member_schema, dict): validate_shape(member, member_schema, root_schema, label + "." + field)
    if isinstance(value, list) and "items" in schema:
        for i,member in enumerate(value): validate_shape(member,schema["items"],root_schema,f"{label}[{i}]")


def contract_schema(name):
    return load(Path(__file__).resolve().parents[1] / "schemas" / (name + ".schema.json"))


def require_evidence(value, label="review"):
    if isinstance(value, dict):
        for field, item in value.items():
            require_evidence(item, label + "." + field)
    elif isinstance(value, list):
        for i, item in enumerate(value): require_evidence(item, f"{label}[{i}]")
    elif isinstance(value, str) and not value.strip():
        if not label.endswith(("no_doc_impact", "findings", "resolutions", "limits")):
            fail(f"empty {label}")


def relpath(value, directory=False, excluded=False, public_sources=()):
    if not isinstance(value, str) or not value or "\\" in value or value.startswith("/") or "\x00" in value:
        fail(f"unsafe relative path: {value!r}")
    parts = PurePosixPath(value).parts
    if any(p in (".", "..", "") for p in parts) or value.startswith("./") or (value.endswith("/") != directory):
        fail(f"unsafe relative path: {value!r}")
    if not excluded and not allowed_source(value, public_sources):
        fail(f"private path cannot be included: {value}")
    return value


def confined(root, relative):
    path = root / relative
    if not path.resolve().is_relative_to(root.resolve()):
        fail(f"path escapes root: {relative}")
    current = root
    for part in PurePosixPath(relative).parts:
        current = current / part
        if current.is_symlink():
            fail(f"symlink input: {relative}")
    return path


def safe_bytes(path):
    if path.is_symlink() or not path.is_file():
        fail(f"missing or symlink input: {path}")
    return path.read_bytes()


def registry_data(registry, *, validate_paths=True):
    data = load(Path(registry))
    if data.get("schema") != 1 or not isinstance(data.get("workspaces"), list):
        fail("invalid registry")
    keys, roots = set(), set()
    for record in data["workspaces"]:
        root = Path(record["root"])
        if root in roots: fail(f"duplicate root: {root}")
        roots.add(root)
        site = record.get("site")
        if site:
            key = site.get("key")
            if not isinstance(key, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", key) or key in keys:
                fail(f"invalid or duplicate key: {key}")
            keys.add(key)
            for field in ("source", "verification"):
                relpath(site[field])
            relpath(site["navigation"])
            if validate_paths:
                confined(root, site["source"])
                confined(root, site["verification"])
            readers = site.get("public_reader_paths", {})
            if not isinstance(readers, dict) or any(not valid_public_reader_literal(path) or not isinstance(reason, str) or not reason.strip() for path,reason in readers.items()):
                fail("invalid public reader path policy")
            public = site.get("public_source_paths", {})
            if not isinstance(public, dict): fail("public source policy must be exact path map")
            for relative, reason in public.items():
                relpath(relative, public_sources=public)
                if not isinstance(reason, str) or not reason.strip() or relative.endswith("/") or any(c in relative for c in "*?[") or not public_exception_allowed(relative):
                    fail(f"invalid public source exception: {relative}")
                if validate_paths:
                    path = confined(root, relative)
                    if not path.is_file() or path.is_symlink(): fail(f"public source exception must be regular file: {relative}")
    return data


def projects(registry):
    return registry_data(registry)["workspaces"]


def project(registry, key):
    matches = [r for r in registry_data(registry, validate_paths=False)["workspaces"] if r.get("site", {}).get("key") == key]
    if not matches: fail(f"unknown project: {key}")
    return matches[0]


def excluded_path(path, patterns):
    return any(fnmatch.fnmatchcase(path, p + "*") if p.endswith("/") else fnmatch.fnmatchcase(path, p) for p in patterns)


def declared_files(root, prefix, excluded=(), public_sources=()):
    base = confined(root, prefix)
    if not base.is_dir(): fail(f"missing directory: {prefix}")
    for directory, dirs, files in os.walk(base, followlinks=False):
        here = Path(directory)
        dirs[:] = sorted(d for d in dirs if d not in BLOCKED and not PRIVATE.search(d) and not (here / d).is_symlink() and not excluded_path((here / d).relative_to(root).as_posix() + "/", excluded))
        for name in sorted(files):
            path = here / name
            relative = path.relative_to(root).as_posix()
            if not allowed_source(relative, public_sources) or excluded_path(relative, excluded):
                continue
            if path.is_symlink(): fail(f"symlink input: {relative}")
            yield relative, path


def source_inventory(root, record, manifest, nested):
    declarations = manifest["sources"]
    public_sources = record["site"].get("public_source_paths", {})
    excluded = [relpath(e["path"], e["path"].endswith("/"), excluded=True) for e in manifest["excluded"]]
    for e in manifest["excluded"]:
        if not e.get("reason"): fail("exclusion requires reason")
    def skip(path):
        return excluded_path(path, excluded + nested)
    result = {}
    for entry in declarations:
        p = relpath(entry["path"], entry["path"].endswith("/"), public_sources=public_sources)
        if not entry.get("role") or skip(p) or not permitted_declaration(p): fail(f"invalid source declaration: {p}")
        candidates = declared_files(root, p, excluded + nested, public_sources) if p.endswith("/") else [(p, confined(root, p))]
        count = 0
        for relative, path in candidates:
            if skip(relative) or not allowed_source(relative, public_sources): fail(f"private source: {relative}")
            if relative in result: fail(f"duplicate source: {relative}")
            result[relative] = sha(safe_bytes(path)); count += 1
        if not count: fail(f"empty source declaration: {p}")
    declared_dist = {PurePosixPath(path).parts[:i+1] for path in result for i, part in enumerate(PurePosixPath(path).parts) if part == "dist"}
    # Directory names are inspected before descent; excluded/private bytes are never opened.
    source_parents = {PurePosixPath(path).parts[:i] for path in result for i in range(1, len(PurePosixPath(path).parts))}
    classified_parents = source_parents | {PurePosixPath(path).parts[:i] for path in excluded for i in range(1, len(PurePosixPath(path).parts))}
    source_directories = [entry["path"] for entry in declarations if entry["path"].endswith("/")]
    documentation_roots = (record["site"]["source"].rstrip("/") + "/", record["site"]["verification"].rstrip("/") + "/")
    def walk_error(error):
        fail(f"source directory unreadable: {error.filename}")
    for directory, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
        here = Path(directory)
        descend = []
        for name in sorted(dirs):
            path = here / name
            relative = path.relative_to(root).as_posix() + "/"
            if skip(relative) or not allowed_source(relative, public_sources) or (name in GENERATED and (name != "dist" or PurePosixPath(relative).parts not in declared_dist)): continue
            if path.is_symlink(): fail(f"unclassified source symlink: {relative}")
            if name in BLOCKED and (name != "dist" or PurePosixPath(relative).parts not in declared_dist): fail(f"unclassified source boundary: {relative}; declare an exclusion")
            if relative in documentation_roots:
                continue
            if (PurePosixPath(relative).parts not in classified_parents
                    and not any(relative.startswith(prefix) for prefix in source_directories)
                    and not any(prefix.startswith(relative) for prefix in documentation_roots)):
                fail(f"unclassified source directory: {relative}; declare an exclusion")
            descend.append(name)
        dirs[:] = descend
        for name in files:
            path = here / name
            relative = path.relative_to(root).as_posix()
            if skip(relative) or not allowed_source(relative, public_sources): continue
            if path.is_symlink(): fail(f"symlink source: {relative}")
            if relative.startswith((record["site"]["source"] + "/", record["site"]["verification"] + "/")): continue
            if relative not in result: fail(f"unclassified source: {relative}")
    return dict(sorted(result.items()))


def sidebar_ids(items):
    ids = []
    for item in items:
        if isinstance(item, str): ids.append(item)
        elif isinstance(item, dict):
            if item.get("type") == "category" and item.get("label") and isinstance(item.get("items"), list): ids += sidebar_ids(item["items"])
            elif item.get("type") == "doc": ids.append(item["id"])
            elif item.get("type") == "link" and item.get("label") and item.get("href", "").startswith("/projects/"): pass
            else: fail("invalid sidebar item")
        else: fail("invalid sidebar item")
    return ids


def validate_sidebar(items, key, pages, docs, project_pages, cross_docs=None, approved_literals=()):
    for item in items:
        if isinstance(item, str): continue
        if item["type"] == "link":
            validate_target(item["href"], key, "index.md", docs, project_pages, cross_docs=cross_docs, approved_literals=approved_literals)
        elif item["type"] == "category":
            link = item.get("link")
            if link:
                if link.get("type") == "doc" and link.get("id") not in pages: fail("category doc target missing")
                elif link.get("type") == "link": validate_target(link["href"], key, "index.md", docs, project_pages, cross_docs=cross_docs, approved_literals=approved_literals)
                elif link.get("type") != "doc": fail("invalid category link")
            validate_sidebar(item["items"], key, pages, docs, project_pages, cross_docs=cross_docs, approved_literals=approved_literals)


def prefixed(items, key):
    result = []
    for item in items:
        if isinstance(item, str): result.append(key + "/" + item)
        elif item["type"] == "doc": result.append({**item, "id": key + "/" + item["id"]})
        elif item["type"] == "category":
            category = {**item, "items": prefixed(item["items"], key)}
            if category.get("link", {}).get("type") == "doc":
                category["link"] = {**category["link"], "id": key + "/" + category["link"]["id"]}
            result.append(category)
        else: result.append(item)
    return result


def frontmatter(text, staged=False, approved_literals=()):
    match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not match: fail("page needs YAML frontmatter")
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict) or not all(isinstance(data.get(k), str) and data[k] for k in ("title", "description", "kind")) or data["kind"] not in KINDS:
        fail("invalid page metadata")
    if "format" in data or (not staged and ("id" in data or "slug" in data)): fail("Markdown format/IDs are adapter owned")
    if private_reader_text(str(data), approved_literals): fail("private page metadata")
    for value in data.values():
        if isinstance(value, str):
            for url in re.findall(r"https?://[^\s<>\'\"]+", value):
                parsed = urlsplit(url)
                if parsed.username or parsed.password: fail("credential URL in metadata")
    return data, text[match.end():]


def markdown_tokens(text, staged=False, approved_literals=()):
    _, body = frontmatter(text, staged=staged, approved_literals=approved_literals)
    tokens = MarkdownIt("commonmark", {"html": True}).parse(body)
    for token in tokens:
        if token.type == "html_block": fail("raw HTML/JSX is not reader Markdown")
        if token.type == "inline":
            for child in token.children or []:
                if child.type == "html_inline": fail("raw HTML/JSX is not reader Markdown")
                if child.type == "text" and (re.search(r"\{[^{}]*[.$()[\]]+[^{}]*\}", child.content) or EXECUTABLE.search(child.content)):
                    fail("executable Markdown expression/import")
    return tokens


def heading_slugs(text, staged=False, approved_literals=()):
    tokens = markdown_tokens(text, staged=staged, approved_literals=approved_literals)
    seen = {}; result = set()
    for index, token in enumerate(tokens[:-1]):
        if token.type != "heading_open": continue
        content = tokens[index + 1].content
        explicit = re.search(r"\s*\{#([^}]+)\}\s*$", content)
        if explicit: content = content[:explicit.start()]
        base = re.sub(r"[^a-z0-9 _-]", "", content.lower()).strip().replace(" ", "-")
        slug = explicit.group(1) if explicit else base
        count = seen.get(slug, 0); seen[slug] = count + 1
        result.add(slug if not count else f"{slug}-{count}")
    return result


def validate_target(value, key, relative, docs, project_pages, staged=False, cross_docs=None, approved_literals=()):
    value = unquote(value)
    url = urlsplit(value)
    if url.scheme in ("http", "https", "mailto"):
        if url.username or url.password: fail(f"credential-bearing URL: {value}")
        return
    if url.scheme or value.startswith("//"): fail(f"unsafe link: {value}")
    if url.path.startswith("/projects/"):
        suffix = url.path.removeprefix("/projects/")
        route, _, rest = suffix.partition("/")
        if route not in project_pages: fail(f"unresolved project link: {value}")
        name = rest.strip("/") or "index"
        if name not in project_pages[route]: fail(f"unresolved project page: {value}")
        if url.fragment:
            target = name + ".md"
            if route == key:
                target_text = docs[target]
            else:
                target_text = (cross_docs or {}).get(route, {}).get(target)
            if target_text is None or url.fragment not in heading_slugs(target_text, staged=staged, approved_literals=approved_literals): fail(f"unresolved anchor: {value}")
        return
    if url.path.startswith("/"): fail(f"unsafe absolute link: {value}")
    target = os.path.normpath((PurePosixPath(relative).parent / url.path).as_posix() if url.path else relative)
    if target.startswith("../") or target == "..": fail(f"escaped link: {value}")
    if target not in docs:
        if target + ".md" in docs: target += ".md"
        else: fail(f"unresolved link: {value}")
    if url.fragment and target.endswith(".md") and url.fragment not in heading_slugs(docs[target], staged=staged, approved_literals=approved_literals):
        fail(f"unresolved anchor: {value}")


def cross_link_targets(docs, sidebar, approved_literals=()):
    urls = []
    for name,text in docs.items():
        if not name.endswith(".md"): continue
        for token in markdown_tokens(text, approved_literals=approved_literals):
            if token.type != "inline": continue
            for child in token.children or []:
                if child.type == "link_open": urls.append(child.attrGet("href"))
    def walk(items):
        for item in items:
            if not isinstance(item, dict): continue
            if item.get("type") == "link": urls.append(item["href"])
            if item.get("type") == "category":
                link = item.get("link", {})
                if link.get("type") == "link": urls.append(link["href"])
                walk(item["items"])
    walk(sidebar)
    for value in urls:
        if not value: continue
        parsed = urlsplit(unquote(value))
        if not parsed.path.startswith("/projects/"): continue
        key, _, rest = parsed.path.removeprefix("/projects/").partition("/")
        yield key, (rest.strip("/") or "index") + ".md"


def allowed_cross_docs(registry, docs, sidebar, project_pages, own_key, approved_literals=()):
    result = {}
    for key, page in cross_link_targets(docs, sidebar, approved_literals=approved_literals):
        if key == own_key: continue
        id_ = page[:-3]
        if id_ not in project_pages.get(key, set()): fail(f"unresolved project page: {key}/{id_}")
        other = project(registry, key)
        root = Path(other["root"]); source = other["site"]["source"]
        relative = source + "/" + page
        manifest_path = confined(root, other["site"]["verification"] + "/manifest.json")
        if not manifest_path.is_file(): fail(f"cross-project manifest missing: {key}")
        excluded = [e["path"] for e in load(manifest_path).get("excluded", [])]
        if not allowed_source(relative) or excluded_path(relative, excluded): fail(f"denied project page: {key}/{page}")
        result.setdefault(key, {})[page] = safe_bytes(confined(root, relative)).decode("utf-8")
    return result


def validate_links(key, pages, docs, project_pages, staged=False, cross_docs=None, approved_literals=()):
    for relative, text in docs.items():
        if not relative.endswith(".md"): continue
        tokens = markdown_tokens(text, staged=staged, approved_literals=approved_literals)
        for token in tokens:
            if token.type != "inline": continue
            for child in token.children or []:
                if child.type in ("link_open", "image"):
                    validate_target(child.attrGet("href") if child.type == "link_open" else child.attrGet("src"), key, relative, docs, project_pages, staged=staged, cross_docs=cross_docs, approved_literals=approved_literals)
                elif child.type == "text" and re.search(r"\[[^]]+\]\[[^]]+\]", child.content):
                    fail(f"unresolved reference link: {relative}")


def collect(registry, key):
    record = project(registry, key); site = record["site"]; root = Path(record["root"])
    source = site["source"]; verification = site["verification"]
    manifest_path = confined(root, verification + "/manifest.json")
    manifest = load(manifest_path)
    required = ("author", "sources", "excluded", "pages", "interfaces", "examples", "tasks", "not_applicable")
    validate_shape(manifest, contract_schema("manifest"), contract_schema("manifest"), "manifest")
    if manifest.get("project") != key: fail("invalid manifest project")
    nested = [Path(r["root"]).relative_to(root).as_posix() + "/" for r in registry_data(registry, validate_paths=False)["workspaces"] if Path(r["root"]) != root and Path(r["root"]).is_relative_to(root)]
    source_hashes = source_inventory(root, record, manifest, nested)
    docs = {}; doc_hashes = {}
    handbook_excluded = [e["path"] for e in manifest["excluded"] if e["path"].startswith(source + "/")]
    for relative, path in declared_files(root, source, handbook_excluded):
        name = relative.removeprefix(source + "/")
        if name.endswith((".html", ".pdf", ".mdx", ".js", ".jsx", ".ts", ".tsx")): fail(f"unsafe handbook input: {name}")
        if name.endswith(".md") or name == site["navigation"] or name.endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")):
            data = safe_bytes(path)
            if name.endswith(".svg"):
                svg = data.decode("utf-8")
                if re.search(r"(?is)<\s*(?:script|foreignObject|iframe|object|embed)\b|\bon\w+\s*=|(?:javascript|data):", svg): fail(f"unsafe SVG: {name}")
            docs[name] = data.decode("utf-8") if name.endswith((".md", ".json")) else data
            doc_hashes[name] = sha(data)
        else: fail(f"unapproved handbook input: {name}")
    sidebar = json.loads(docs[site["navigation"]]); ids = sidebar_ids(sidebar)
    pages = {name[:-3]: name for name in docs if name.endswith(".md")}
    if len(ids) != len(set(ids)) or set(ids) != set(pages) or "index" not in ids: fail("invalid or unreachable navigation")
    entries = {p["id"]: p for p in manifest["pages"]}
    if len(entries) != len(manifest["pages"]) or set(entries) != set(pages): fail("manifest page coverage mismatch")
    for id_, name in pages.items():
        data, body = frontmatter(docs[name], approved_literals=site.get("public_reader_paths", {}))
        if private_reader_text(docs[name], site.get("public_reader_paths", {})): fail(f"private page content: {name}")
        markdown_tokens(docs[name], approved_literals=site.get("public_reader_paths", {}))
        entry = entries[id_]
        if entry["kind"] != data["kind"]: fail(f"page kind mismatch: {id_}")
        refs = data.get("source_ref", [])
        if isinstance(refs, str): refs = [refs]
        for source_ref in refs:
            ref = source_ref.split("#", 1)[0]
            if ref not in source_hashes or not allowed_source(source_ref, site.get("public_source_paths", {})): fail(f"invalid source_ref: {source_ref}")
        claimed = entry.get("sources", [])
        if any(path not in source_hashes for path in claimed) or (claimed and not refs) or (refs and set(ref.split("#",1)[0] for ref in refs) != set(claimed)):
            fail(f"page source mapping mismatch: {id_}")
    for interface in manifest["interfaces"]:
        if interface["source"] not in source_hashes or not interface.get("claims") or not interface.get("docs"):
            fail("uncovered interface")
        for doc in interface["docs"]:
            id_, _, anchor = doc.partition("#")
            if id_ not in pages or (anchor and anchor not in heading_slugs(docs[pages[id_]], approved_literals=site.get("public_reader_paths", {}))):
                fail(f"interface docs/anchor missing: {doc}")
    for item in manifest["examples"]:
        if item["page"] not in pages or not item.get("command") or any("<" in str(x) or "TODO" in str(x) for x in item["command"]): fail("invalid example")
    for task in manifest["tasks"]:
        if task["start"] not in pages or any(p not in pages for p in task["pages"]): fail("invalid task")
    route_pages = {}
    cross_docs = {}
    linked_projects = {key, *(target for target, _ in cross_link_targets(docs, sidebar, approved_literals=site.get("public_reader_paths", {})))}
    for other in registry_data(registry, validate_paths=False)["workspaces"]:
        if not other.get("site") or other["site"]["key"] not in linked_projects: continue
        other_site = other["site"]
        handbook = confined(Path(other["root"]), other_site["source"])
        route_pages[other_site["key"]] = {relative.removeprefix(other_site["source"] + "/")[:-3] for relative, _ in declared_files(Path(other["root"]), other_site["source"]) if relative.endswith(".md")} if handbook.is_dir() else set()
        cross_docs[other_site["key"]] = {}
    cross_docs = allowed_cross_docs(registry, docs, sidebar, route_pages, key, approved_literals=site.get("public_reader_paths", {}))
    validate_links(key, pages, docs, route_pages, cross_docs=cross_docs, approved_literals=site.get("public_reader_paths", {}))
    validate_sidebar(sidebar, key, pages, docs, route_pages, cross_docs=cross_docs, approved_literals=site.get("public_reader_paths", {}))
    snapshot = {"source_hashes":source_hashes,"doc_hashes":dict(sorted(doc_hashes.items())),"manifest_hash":sha(safe_bytes(manifest_path))}
    return record, manifest, docs, sidebar, snapshot


def snapshot(registry, key):
    return collect(registry, key)[-1]


def accepted(registry, key, current=None):
    record, manifest, docs, sidebar, actual = current or collect(registry, key)
    review = confined(Path(record["root"]), record["site"]["verification"] + "/review.json")
    if not review.exists(): return False, "review missing"
    receipt = load(review)
    fields = ("schema", "project", "reviewed_at", "snapshot", "impact", "checks", "claim_review", "task_trials", "limits", "decision")
    if not isinstance(receipt, dict) or receipt.get("schema") != 1 or receipt.get("project") != key or receipt.get("decision") not in ("accepted", "changes-required"): fail("invalid review header")
    if receipt["decision"] != "accepted": return False, "review changes-required"
    schema = contract_schema("review")
    validate_shape(receipt, schema, schema, "review")
    require_evidence({"checks": receipt["checks"], "claim_review":receipt["claim_review"], "task_trials":receipt["task_trials"]})
    reviewed = {field: receipt["snapshot"].get(field) for field in actual}
    if reviewed != actual: return False, "accepted snapshot stale"
    for target, _ in set(cross_link_targets(docs, sidebar, approved_literals=record["site"].get("public_reader_paths", {}))):
        if target == key: continue
        other = project(registry, target)
        path = confined(Path(other["root"]), other["site"]["verification"] + "/review.json")
        if not path.exists(): return False, f"cross-project target pending: {target}"
        other_review = load(path)
        try: other_snapshot = snapshot(registry, target)
        except (PortalError, ValueError, KeyError, TypeError): return False, f"cross-project target invalid: {target}"
        if other_review.get("decision") != "accepted" or {field:other_review.get("snapshot",{}).get(field) for field in other_snapshot} != other_snapshot:
            return False, f"cross-project target pending: {target}"
    impact_evidence = receipt["impact"]
    if not isinstance(impact_evidence, dict) or not isinstance(impact_evidence.get("base"), str) or any(field not in impact_evidence for field in ("changed_paths", "affected_pages", "affected_interfaces", "no_doc_impact")) or any(not isinstance(impact_evidence[field], list) for field in ("changed_paths", "affected_pages", "affected_interfaces", "no_doc_impact")):
        fail("impact evidence missing")
    claims = receipt["claim_review"]
    if not isinstance(claims, dict) or not claims.get("reviewer") or claims["reviewer"] == manifest["author"] or not claims.get("source_observations") or not claims.get("test_observations") or any(field not in claims or not isinstance(claims[field], list) for field in ("changed_claims", "findings", "resolutions")) or not isinstance(receipt["checks"], list) or not receipt["checks"] or not isinstance(receipt["task_trials"], list) or not receipt["task_trials"]:
        fail("independent review evidence missing")
    for check_item in receipt["checks"]:
        if not isinstance(check_item, dict) or any(field not in check_item for field in ("command", "environment", "effects", "exit", "outcome", "evidence")) or not isinstance(check_item["exit"], int) or (check_item["exit"] != 0 and check_item["outcome"].strip().lower() in ("pass", "passed", "success")): fail("check evidence missing or contradicts exit")
    for trial in receipt["task_trials"]:
        if not isinstance(trial, dict) or any(not trial.get(field) for field in ("reader", "task", "starting_state", "observed_result", "author_assistance")) or trial["reader"] == manifest["author"] or trial["task"] not in {t["id"] for t in manifest["tasks"]}: fail("task trial evidence missing or unmapped")
    return True, "accepted"


def check(registry, key=None):
    records = projects(registry); states = {}
    for record in records:
        site = record.get("site")
        if key and (not site or site["key"] != key): continue
        if not site: continue
        k = site["key"]
        manifest = confined(Path(record["root"]), site["verification"] + "/manifest.json")
        if not manifest.exists():
            review = confined(Path(record["root"]),site["verification"] + "/review.json")
            states[k] = {"state":"invalid" if review.exists() and load(review).get("decision") == "accepted" else "pending", "reason":"manifest missing" if review.exists() else "manifest not authored"}
            continue
        try:
            current = collect(registry, k)
            yes, reason = accepted(registry, k, current)
            states[k] = {"state":"admitted" if yes else "pending", "reason":reason}
        except (PortalError, ValueError, KeyError, TypeError, UnicodeDecodeError) as exc:
            states[k] = {"state":"invalid", "reason":str(exc)}
    if key and key not in states: fail(f"unknown project: {key}")
    return {"schema":1,"projects":states}


def prepare(registry, output):
    registry_hash = sha(safe_bytes(Path(registry)))
    records = projects(registry); states = check(registry)["projects"]
    for record in records:
        site = record.get("site")
        if not site or states[site["key"]]["state"] == "admitted": continue
        review = confined(Path(record["root"]), site["verification"] + "/review.json")
        if review.exists() and load(review).get("decision") == "accepted":
            fail(f"non-admitted accepted project inputs: {site['key']}: {states[site['key']]['reason']}")
    admitted = sorted(k for k,v in states.items() if v["state"] == "admitted")
    bundles = {key:collect(registry, key) for key in admitted}
    review_hashes = {key:sha(safe_bytes(confined(Path(bundle[0]["root"]),bundle[0]["site"]["verification"]+"/review.json"))) for key,bundle in bundles.items()}
    for key,bundle in bundles.items():
        if not accepted(registry, key, bundle)[0]: fail(f"stale accepted review: {key}")
    target = Path(output).absolute()
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="portal-", dir=target.parent))
    try:
        sidebars = {}; metadata = []; receipt = {"schema":1,"registry_hash":registry_hash,"projects":{}}
        for record in records:
            site = record.get("site"); key = site["key"] if site else record["id"]
            state = states[key]["state"] if site else "reference/archive"
            reason = states[key]["reason"] if site else record.get("reason", "Not an owned manual")
            meta = {"key":key,"title":site["title"] if site else record["title"],"route":f"/projects/{key}/" if state=="admitted" else None,"state":state,"reason":reason,"owner":site.get("owner", "") if site else record.get("owner", ""),"sourceLabel":site["source"] if site else record.get("kind", "reference"),"reviewedAt":load(confined(Path(record["root"]),site["verification"]+"/review.json"))["reviewed_at"] if state=="admitted" else None,"overview":f"/projects/{key}/" if state=="admitted" else None,"collaborationRoute":f"/projects/{key}/" if state=="admitted" else None,"reviewDecision":"accepted" if state=="admitted" else "changes-required"}
            if state == "admitted": meta["publicReaderPaths"] = sorted(site.get("public_reader_paths", {}))
            metadata.append(meta)
            if state != "admitted": continue
            _, _, docs, sidebar, snap = bundles[key]
            receipt["projects"][key] = {"snapshot":snap,"site_hash":sha(json.dumps(site, sort_keys=True).encode()),"review_hash":review_hashes[key],"contract_schema":1,"staged_hashes":{}}
            sidebars[key] = prefixed(sidebar, key)
            for name,data in docs.items():
                if name == site["navigation"]: continue
                original = confined(Path(record["root"]),site["source"]+"/"+name)
                if sha(safe_bytes(original)) != snap["doc_hashes"][name]: fail(f"input mutated: {key}/{name}")
                if name.endswith(".md"):
                    id_ = name[:-3]
                    lines = data.split("---", 2)
                    slug = f"/{key}/" if id_ == "index" else f"/{key}/{id_}/"
                    data = ("---" + lines[1] + f"slug: {slug}\n---" + lines[2]).encode()
                staged = tmp / "docs" / key / name; staged.parent.mkdir(parents=True, exist_ok=True); staged.write_bytes(data)
                receipt["projects"][key]["staged_hashes"][name] = sha(data)
            for relative, expected in snap["source_hashes"].items():
                if sha(safe_bytes(confined(Path(record["root"]), relative))) != expected: fail(f"source mutated: {key}/{relative}")
            if sha(safe_bytes(confined(Path(record["root"]),site["verification"]+"/manifest.json"))) != snap["manifest_hash"]: fail("manifest mutated")
        for name,obj in (("sidebars.json",sidebars),("projects.json",{"schema":1,"projects":metadata})):
            (tmp/name).write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
        receipt["metadata_hashes"] = {name:sha(safe_bytes(tmp/name)) for name in ("projects.json", "sidebars.json")}
        (tmp/"input-receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
        # A copied snapshot is not trusted until each staged asset and transformed Markdown is checked.
        if sha(safe_bytes(Path(registry))) != receipt["registry_hash"]: fail("registry mutated")
        for key,bundle in bundles.items():
            site = bundle[0]["site"]
            owner_root = Path(bundle[0]["root"])
            if sha(safe_bytes(confined(owner_root, site["verification"] + "/review.json"))) != review_hashes[key]: fail("accepted review mutated")
            for name, expected in bundle[-1]["doc_hashes"].items():
                if sha(safe_bytes(confined(owner_root, site["source"] + "/" + name))) != expected: fail(f"accepted input mutated: {key}/{name}")
            if sha(safe_bytes(confined(owner_root, site["verification"] + "/manifest.json"))) != bundle[-1]["manifest_hash"]: fail("manifest mutated")
            for name, expected in bundle[-1]["source_hashes"].items():
                if sha(safe_bytes(confined(owner_root, name))) != expected: fail(f"source mutated: {key}/{name}")
            for name,data in bundle[2].items():
                if name == site["navigation"]: continue
                staged = safe_bytes(tmp/"docs"/key/name)
                if name.endswith(".md"):
                    expected_body = frontmatter(data, approved_literals=site.get("public_reader_paths", {}))[1]
                    if staged.decode().split("---", 2)[2] != "\n" + expected_body: fail("staged page mismatch")
                elif sha(staged) != bundle[-1]["doc_hashes"][name]: fail("staged asset mismatch")
        if target.is_symlink(): fail("output symlink")
        old = target.with_name(target.name + ".previous")
        if old.exists(): fail(f"previous output exists: {old}")
        if target.exists(): target.rename(old)
        try: tmp.rename(target)
        except BaseException:
            if old.exists(): old.rename(target)
            raise
        if old.exists(): shutil.rmtree(old)
        return {"admitted":admitted,"output":str(target)}
    finally:
        if tmp.exists(): shutil.rmtree(tmp)


def impact(registry, key):
    record = project(registry, key); root = Path(record["root"]); site = record["site"]
    manifest = load(confined(root, site["verification"] + "/manifest.json"))
    public_sources = site.get("public_source_paths", {})
    nested = [Path(r["root"]).relative_to(root).as_posix() + "/" for r in projects(registry) if Path(r["root"]) != root and Path(r["root"]).is_relative_to(root)]
    exclusions = [e["path"] for e in manifest["excluded"]] + nested
    review = confined(root, site["verification"] + "/review.json")
    before = load(review).get("snapshot", {}) if review.exists() else {}
    old_sources = before.get("source_hashes", {})
    current_sources = {}
    missing = []
    unclassified = []
    for entry in manifest["sources"]:
        path = entry["path"]
        try: relpath(path, path.endswith("/"), public_sources=public_sources)
        except PortalError:
            unclassified.append(path); continue
        if excluded_path(path, exclusions) or not allowed_source(path, public_sources) or not permitted_declaration(path):
            unclassified.append(path); continue
        if path.endswith("/"):
            for relative, file in declared_files(root, path, exclusions, public_sources):
                current_sources[relative] = sha(safe_bytes(file))
        else:
            file = confined(root, path)
            if file.is_file(): current_sources[path] = sha(safe_bytes(file))
            else: missing.append(path)
    declared_dist = {PurePosixPath(path).parts[:i+1] for path in current_sources for i,part in enumerate(PurePosixPath(path).parts) if part == "dist"}
    for directory, dirs, files in os.walk(root, followlinks=False):
        here = Path(directory); descent = []
        for name in sorted(dirs):
            relative = (here / name).relative_to(root).as_posix() + "/"
            if excluded_path(relative, exclusions) or not allowed_source(relative, public_sources) or (name in GENERATED and (name != "dist" or PurePosixPath(relative).parts not in declared_dist)): continue
            if (here / name).is_symlink() or name in BLOCKED and (name != "dist" or PurePosixPath(relative).parts not in declared_dist): unclassified.append(relative)
            else: descent.append(name)
        dirs[:] = descent
        for name in files:
            relative = (here / name).relative_to(root).as_posix()
            if excluded_path(relative, exclusions) or not allowed_source(relative, public_sources) or relative.startswith((site["source"] + "/", site["verification"] + "/")): continue
            if relative not in current_sources: unclassified.append(relative)
    try:
        current = snapshot(registry, key)
        changed_docs = [p for p in sorted(set(before.get("doc_hashes", {})) | set(current["doc_hashes"])) if before.get("doc_hashes", {}).get(p) != current["doc_hashes"].get(p)]
        if before.get("manifest_hash") != current["manifest_hash"]: changed_docs.append("manifest.json")
    except (PortalError, KeyError, ValueError):
        changed_docs = []
    changed = sorted(set(unclassified + missing + changed_docs + [p for p in set(old_sources) | set(current_sources) if old_sources.get(p) != current_sources.get(p)]))
    affected = [p["id"] for p in manifest["pages"] if any(s in changed for s in p["sources"]) or p["id"] + ".md" in changed or "sidebar.json" in changed]
    interfaces = [i["id"] for i in manifest["interfaces"] if i["source"] in changed]
    return {"changed_paths":changed,"affected_pages":affected,"affected_interfaces":interfaces,"unclassified":sorted(set(unclassified)),"missing":sorted(set(missing)),"action":"classify and review before admission" if unclassified or missing else "review affected claims" if changed else "none"}


def discover(registry):
    data = registry_data(registry); roots = {Path(r["root"]).absolute():r for r in data["workspaces"]}
    classified, unclassified, errors = set(), set(), []
    blocked = BLOCKED | {"docs", "private", "Archive", "Backups", "data", "storage", ".git"}
    for declaration in data.get("discovery_roots", []):
        base = Path(declaration["root"]).absolute()
        depth = declaration.get("depth", 1)
        if not isinstance(depth, int) or not 1 <= depth <= 8: fail("discovery depth must be 1..8")
        if not base.is_dir() or base.is_symlink():
            errors.append("missing or symlink discovery root: " + str(base)); continue
        def walk(folder, level):
            try:
                items = sorted(folder.iterdir())
                for item in items:
                    if item.is_symlink() or not item.is_dir() or item.name.startswith(".") or item.name in declaration.get("ignore", {}): continue
                    if level == 1 and declaration.get("name_glob") and not fnmatch.fnmatchcase(item.name, declaration["name_glob"]): continue
                    owner = roots.get(item)
                    if level == 1 or (item / ".git").exists():
                        (classified if owner else unclassified).add(owner.get("site",{}).get("key", owner["id"]) if owner else str(item))
                    if owner and owner.get("kind") in ("reference", "archive", "adopted"): continue
                    if level < depth and item.name not in blocked: walk(item, level + 1)
            except OSError as error:
                errors.append("unreadable discovery path: " + str(folder) + ": " + error.__class__.__name__)
        walk(base, 1)
    return {"classified":sorted(classified),"unclassified":sorted(unclassified),"errors":sorted(set(errors))}


def onboard(registry, root, key, title):
    relpath(key)
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",key) or not title.strip(): fail("invalid key/title")
    root = Path(root).resolve()
    if any(Path(r["root"]).resolve() == root or r.get("site",{}).get("key") == key for r in projects(registry)):
        fail("duplicate root or key")
    return {"id":key,"title":title,"root":str(root),"kind":"maintained","site":{"key":key,"title":title,"source":"docs/handbook","navigation":"sidebar.json","verification":"docs/verification","owner":"owner required"},"required_paths":["docs/handbook/index.md","docs/handbook/sidebar.json","docs/verification/manifest.json","docs/verification/review.json"],"state":"proposal only; independent acceptance required"}


def export(build, input_dir):
    build = Path(build); input_dir = Path(input_dir)
    projects_data = load(input_dir/"projects.json")["projects"]
    receipt = load(input_dir/"input-receipt.json")
    staged_cross_docs = {p["key"]:{path.relative_to(input_dir/"docs"/p["key"]).as_posix():safe_bytes(path).decode("utf-8") for path in (input_dir/"docs"/p["key"]).rglob("*.md") if not path.is_symlink()} for p in projects_data if p["state"] == "admitted"}
    route_pages = {key:{name[:-3] for name in pages} for key,pages in staged_cross_docs.items()}
    directory = []
    for project_meta in projects_data:
        if project_meta["state"] != "admitted": continue
        key = project_meta["key"]; staged = input_dir/"docs"/key; pages = sorted(staged.rglob("*.md"))
        if not pages: fail(f"missing staged docs: {key}")
        markdown = {p.relative_to(staged).as_posix():safe_bytes(p).decode() for p in pages}
        staged_hashes = receipt["projects"][key]["staged_hashes"]
        staged_files = {p.relative_to(staged).as_posix():sha(safe_bytes(p)) for p in staged.rglob("*") if p.is_file()}
        if staged_files != staged_hashes: fail(f"staged input hashes differ: {key}")
        staged_docs = {**{p.relative_to(staged).as_posix():safe_bytes(p) for p in staged.rglob("*") if p.is_file() and not p.name.endswith(".md")}, **markdown}
        for text in markdown.values():
            if private_reader_text(text, project_meta.get("publicReaderPaths", ())): fail("private staged page")
            markdown_tokens(text, staged=True, approved_literals=project_meta.get("publicReaderPaths", ()))
        validate_links(key, {name[:-3]:name for name in markdown}, staged_docs, route_pages, staged=True, cross_docs=staged_cross_docs, approved_literals=project_meta.get("publicReaderPaths", ()))
        index = []
        for name,text in markdown.items():
            dest = build/"projects"/key/name
            dest.parent.mkdir(parents=True,exist_ok=True)
            canonical = project_meta["sourceLabel"] + "/" + name
            dest.write_text(text + f"\n\n---\nCanonical source: `{canonical}`. Reviewed: {project_meta['reviewedAt']}. Snapshot: `{receipt['projects'][key]['snapshot']['doc_hashes'][name]}`.\n")
            index.append(f"- [{frontmatter(text, staged=True, approved_literals=project_meta.get('publicReaderPaths', ()))[0]['title']}](/projects/{key}/{'' if name=='index.md' else name[:-3]})")
        (build/"projects"/key/"llms.txt").write_text("# " + project_meta["title"] + "\n" + "\n".join(index) + "\n")
        directory.append(f"- [{project_meta['title']}](/projects/{key}/llms.txt)")
    build.mkdir(parents=True,exist_ok=True)
    (build/"llms.txt").write_text("# Project manuals\n" + "\n".join(directory) + "\n")
    return {"exported":len(directory)}


def main(argv=None):
    parser = argparse.ArgumentParser(); sub = parser.add_subparsers(dest="command",required=True)
    for name in ("check","prepare","snapshot","impact","discover","onboard","export"):
        cmd = sub.add_parser(name)
        if name != "export": cmd.add_argument("--registry",type=Path,default=Path(__file__).resolve().parents[2]/"workspaces.json")
        if name in ("check","snapshot","impact"): cmd.add_argument("--project",required=name!="check")
        if name == "check": cmd.add_argument("--json",action="store_true")
        if name == "prepare": cmd.add_argument("--output",type=Path,default=Path(".generated"))
        if name == "export": cmd.add_argument("--build",type=Path,required=True); cmd.add_argument("--input",type=Path,default=Path(".generated"))
        if name == "onboard":
            cmd.add_argument("--root",type=Path,required=True); cmd.add_argument("--key",required=True); cmd.add_argument("--title",required=True); cmd.add_argument("--check",action="store_true")
    args = parser.parse_args(argv)
    try:
        result = {"check":lambda:check(args.registry,args.project),"prepare":lambda:prepare(args.registry,args.output),"snapshot":lambda:snapshot(args.registry,args.project),"impact":lambda:impact(args.registry,args.project),"discover":lambda:discover(args.registry),"onboard":lambda:onboard(args.registry,args.root,args.key,args.title),"export":lambda:export(args.build,args.input)}[args.command]()
        print(json.dumps(result,indent=2,sort_keys=True))
        if args.command == "check" and (any(p["state"]=="invalid" for p in result["projects"].values()) or (args.project and result["projects"][args.project]["state"]!="admitted")):
            return 1
        return 0
    except (PortalError, ValueError, KeyError, TypeError, UnicodeDecodeError) as exc:
        print(f"portal: {exc}",file=sys.stderr); return 1


if __name__ == "__main__": sys.exit(main())
