# Revision 1.2.0 draft notes

> Status — October 9, 2026: prepared locally on `codex/plugin-v1.2.0`. Not
> committed, packaged, uploaded, or submitted. Version 1.1.0 is still in
> review and has not been cancelled.

## Why

Two hosted tool changes landed after 1.1.0 was submitted:

- The subtitle tool is now listed as `generate_video_subtitles`. The name
  `proofread` is no longer in the hosted tool list, and OpenAI's scan no
  longer shows it. The 1.1.0 skill still routes to `proofread`.
- `create_upload_url` lets the hosted server take a file from the user's
  machine. The 1.1.0 skill tells the model that a local file cannot be used.

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
- `plugins/sonilo/skills/sonilo-workflows/SKILL.md`: routing table, service-key
  note, new "Use a file from the user's machine" section.
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
  - With this draft: 6 of 6 subtitle requests chose `generate_video_subtitles`.
  - Local file, network blocked: 2 of 2 called `create_upload_url`, could not
    upload, started no generation, and asked for a public HTTPS link.
  - Local file, network allowed: 1 of 1 uploaded (PUT 200) and then called
    `video_to_video_music` with the returned link.
  - Private-network `http://` URL: 1 of 1 refused with no tool call.
- Every generation call in these runs was stopped by the session's approval
  policy before executing, so no task was created and nothing was charged.
  The runs establish tool selection, not finished results.

Not validated: a complete run through to a delivered result, the Codex
desktop app, ChatGPT web, the packaged ZIP, and the portal Skill scan.

## Before submitting

- The long description changed. The nine portal translations and
  `docs/LISTING_COPY_1.1.0.json` still carry the old sentence.
- The portal's tool justifications were written for the 15 tools of 1.1.0.
  They need entries for `generate_video_subtitles` and `create_upload_url`,
  and the `proofread` entry removed.
- The privacy and data-use answers should mention that a local file the user
  asks to process is uploaded to Sonilo.
- Check whether any of the three negative test cases expects a local file to
  be refused; that behaviour changed.
- Record one end-to-end local-file run before claiming the feature in review
  notes.
