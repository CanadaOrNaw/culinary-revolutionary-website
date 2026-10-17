---
title: Browser and inquiry reference
description: Look up DOM bindings, menu query values, native/enhanced fields and failure
  defaults.
kind: reference
source_ref:
- index.html#L146-L194
- index.html#L474-L600
- script.js#L12-L109
- script.js#L111-L237
- styles.css#L419-L469
- styles.css#L728-L759
---

# Browser and inquiry reference

The sole browser program is an immediately invoked function in `script.js`, not an exported JavaScript library. It binds existing DOM controls; there is no culinary HTTP-server API.

## DOM and navigation bindings

| Binding | Behavior |
|---|---|
| `menu-toggle`, `primary-nav` | Optional pair; click toggles `.open` and `aria-expanded` |
| Nav link click | Closes nav |
| Escape while open | Closes and returns focus to toggle |
| Document click outside nav/toggle | Dismisses open nav |
| Resize beyond 1200 pixels | Closes nav |
| `inquiry-form` absent | Program returns after setting up navigation |
| `form-status` | Reveals text/status class, `role=status`/polite live region in markup |
| `form-mode-note` | Revealed only for unconfigured routing |
| `inquiry-submit` | Text changes for draft mode; disabled while enhanced request pending |
| `menu-interest` | Optional query selection match |
| `pageshow` | Reenables submit and clears status on cached-page return |

Status classes are `is-pending` and `is-error`. Honeypot styling hides `botcheck` visually and removes pointer interaction; script silently returns if its value is truthy.

## Menu query

`?menu=VALUE#inquiry` compares VALUE case-insensitively with actual option values. Unknown values are ignored. Current values are:

```text
(empty), italian-feast, brunch, tour-of-spain, key-west-inspired,
wild-game, spanish-tapas, vegetarian, custom
```

The generator emits source ids in request links but does not update this static list. [Menu trace](../tutorials/trace-a-menu-inquiry.md) shows the cross-file contract.

## HTML form contract

Action: `https://api.web3forms.com/submit`; method POST, ordinary native form encoding when JavaScript is absent.

| Name | HTML behavior |
|---|---|
| `access_key` | Hidden provider routing value; deliberately not reproduced |
| `subject`, `from_name` | Hidden native subject/site name |
| `redirect` | Hidden absolute canonical thank-you URL for native flow |
| `botcheck` | Hidden checkbox honeypot, not keyboard focusable |
| `name` | Required text, name autocomplete |
| `email` | Required email type/autocomplete |
| `phone` | Optional telephone/autocomplete |
| `service` | Select: Private Chef, Catering, Meal Preparation, In-Home Cooking Class, Restaurant Consultation |
| `location` | Required city/ZIP text, address-level2 autocomplete |
| `menu` | Optional static menu value |
| `guests` | Optional number, minimum 1, numeric input mode |
| `date` | Optional date input, no minimum date in markup |
| `notes` | Optional textarea |

Native HTML names are not identical to enhanced JSON field names. Native required/type/min handling is not demonstrated server-side validation.

## Enhanced JSON request

The script first calls `reportValidity`, checks the honeypot and trims displayed values. It POSTs to the form's action with `Content-Type: application/json` and `Accept: application/json`.

| JSON field | Source/default |
|---|---|
| `subject` | `New website inquiry — ` plus name or `prospective client` |
| `from_name` | `Culinary Revolutionary website` |
| `name`, `email` | Trimmed form values |
| `phone` | Trimmed value or `Not provided` |
| `service` | Trimmed value or `Not specified` |
| `event_location` | HTML `location` or `Not specified` |
| `menu_of_interest` | HTML `menu` or `Not specified` |
| `guest_count` | HTML `guests` or `Not specified` |
| `preferred_date` | HTML `date` or `Not specified` |
| `notes` | Trimmed value or `None provided` |
| `access_key` | Trimmed hidden routing value |

No `redirect` or `botcheck` field is sent in this enhanced payload. The script performs its own honeypot return and success navigation.

## Response and fallback contract

An enhanced success requires both `response.ok` and parsed JSON with `success === true`. Non-OK HTTP, rejected/missing/malformed/null success data or fetch failure leads to direct-contact error text and reenabled submit. Error details go to browser console; fields are not deliberately reset.

Success navigates to relative `thank-you.html`. No timeout/retry is configured, so a pending network operation can remain pending. This is not inbox-delivery proof.

For missing, blank or exact `PASTE_WEB3FORMS_ACCESS_KEY_HERE` routing, script changes the button to Open email to send, reveals the draft note, creates a `mailto` subject/body with `encodeURIComponent`, and navigates to the visitor's email handler. After 2000 ms it shows contact fallback if still on the page. A draft requires the visitor to send; no configured mail handler may exist.

The fallback recipient and JS thank-you target are constants in `script.js`; the native redirect is separately in HTML. There is no application environment configuration. A mailbox/domain change must review all affected copy/constants/routes, not blindly assume one hidden field updates every contract.

For privacy and live-test limits read [inquiry architecture](../architecture/inquiry-and-personal-data.md) and [status](../status.md).
