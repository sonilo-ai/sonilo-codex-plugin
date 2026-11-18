# Revision 1.2.0 draft notes

> Status — November 18, 2026: OpenAI rejected 1.1.0 on October 21, 2026
> (see "Response to the 1.1.0 rejection" below). This draft now also carries
> the fixes for that rejection. Not packaged, uploaded, or submitted.
> Version 1.0.0 remains published.

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

- `plugin.json`: long description rewritten (567 characters, was about 1,000)
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

Not fixed here (hosted server, `sonilo-api-dashboard`):

- `backend/app/services/dubbing_trial.py` puts "Translating the full video
  costs $X — add funds at <billing URL>" in `trial_preview.message`, and the
  402 hints say "or add funds to …". Reviewers testing the hosted MCP in
  ChatGPT see tool output directly, without this skill's suppression rules.
- On November 17 the daily MCP scan held a new `dubbing` tool definition
  ("needs further review before it can be published"); the earlier
  definition stays live. The portal offers "Request manual review".

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

## Before submitting

- Enter `docs/LISTING_COPY_1.2.0.json` in the portal: English, nine
  translations, and the capability list. Have the translations checked.
- Decide on the hosted server's add-funds messages (above) before
  resubmitting; the listing fix alone does not cover what reviewers see in
  ChatGPT.
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
