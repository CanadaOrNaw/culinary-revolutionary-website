---
title: Generator and checker CLI
description: Look up real command arguments, defaults, write effects, exit behavior
  and unsupported flags.
kind: reference
source_ref:
- build-menus.py#L1-L14
- build-menus.py#L158-L187
- build-blog.py#L10-L46
- build-blog.py#L78-L111
- tests/check-site.py#L1-L80
- ops/verify-domain.sh#L1-L28
- .githooks/docs-pre-commit#L1-L4
- .github/workflows/deploy-pages.yml#L27-L39
---


# Generator and checker CLI

Run maintenance commands from the repository root unless otherwise noted. No application environment variables or install command are defined. Command names below are actual interfaces, not permission to perform their effects.

## Menu builder

```bash
python3 build-menus.py menus.json
```

| Property | Actual behavior |
|---|---|
| Optional first argument | JSON path; defaults to `menus.json` beside the script |
| Relative supplied path | Resolved from shell working directory |
| Extra arguments | Ignored; only `sys.argv[1]` is read |
| Required root JSON member | `menus` |
| Outputs | Overwrite script-adjacent `menus.html`, then homepage teaser region |
| Success output | Page length/menu/dish counts, then `index.html teaser grid replaced` |
| Exit 0 | Top-level program reached both writes and final print |
| Failure | Normal uncaught Python exception/nonzero (normally 1); no custom error-code mapping |

The printed page-length label says bytes, but its value is Python `len(page)`, a character count. No argparse/help/version/dry-run/output-dir interface exists. `--help` is treated as an input filename, not help. The `menus.html` write precedes the homepage boundary lookup, so failure can leave partial products.

## Blog builder

```bash
python3 build-blog.py
```

| Property | Actual behavior |
|---|---|
| Arguments/options | None parsed; extra tokens ignored |
| Inputs | Script-adjacent home chrome and `content/blog/*.json` plus eligible same-stem HTML/images |
| Origin | Hardcoded `https://culinary-revolutionary.com` |
| Eligibility | Publication date not later than current UTC date |
| Sort | Publication-date string, then slug, both descending |
| Reading time | Strip tags; word count / 200; rounded; minimum 1 minute |
| Minimum content | At least one eligible published post |
| Outputs | Article pages, blog index, homepage preview, sitemap, RSS |
| Success output | `Built blog index, N article(s), RSS, homepage preview and sitemap.` |
| Failure | Uncaught file/JSON/key/date/value/regex errors; normally exit 1 |
| Exit 0 | All writes and final print reached |

There is no date override, prune, per-post build, output directory, dry-run or `--help` contract. Article/index writes precede homepage marker validation. The program does not delete obsolete directories. See [article schema](article-source-and-metadata.md) for explicit validation messages.

## Offline site checker

```bash
python3 tests/check-site.py
```

No arguments are parsed. It reads current root/blog HTML plus sitemap/RSS and local targets; it makes no network request or file write. Exit 0 prints PASS; an uncaught assertion/parse/file/key error exits nonzero, normally 1. Do not run under `-O`.

The [tutorial](../tutorials/check-the-shipped-site-offline.md) shows a real run. It is not a generator-freshness, live-delivery or browser test.

## Temporary preview

```bash
python3 -m http.server 8096 --bind 127.0.0.1
```

This is the README's stdlib server command, not a culinary server/API. It serves the current directory, starts a process and requires deliberate cleanup with Ctrl-C. No culinary-specific exit mapping exists. It was not started in author verification; read [preview safety](../how-to/preview-and-review-interactions.md).

## Domain diagnostic

```bash
bash ops/verify-domain.sh
```

No arguments are parsed. `DOMAIN` is a hardcoded shell variable. Requirements: Bash with uppercase parameter expansion, `curl`, `jq`, `dig`, `tr` and network access.

The script reads registry status/nameservers via RDAP, DNS NS/A/www CNAME/MX/TXT, A answers from two public resolvers, then four HTTP/HTTPS apex/www URL status/effective destinations. It does not modify accounts or DNS.

`set -euo pipefail` can stop on early tool/pipeline errors. Serving curl failures are caught and printed as unavailable. DNS/HTTP values are printed rather than asserted against expected records. Thus exit 0 is not a full health result. Not executed during authoring.

## Submitted-index documentation check

The Pages workflow now calls the portable shared checker before building the blog:

```text
python -B .docs-check/scripts/check_index.py check
  --registry .docs-check/workspaces.json
  --project culinary --git-root "$PWD"
  --receipt .docs-check/receipt.json
```

This is the exact workflow command split for reading; the workflow owns its actual single-line shell invocation. It uses the interpreter supplied by setup-python, not a culinary application environment.

| Input | Actual purpose |
|---|---|
| `check` | Only submitted-index checker action |
| `--registry` | Required portable selected-project registry |
| `--project culinary` | Required stable project key, not the retired `--id` option |
| `--git-root` | Required selected checkout root |
| `--receipt` | Portable bundle receipt; binds complete member inventory and hashes |
| `-B` | Python bytecode-write suppression, not an application flag |

The shared checker compares executing checkout-local policy against its complete stage-0 Git index before validation. The portable registry is relocated into an isolated index snapshot. Source, handbook, manifest and independent review must agree there; an unstaged working repair does not approve the submitted snapshot.

Exit 0 means the selected indexed project is admitted. Exit 1 means a valid check is pending/non-admitted. Exit 2 reports policy/index/receipt/input errors; invalid argparse usage also uses 2. Missing/extra/nonregular/symlink bundle members, executing-versus-index byte mismatch, receipt mismatch and selected-project disagreement are errors, not reasons to alter tests or pins.

The derived `.docs-check/` bundle has exactly seven files: three scripts (`check_index.py`, `index_snapshot.py`, `portal.py`), manifest/review schemas, portable `workspaces.json` and `receipt.json`. The shared `fleet-index/_system/documentation/enforce.py` generator owns regeneration. These generated executors/receipts are excluded from this project's authored-source hashes to avoid making policy hash its own project acceptance. The actual workflow and local enforcing-hook call remain reviewed source.

The local hook path uses the shared owner rather than this portable command. A present hook/bundle does not prove invocation, index inclusion, remote CI success or business acceptance. Do not run generator sync, stage/untrack policy, hand-edit copied files or run a real submitted-index mutation as a documentation example. Current integration evidence is parent-owned.

The removed copied `docs.py`/`render.py` and their four-page `build/check/fingerprint` interface are no longer current project commands. Historical `_generated/` views remain excluded; do not rebuild them to claim new acceptance. See [maintenance](../maintenance/change-impact-and-docs-ownership.md).
