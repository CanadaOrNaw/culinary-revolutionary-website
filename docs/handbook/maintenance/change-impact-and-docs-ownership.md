---
title: "Documentation maintenance and change impact"
description: "Review exact changed interfaces, claim sources, examples and independent acceptance without creating another tracker."
kind: "developer"
source_ref: ["AGENTS.md", "CONTEXT.md", "docs/CONTEXT.md#L1-L5", ".githooks/docs-pre-commit#L1-L4", ".github/workflows/deploy-pages.yml#L35-L59"]
---


# Documentation maintenance and change impact

Canonical reader pages and navigation live in `docs/handbook/`. Private `docs/verification/` records source/page/interface coverage, safe examples and exact review evidence. The unified portal reads approved inputs; it is not a second authoring home. No raw source, review receipt, customer record or old generated private product belongs in reader output.

## Review impact before acknowledging freshness

| Changed source | Review these facts/pages | Product/test impact |
|---|---|---|
| Menu fields, ids, course/item rules | [Menu reference](../reference/menu-source.md), [update workflow](../how-to/update-menus.md) | Full menu/home grid, static options and links; offline checker does not compare every dish |
| Article metadata/body/image | [Article reference](../reference/article-source-and-metadata.md), [edit](../how-to/write-and-rebuild-an-article.md), [retire](../how-to/change-or-retire-article-source.md) | Article, index, homepage, feed and sitemap and stale dirs |
| Home shell or generator boundaries | [Architecture](../architecture.md), [dataflow](../architecture/source-to-public-artifact.md) | Both generators, separately authored confirmation shell |
| Form/endpoint/DOM/query/constants | [Browser reference](../reference/browser-contracts-and-form.md), [inquiry flow](../architecture/inquiry-and-personal-data.md) | Native vs enhanced payload, defaults, failure/redirect/privacy; no automatic live test |
| CSS/assets/crawl metadata | [Design/assets](../reference/design-assets-and-crawl.md), [preview](../how-to/preview-and-review-interactions.md) | Browser review and asset rights; parser is partial |
| Workflow/diagnostic/dependencies | [CLI](../reference/generator-and-checker-cli.md), [setup](../developer/setup-and-project-map.md), [publication](../how-to/review-publication-and-domain-evidence.md) | Public exposure, CI order, external-effect boundary |
| Launch authority/client decisions | [Collaboration](../collaboration.md), [status](../status.md) | Preserve dates and owner approval; no invented tracker state |

For a concrete change, name the exact files, interfaces, pages and behavior affected. A no-documentation-impact disposition needs a reason tied to that change, not a blanket checkbox. New meaningful source must be classified rather than silently omitted.

## Two different gates

**Integrity/freshness:** manifests/nav/source refs agree, exact bytes match the reviewed hashes, links and safe inputs validate. This catches drift.

**Correctness/usefulness:** a person or independent agent compares implementation claims to source/tests and completes representative reader/developer tasks. They record starting state, observations, assistance, findings and limits. This cannot be manufactured by a build, timestamp or hash.

The author snapshot's decision is changes-required. An independent reviewer must assess the exact source/docs/navigation/asset inputs before acceptance. Any relevant content/source/nav/asset change invalidates earlier exact-byte acceptance until reviewed again.

## Submitted policy and generated ownership

The actual Pages workflow invokes the shared portable submitted-index checker before the blog build. The local pre-commit script calls the central enforcement owner. Both callsites are reviewed project source; their presence alone is not proof they ran.

The derived `.docs-check/` tree is generated policy, not authored culinary implementation. The shared enforcement generator owns its three scripts, two schemas, selected portable registry and receipt. Do not declare/hash these copies into their own project acceptance: source or receipt changes would create circular evidence. The shared owner separately verifies generator/member/registry/toolchain identity, complete bundle inventory and submitted executing-byte agreement.

The workflow gate reads the complete submitted index and requires actual independent source/docs review. A working-tree repair does not approve stale submitted content or policy. New bundle files must be eligible and actually submitted before a clean checkout can use them. This author does not stage, untrack products, edit bundles or change tests/dependency pins to hide a gate failure.

Removed copied `docs.py`/`render.py` and their old four-page registry assumptions are historical, not current project CLI. Existing `docs/handbook/_generated/` HTML/PDF/receipt views remain excluded and are not rebuilt here. Shared migration or release evidence stays with its owner; no generic hash refresh grants correctness or business/runtime acceptance.

## Contribution and handoff

1. Read root/owner contracts and [collaboration](../collaboration.md).
2. Review source changes and map claims before prose.
3. Update only authorized canonical docs and private verification records; preserve unrelated work.
4. Run explicitly safe native examples, recording commands/effects/exit/output. Do not execute arbitrary Markdown snippets or live form/publication commands.
5. Obtain independent source/task review. Record findings and fixes; never self-accept.
6. Let the shared owner validate/build/release only accepted content. Authoring is not publication or product acceptance.

No source constants are changed by this handbook authoring. Runtime acceptance, business account actions and private record ownership remain with their original owners.
