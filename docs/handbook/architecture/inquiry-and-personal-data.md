---
title: Inquiry and personal data
description: Follow enhanced POST, native POST and unconfigured email drafts without
  claiming inbox delivery.
kind: concept
source_ref:
- index.html#L474-L600
- script.js#L62-L109
- script.js#L111-L229
- thank-you.html#L88-L123
- LAUNCH.md#L39-L56
---

# Inquiry and personal data

The site collects contact/event details for a human response. It does not store inquiries in a local application database, confirm a reservation or take payment.

## Three real paths

| Starting state | Browser behavior | What success actually means |
|---|---|---|
| JavaScript and configured routing | Validate form, map trimmed values into JSON, POST to the form action | HTTP success plus JSON `success === true`; then relative thank-you navigation |
| JavaScript with missing/blank/exact placeholder routing | Open a URL-encoded prefilled email draft | Only a draft opened; visitor must send it in their own mail app |
| JavaScript absent | Native HTML form POST with hidden routing/subject/from-name/redirect | Provider controls response and absolute canonical redirect; JS success/fallback logic does not run |

The hidden routing value is publicly served so the form can work, but it is site-specific. It is intentionally not copied into documentation, examples or other sites. The script reads the endpoint and trimmed routing value from the markup rather than an environment file.

## Enhanced request sequence

1. Intercept submit and call browser `reportValidity()`.
2. Build `FormData`; if the hidden honeypot is truthy, silently return.
3. Trim the displayed fields. Match the optional menu query against actual option values, case-insensitively.
4. Disable the submit button, display pending status and send JSON.
5. Require an OK HTTP response and parsed JSON whose `success` is exactly `true`.
6. Navigate to `thank-you.html`. Otherwise reenable the button, show direct-contact fallback and log the error.

No custom request timeout, retry or durable client queue exists. On a cached-page return, `pageshow` reenables the button and clears status. Closing the page or observing the thank-you page is not evidence of inbox receipt; the confirmation page can be opened directly.

## Native and enhanced fields differ

The HTML names are `location`, `menu`, `guests` and `date`. The enhanced JSON names are `event_location`, `menu_of_interest`, `guest_count` and `preferred_date`. The script also supplies its own subject/from-name and default strings. [Browser reference](../reference/browser-contracts-and-form.md) lists both contracts exactly.

With no JavaScript, the placeholder-to-email fallback is unavailable. Native POST capability is distinct from full no-JavaScript navigation: at narrow widths the main navigation is hidden until the script toggles it.

## Privacy and acceptance boundaries

The privacy copy says details are used to respond, discloses Web3Forms and asks visitors not to include payment information. Dietary notes may contain sensitive health information. Keep documentation examples fictional and minimal; never copy actual submissions, mailbox content or customer records.

The README records the provider's historical free-plan retention statement; this authoring pass did not verify current provider terms. Client validation and a honeypot are useful behavior, not demonstrated spam prevention or server-side validation guarantees.

`LAUNCH.md` records an automation-only preflight rejection and later user-confirmed delivery on 2026-09-10. Do not treat the former as proof of a broken customer form, or the latter as a current delivery test. Reply-to behavior remains separately unconfirmed.

For safe first use, [trace a menu request in source](../tutorials/trace-a-menu-inquiry.md). Live form/browser/inbox tests are outward actions requiring owner approval, not routine documentation examples.
