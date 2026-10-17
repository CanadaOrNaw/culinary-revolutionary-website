---
title: Project and collaboration overview
description: Understand the business outcome, implemented work, decisions, open questions
  and how humans or agents contribute.
kind: overview
source_ref:
- AGENTS.md#L15-L31
- README.md#L67-L139
- LAUNCH.md#L3-L66
- LAUNCH.md#L86-L91
- CLIENT-QUESTIONS.md#L8-L99
- DESIGN.md#L36-L49
---

# Project and collaboration overview

## Intended outcome

Help prospective guests understand the chef's services and sample menus, then send enough information for a human availability check and quote. The website is not an online booking, pricing or payment system. The inquiry copy describes a personal reply, planning call and written proposal rather than a confirmed reservation.

The developer outcome is equally concrete: an approved menu or article change should produce a reviewable set of static files without leaking private operational material.

## What is implemented now

| Area | Implemented behavior | Evidence boundary |
|---|---|---|
| Public experience | Home, services, broad service area, biography, seven menus, articles and inquiry | Source and offline markup checks; not a fresh live-site inspection |
| Content maintenance | Menu generator and article generator | Both rewrite products; neither is transactional or a publishing scheduler |
| Inquiry | External Web3Forms relay, native form and unconfigured email-draft path | Owner confirmed delivery on 2026-09-10; today's inbox and reply-to behavior are not established here |
| Release | Main-branch/manual Pages workflow with explicit public staging | Workflow source reviewed; no remote run queried |
| Developer documentation | This project-local topic tree and private verification map | Author snapshot awaits independent source/task review; not self-accepted |

[Status](status.md) owns this documentation's evidence summary. The repository's `LAUNCH.md` owns the dated launch confirmation and account/domain decisions. `CLIENT-QUESTIONS.md` owns unresolved chef questions. Those remain source records; this page is not a competing queue.

## Decisions that affect contributors

- Keep the business site plain and static. The generators use Python's standard library; the public browser does not run a framework bundle.
- Keep approved factual claims separate from inference. Do not invent specific service cities from the phone prefix, prices, reviews, certifications, awards or personal bylines.
- Keep the established mailbox, registrar/DNS and Pages hosting decisions. A historical automation-only preflight rejection did not justify changing providers or buying an eligibility plan.
- Draft and obtain approval for outward actions. The README also records a specific externally owned weekly publishing authorization; do not generalize that into permission for any agent to publish.
- Preserve deterministic source-to-product generation. Fix the owning source rather than patching a generated page.

The old `DESIGN.md` is a prototype record. Its non-submitting demo-form description is superseded by the dated launch record and current code. Retained Agrippa references describe history, not a component to restart.

## Limitations and blockers

The chef still owns answers about menu ambiguities, travel radius, pricing/minimums, insurance/certification claims, biography details and image rights. Provenance is not a license. Confirm the relevant item at `CLIENT-QUESTIONS.md` before changing copy.

No current live mailbox, provider, Pages, DNS or external weekly-job health is claimed. No browser support matrix or persisted browser-response test suite exists in this repository. See [verification limits](status.md#verification-and-limits).

## How to contribute

**Content editor:** start with [menu editing](how-to/update-menus.md) or [article editing](how-to/write-and-rebuild-an-article.md). Get factual and image approval before writing. Keep customer, billing and account material outside public source/output trees.

**Developer:** start with [repository map](developer/setup-and-project-map.md), [architecture](architecture.md) and [testing](developer/testing-and-extension-points.md). Respect exact homepage extraction markers and the two generators' overlapping output ownership.

**Human or agent reviewer:** follow [maintenance](maintenance/change-impact-and-docs-ownership.md). Review changed claims against implementation, run only safe explicit examples, and record assistance and limits. Do not approve prose by refreshing a fingerprint.

**Release owner:** use [publication review](how-to/review-publication-and-domain-evidence.md). A main push is an outward-facing deployment, not merely a local save.

## Progress and demonstrations

`LAUNCH.md` records September 10 production deployment, historical local browser-response/mobile/menu tests, and the user's successful inquiry test. Those are dated demonstrations, not a current replay. Old preview captures are not included in this handbook and are not fresh acceptance evidence.

A new reader can reproduce a safe local demonstration now: [run the offline checker](tutorials/check-the-shipped-site-offline.md), then [trace a menu inquiry without submitting](tutorials/trace-a-menu-inquiry.md). Independent documentation task trials and a current live demonstration remain separate work; none is invented here.
