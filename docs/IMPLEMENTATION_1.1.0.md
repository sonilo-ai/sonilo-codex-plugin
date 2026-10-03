# Sonilo 1.1.0 implementation

> October 3 verification update: **not release-ready**. Backend PRs #393 and
> #398 are merged and deployed. Live dubbing preview, full approved-script
> continuation, and timed-SFX generation now succeed. Clean Codex conversation
> checks and listening verification, including exact SFX timing, remain.
> The current Skill upload passed its portal scan.
> Production media results and isolated credit-recovery coverage are recorded
> in [the live verification report](LIVE_TEST_1.1.0.md). Package coverage below
> is not proof that every workflow has passed a clean Codex conversation test.


Scope: the 13 features in the [manager plan](https://docs.google.com/document/d/1woqbRgMlCemdw46mpP6Wz1uDkVUK9_C4QyPi2cX2y0s/edit).
This package updates the hosted-MCP workflow instructions and listing metadata;
it does not deploy the server, publish the plugin, or change account entitlements.

| Plan item | Package behavior |
| --- | --- |
| Subtitle review before dubbing | Route to `proofread`, wait for approval, then use approved target-language subtitle URLs. Requires the service to be enabled. |
| Music and effects together | Use one combined tool, selecting audio or new-video output to match the request. |
| Free dubbing preview | Check trial eligibility, require one explicit target language and no scripts, label the actual preview metadata. |
| Full video after preview | Require the user's full-version request; submit the original source once as a new task, without claiming only the remainder is billed. |
| Balance and trial lookup | Read current `cash_balance` and `currency` from `get_account_services`, alongside actual service trial counts. Preserve USD sub-cent precision; missing values remain unknown. Usage history is separate. |
| Insufficient-credit feedback | Explain the actual error, avoid repeated submissions, and report charging/refunds only when established. Link to the deployed Balance and free trials guide in the conversation language; no automatic retry or direct purchase link. |
| Continue after account update | Refresh services, retain known inputs, and retrieve existing work before any authorized resubmission. |
| Usage examples | Bundle concrete prompts and response patterns; link the public MCP guide for product-help requests. |
| Generation status | Poll the original task; preserve its ID after interruptions and avoid unsupported background-monitoring promises. |
| Multiple variants | Use one supported `variants_num` request and label each returned variant. Do not use a free-only request to authorize paid variants. |
| Audible narration | Use supported speech preservation and ducking parameters; remove obsolete `isolate_vocals` guidance. |
| Timed effects | Follow the hosted JSON-string segment schema, including contiguous quiet gaps. |
| Instrument stems | Request stems of generated music, return actual stem URLs, and handle partial separation failures without regenerating. |

## Backend integration

[Backend PR #384](https://github.com/sonilo-ai/sonilo-api-dashboard/pull/384)
was merged and [deployed to production](https://github.com/sonilo-ai/sonilo-api-dashboard/actions/runs/36210070550)
on 2026-09-26 UTC. The hosted account tool now returns `cash_balance` (decimal
string) and `currency` (`USD`); it does not expose `billing_mode`. No new plugin
endpoint, OAuth scope, or client library is needed.

The manager plan's dollar-balance example is supported using actual returned
data. Its continuation examples are intent illustrations: the plugin reports
current balance, but never promises sufficient funds from a snapshot alone.
“No charge” and “trial exhausted” wording requires evidence in the response.

## Published help page and review status

The [Balance and free trials guide](https://platform.sonilo.com/usage-and-entitlements)
was deployed on 2026-10-02 after dashboard PRs #391 and #392, in
[production run 37076829530](https://github.com/sonilo-ai/sonilo-api-dashboard/actions/runs/37076829530).
The skill links its 10 language routes for confirmed credit rejections and
balance/trial help. It preserves the original request for user-requested continuation.

The page deliberately retains the public site's shared navigation and the
**View pricing / View billing** buttons requested for review. The plugin reply
links to the explanation and does not tell users to click through to purchase.
This is a review candidate, not an assertion that OpenAI has approved the flow.
The commerce rules prohibit direct or indirect digital-service sales; acceptance
of this page with its onward buttons remains unconfirmed. Do not hide those
buttons or describe the page as having no purchase-related links in review materials.

Hosted availability still depends on the connected account. In particular,
`proofread` is feature-gated. Check connected schemas and `available_services`
at runtime; this package does not change backend flags.

## Verification scope

- Package structure, assets, reference links, manifest, and skill validation.
- Documented tool names and parameter types compared with the hosted MCP source.
- Read-only production endpoint and OAuth discovery checks via `check_release.py --live`.
- No paid generation, authenticated end-to-end media run, server deployment,
  directory submission, or installed-plugin replacement is performed by these checks.

Reference: [OpenAI commerce and monetization](https://developers.openai.com/plugins/plugin-guidelines#commerce-and-monetization).
