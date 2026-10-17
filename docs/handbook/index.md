---
title: Culinary Revolutionary
description: Maintain the static chef website from approved source without confusing
  local checks with live delivery.
kind: overview
source_ref:
- CLAUDE.md#L1-L31
- README.md#L3-L23
- LAUNCH.md#L3-L21
---

# Culinary Revolutionary

Culinary Revolutionary is a static website for a private-chef business. Maintainers edit plain HTML, CSS and JavaScript, approved menu data, and article source. Two Python scripts generate the repeated content. There is no application server, database or framework install.

This handbook is for Zack, approved content editors and developers. It is **private developer documentation**, not part of the public chef website.

## Choose your task

| I need to… | Start here |
|---|---|
| Understand the outcome, current work and contribution boundaries | [Collaboration overview](collaboration.md) |
| Get a safe first result without sending or publishing anything | [Offline site check](tutorials/check-the-shipped-site-offline.md) |
| Find requirements and the right source file | [Setup and repository map](developer/setup-and-project-map.md) |
| Understand what writes each public artifact | [Architecture](architecture.md), then [source-to-artifact flow](architecture/source-to-public-artifact.md) |
| Change dishes or article copy | [Update menus](how-to/update-menus.md) or [write an article](how-to/write-and-rebuild-an-article.md) |
| Understand inquiry fields and response handling | [Inquiry flow](architecture/inquiry-and-personal-data.md) and [browser reference](reference/browser-contracts-and-form.md) |
| Find exact commands, defaults or schema fields | [CLI reference](reference/generator-and-checker-cli.md), [menu source](reference/menu-source.md), [article source](reference/article-source-and-metadata.md) |
| Diagnose a failure or assess a release | [Troubleshooting](operations/verification-and-troubleshooting.md) and [publication review](how-to/review-publication-and-domain-evidence.md) |

## What works, and what that means

The inspected source implements seven sample menus, authored planning articles, crawlable HTML, and three inquiry paths: a JavaScript relay request, native HTML POST, or an email draft when routing is unconfigured. [Status](status.md) separates checked local behavior from dated owner confirmation and untested live state.

A local checker passing is useful. It is not evidence that a message reached the business inbox, a weekly job ran, or a public deployment is current.

## Keep source ownership clear

- Edit `menus.json`, not the generated full menu page or teaser cards.
- Edit article metadata/body pairs, not generated article pages.
- The public deployment stages an allowlist. Do not add private records to published trees.
- Publishing and live inquiry tests need the owning business approval. A command printed here does not grant that approval.

See [collaboration](collaboration.md) for decisions and contribution routes, and [maintenance](maintenance/change-impact-and-docs-ownership.md) for claim/source review before handoff.
