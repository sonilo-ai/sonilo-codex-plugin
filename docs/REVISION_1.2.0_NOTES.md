# Revision 1.2.0 draft notes

> Status — November 19, 2026: **1.2.0 approved and published.** OpenAI
> approved it the day it was submitted (email "ChatGPT Plugin Submission
> Approved" to dev@sonilo.com, no conditions). Published from the dashboard
> with "Publish plugin", which replaced 1.0.0: "Version 1.2.0", "Listed
> publicly". It carries the fixes for the October 21 rejection of 1.1.0 (see
> "Response to the 1.1.0 rejection" below). GitHub `main` is 1.2.0 (PR #4,
> merged before the decision). The six policy attestations were ticked on
> the user's instruction, the same six the user confirmed for 1.1.0; the
> review-private "Additional Submission Context" note is under "Submission".

## Response to the 1.1.0 rejection

The rejection email (openai-review → dev@sonilo.com, October 21) gave two
reasons and no further detail:

1. The plugin "appears to enable or facilitate commerce for disallowed
   offerings (e.g., digital goods/services or other prohibited categories)."
2. The "plugin name or description did not meet our quality standards."

What 1.1.0 added over the approved 1.0.0, and the likely triggers:

- After a credit rejection the skill linked the localized "Balance and free
  trials" guide (`/usage-and-entitlements`). That page carries View pricing
  and View billing buttons to `/pricing` and `/dashboard/billing`, so the
  plugin routed users from an out-of-credit error straight to a purchase.
  `docs/REVISION_1.1.0_NOTES.md` had already flagged this link as unconfirmed.
- The listing promoted "check your USD balance and free trials", "existing
  account funds", and a free dubbing preview followed by the paid full video.
- The long description was long and read like terms of use.

Changes in this draft:

- `plugin.json`: long description rewritten (567 characters; the 1.1.0 portal copy was 818)
  around what the plugin makes; no balance, funds, trial, or preview wording.
  Capability "Cash balance, trial allowance and usage reporting" is now
  "Usage reporting", as in 1.0.0.
- Skill: the balance guide and all ten of its links are removed. Credit
  errors carry no links, prices, or purchase steps. The balance is reported
  only when the user asks. No pitching of paid follow-ups; the full-video
  price from `trial_preview` is quoted only on request. Skill metadata no
  longer advertises balances.
- `scripts/check_release.py`: the guide-link checks are replaced by guards
  that fail if guidance links `/usage-and-entitlements`, `/pricing`, or
  `/dashboard/billing`, or if the listing or capabilities use commerce words.
  Checked against the 1.1.0 manifest and reference: both fail.
- `docs/LISTING_COPY_1.2.0.json`: new English copy and nine translations
  (drafted by Claude, not natively reviewed).

Hosted server (`sonilo-api-dashboard` PR #475, merged as `4a5f3a4a`,
deployed to `backend-mcp` task definition `:135` on November 18, 2026):

- The dubbing preview message ("Translating the full video costs $X — add
  funds at <billing URL>"), the `trial_exhausted` 402 with the billing link,
  and the "or add funds" hints no longer reach ChatGPT or Codex. The server
  decides by the MCP handshake name: `openai-mcp` (ChatGPT),
  `openai-mcp (Codex)`, `codex-mcp-client`, and any unidentified MCP client
  get no purchase prompt; REST and other MCP clients are unchanged.
- Covered by end-to-end tests through the real MCP transport.
- Checked by hand in ChatGPT web on November 18, 2026 (zero-balance
  prepay account; ChatGPT identified itself as `openai-mcp (Codex)`):
  a free Spanish preview of `tests/fixtures/speech-demo.mp4` returned
  "Free preview: the first 15 seconds of your 22-second video, in 1
  language. The rest of the video was not translated." (task `798e7e62…`,
  no charge); the follow-up full-length request was refused with "You've
  used your 1 free 15-second video translation preview." (no link, no task,
  no charge). Codex with the plugin's bundled MCP config
  (`codex-mcp-client`) was not checked by hand.
- ChatGPT still quoted `trial_preview.full_video_cost_usd` unprompted
  ("$1.28"). PR #476 (`0edf4feb`, task definition `:136`) makes the field
  optional in `get_generation_task`'s output schema and adds
  `MCP_PREVIEW_PRICE_TO_OPENAI_CLIENTS` (default True: nothing changes yet).
- The `dubbing` tool description changed with it ("says what the preview
  covered"). The daily MCP scan held the previous `dubbing` change on
  November 17 and will hold this one too; the earlier definition stays live
  until a manual review passes.

## Why

Two hosted tool changes landed after 1.1.0 was submitted:

- The subtitle tool is now listed as `generate_video_subtitles`. The name
  `proofread` is no longer in the hosted tool list, and OpenAI's scan no
  longer shows it. The 1.1.0 skill still routes to `proofread`.
- `create_upload_url` lets the hosted server take a file from the user's
  machine. The skill guidance for it was added to the `codex/plugin-v1.1.0`
  branch in PR #3 on October 9, after the 1.1.0 package had been submitted,
  so the package in review does not contain it. This draft builds on that
  guidance and does not replace it.

## Hosted features added to the skill (November 19, 2026)

Compared against `app/mcp_server.py` on `sonilo-api-dashboard` `develop`
(`97283e57`), the tools offer these, which the skill did not explain:

- `glossary` on `generate_video_subtitles` (terms kept as written, optional
  per-language translation) and on `dubbing` (same list plus `alias` for
  pronunciation; only together with `subtitles`). Added to
  `references/dubbing.md` and two examples.
- `source_language` on `generate_video_subtitles`.
- `analyze_video` `mode` (`music`, `sfx`, `both`; same price).
- Input limits: subtitles up to 300 s with an audio track; dubbing up to
  300 s, 400 MB, shorter side at least 360 px.

Left out on purpose: `audio_ref_url` / `cover_ref_url` on `text_to_music`
(behind `T2M_REF_PARAMS_ENABLED`, off in production), and dubbing stems,
speaker or emotion detection, acting directions and custom voices (REST
only; the hosted tools have no such parameters). `check_release.py` fails if
the skill mentions those parameters or drops the glossary, source language,
mode or limit guidance.

Listing: the third bullet now mentions keeping names and terms; capability
"Subtitle review and dubbing" is now "Subtitle review, glossary and
dubbing". `docs/LISTING_COPY_1.2.0.json` carries the updated English (605
characters) and nine translations.

## Release notes

Subtitle review before dubbing now uses the hosted `generate_video_subtitles`
tool. Its availability and trial allowance are still reported under the
`proofread` service key, and the skill says so.

Videos, audio, and subtitle files on your computer can now be used directly:
the skill uploads the file to Sonilo with the hosted upload tool and then
runs the requested workflow. Uploads go only to the one-time URL Sonilo
returns, only for a file the user named, and are temporary working files.
Where the upload cannot run, the skill asks for a public HTTPS link instead.
An edited subtitle file can be uploaded the same way before dubbing.

Rules for user-supplied URLs are unchanged: public HTTPS only, and no tool
call for an unsafe URL.

## Changed files

- `plugins/sonilo/.codex-plugin/plugin.json`: version 1.2.0; the long
  description no longer says media must be public HTTPS links.
- `plugins/sonilo/skills/sonilo-workflows/SKILL.md`: subtitle routing and the
  service-key note. The "Use a local file" section comes from PR #3 unchanged.
- `references/dubbing.md`, `references/examples.md`: tool name, upload of an
  edited script, one local-file example.
- `scripts/check_release.py`: paid-tool list, a guard against routing to the
  retired name, and guards for the upload rules.
- `README.md`: feature list, example, data-sent and local-command statements.

## Validation recorded for this draft

- `python3 scripts/check_release.py` and `--live` pass.
- Codex CLI 0.162.0-alpha.2, fresh non-interactive sessions, hosted MCP only
  (the legacy local `sonilo` server removed from the test configuration):
  - Baseline with the installed 1.1.0 skill: 8 of 9 subtitle requests chose
    `generate_video_subtitles`; 1 stopped, reporting that `proofread` was not
    available.
  - With this draft, after merging PR #3: 4 of 4 subtitle requests chose
    `generate_video_subtitles`.
  - Local file, network blocked: 1 of 1 called `create_upload_url`, could not
    upload, started no generation, and asked for a public HTTPS link.
  - Local file, network allowed: 1 of 1 uploaded and then called a generation
    tool with the returned link. It chose `video_to_music` although the
    request asked for a finished video, where `video_to_video_music` is the
    documented route; one run, not investigated.
  - Private-network `http://` URL: 1 of 1 refused with no tool call.
- Every generation call in these runs was stopped by the session's approval
  policy before executing, so no task was created and nothing was charged.
  The runs establish tool selection, not finished results.

Not validated: a complete run through to a delivered result, the Codex
desktop app, ChatGPT web, the packaged ZIP, and the portal Skill scan.

## Portal draft (November 19, 2026)

Created the 1.2.0 draft with "Create draft from ZIP" from
`dist/sonilo-1.2.0.zip`, built by `scripts/build_release.py`. The upload now
rejects three things the 1.1.0 package carried or lacked, fixed in that order:

1. `.mcp.json` `scopes` ("App setup does not support these MCP settings"),
   and then any auth setting at all ("This app already has authentication
   configured. Remove the ZIP's auth override"). The portal package keeps
   only `type` and `url`; the existing app connection is reused.
2. Manifest `name` must be the package name
   `app-6a56e50ff2788191a96c7c8cd84bb6c2`; the portal package is rewritten,
   the repository keeps `sonilo` for local Codex installs.
3. "Support URL is required": added `interface.supportURL`
   (https://platform.sonilo.com), uploaded again with "Upload new version".

State after the third upload: review status "Not submitted", metadata
checks pass, the skill scan passes ("No findings with the plugin's metadata
and skills").

The "Submit for review" dialog (opened and cancelled, nothing ticked) has
only the six policy attestations and an optional, review-private
"Additional Submission Context" note. Tools are reviewed separately on the
MCPs tab (already published after the November 18 appeal), so this review
covers the listing and the skill; no test cases, demo URL or reviewer
credentials are asked for here.

Added to the manifest under `extensions["com.openai"].publication`:
`release_notes` and the nine translated descriptions (locale keys de-DE,
es-419, fr-FR, it-IT, ja-JP, ko-KR, pt-PT, zh-CN, zh-HK, from
`docs/LISTING_COPY_1.2.0.json`). Per the submission docs, imported
translations do not yet change what the directory shows. Uploaded again with
"Upload new version".

## Before submitting

- Enter `docs/LISTING_COPY_1.2.0.json` in the portal: English, nine
  translations, and the capability list. Have the translations checked.
- Tool definitions: one appeal for `dubbing` (new `glossary` parameter,
  documented 400 MB / 360 px limits, preview wording) and
  `get_generation_task` (`full_video_cost_usd` optional) was approved on
  November 18, 2026; both are published and scans run again.
- PR #477 (`97283e57`, task definition `:137`, November 19) turned
  `MCP_PREVIEW_PRICE_TO_OPENAI_CLIENTS` off. Checked in ChatGPT: reading
  task `798e7e62…` returns `trial_preview` with five fields and no
  `full_video_cost_usd`. Setting it True is the rollback.
- Reviewer notes in the portal still mention the pricing/billing-link
  disclosure from 1.1.0; replace it with a short note on what changed.
- The portal's tool justifications were written for the 15 tools of 1.1.0.
  They need entries for `generate_video_subtitles` and `create_upload_url`,
  and the `proofread` entry removed.
- The privacy and data-use answers should mention that a local file the user
  asks to process is uploaded to Sonilo.
- Check whether any of the three negative test cases expects a local file to
  be refused; that behaviour changed.
- Record one end-to-end local-file run before claiming the feature in review
  notes.

## Submission (November 19, 2026)

Submitted the 1.2.0 draft (package built from `4a37181`; no findings,
skill scan passed). Additional Submission Context, as entered:

> 1.2.0 responds to the rejection of 1.1.0 (October 21, 2026):
>
> 1. Commerce. 1.1.0 linked a balance guide whose page carried pricing and
> billing buttons, and the listing promoted balance, funds and a free preview
> of a paid result. 1.2.0 removes all of that: the skill links no pricing,
> billing or balance pages, explains credit errors without links or purchase
> steps, and reports a balance only when the user asks. On the server,
> responses to ChatGPT and Codex no longer contain billing links, "add funds"
> prompts, or the price of a full video after a free preview. The related
> tool updates were approved on appeal on November 18.
> 2. Name and description. The description is rewritten to say what the
> plugin makes, without terms-of-use style disclaimers (605 characters, down
> from 818).
>
> New in 1.2.0: files the user names on their computer are uploaded to
> Sonilo through the hosted create_upload_url tool; subtitle translation uses
> generate_video_subtitles; a glossary keeps names and terms intact in
> subtitles and dubbing; analyze_video can return a music brief, a
> sound-design brief, or both.

## Approval and publication (November 19, 2026)

The dashboard showed "1.2.0 · Approved" and "Ready to publish". Approval and
publication are separate steps: "Publish plugin" asks to confirm that 1.2.0
"will replace the currently published version 1.0.0". There is no button to
roll back to a previous version; "Unpublish plugin" removes the listing.
A problem in a published version is fixed by submitting a new one.

Keep `MCP_PREVIEW_PRICE_TO_OPENAI_CLIENTS` off on `backend-mcp`, and route any
user-facing billing text in MCP-shared code through `purchase_prompt_allowed`.

