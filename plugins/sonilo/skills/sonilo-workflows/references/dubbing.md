# Subtitle review, previews, and full videos

## Review the script before dubbing

1. For “translate the subtitles first; I will correct them,” use
   `generate_video_subtitles` only, with the glossary below when the user
   names terms to keep. Its availability and trial allowance are
   listed under the service key `proofread`. It may consume credits; it
   produces SRT files, not a dubbed video.
   Check that the service is available before submitting.
2. Return the source transcript and target-language SRT URLs actually present
   in the result. Report warnings without claiming the files are invalid
   unless the service says so. Wait for the user's review before dubbing.
3. Use the approved target-language scripts as `dubbing.subtitles`, one public
   HTTPS SRT/VTT URL per target language, with keys matching the requested
   languages exactly. Pass the same glossary again, with any aliases.
   Validate every subtitle URL as well as the video URL.
   If the user edits text in chat, do not silently reuse the unedited SRT:
   obtain a reachable URL for the approved script before submission. An
   edited `.srt` or `.vtt` saved on the user's machine can be uploaded with
   `create_upload_url`; use its `file_url` as the script URL.
4. Set `export_srt=true` only if the user wants aligned subtitles with the
   dubbed result and scripts were supplied. Deliver each language's video
   and any successful subtitle export; report a blocked export separately.

## Keep names and terms right (glossary)

Use a glossary when the user names people, brands, products, or terms that
must stay as written in translation, or must be pronounced a certain way in
the dub. Include only terms the user gave or confirmed; do not invent them.

- `generate_video_subtitles.glossary` is a list such as
  `[{"term": "Sonilo"}]`. Each term is kept exactly as written in every
  translation. Add `"language"` to limit an entry to one target language,
  and `"translation"` together with `"language"` to write the term a
  specific way in that language, for example
  `{"term": "Thom", "language": "zh_cn", "translation": "汤姆"}`.
- `dubbing.glossary` works only together with `dubbing.subtitles`, the
  approved scripts. Pass the same list and add `"alias"` where the voice
  should say a term differently, for example
  `{"term": "SQL", "alias": "sequel"}`. The returned subtitles keep the
  script's wording; only the spoken audio uses the alias.
- Without approved scripts, do not send a glossary to `dubbing`. Offer the
  subtitle-review flow below, which applies the glossary to the translation
  first.
- Follow each tool's schema for the glossary's type; do not copy parameter
  types from the local MCP server.

## Input limits

- `generate_video_subtitles`: up to 300 seconds, and the video needs an
  audio track. Pass `source_language` only when the user says which
  language is spoken or detection got it wrong; otherwise omit it.
- `dubbing`: up to 300 seconds, a file of at most 400 MB, and a shorter
  side of at least 360 px. The video URL must use https.
- When the user has already said the video breaks a limit (for example, a
  10-minute video), explain the limit before calling a tool. Otherwise
  report the service's refusal as returned; say “not charged” only when the
  response establishes it.

## Select languages and preview eligibility

- Always specify the languages the user requested; never omit this argument
  and accidentally accept the server's multiple-language default. Ask for the
  target language if missing. Dubbing is billed per language.
- Follow the hosted schema: `dubbing.languages` currently takes a JSON array
  encoded as a string (for example, `["en"]`), while
  `generate_video_subtitles.languages` takes a list. Do not copy local MCP
  parameter types or path parameters; a local file goes through
  `create_upload_url`.
- A free dubbing preview is conditional on current account eligibility, a
  single target language, and no supplied subtitles. Check
  `trial.dubbing.remaining`; never promise every user a free preview.
- The eligible first call processes up to the first 15 seconds. A free-only
  request does not authorize a normal charged call when eligibility is absent,
  exhausted, unknown, or incompatible with multiple languages or scripts.
  Explain that no free preview is available; do not silently bill instead.
- Read `trial_preview` from both submission text and the retrieved task result.
  Use `preview_seconds`, `source_duration_seconds`, and `trimmed` to label the
  actual preview. Do not say 45 seconds remain unless the source is 60 seconds.
  Never display the prices or purchase instructions in its `message` field.
- `full_video_cost_usd`, when present, describes the full source, not the
  amount charged for the preview. Quote it only if the user asks what the
  full video would cost, and do not infer the current balance from it.

## Continue after a preview

- A preview is complete for that preview task. Polling it again cannot make
  it full length. Never automatically submit a second dubbed video.
- When the user explicitly asks for the full version, reuse the original
  video URL, target language, and approved settings. Refresh account services;
  the full source is a new generation and may use existing paid credits.
  Do not promise it charges only for the remaining seconds.
- If a previous full-video task exists, retrieve it instead of starting a
  duplicate. If only the completed preview exists, the explicit full-video
  request authorizes one new submission. Stop on a credit rejection.
- If the first request was for a full video but the server returns a preview,
  deliver it accurately, say the rest of the video was not processed, and
  that the user can ask for the full version. Do not automatically make
  another charged call.
- If the user later asks to continue, apply the same task check. Do not
  promise the account covers the full video; let the service enforce billing
  on the requested task.
- Use `lipsync=false` only when requested or needed to preserve the original
  picture; use `ducking=true` when the background must lower under the dubbed
  speech. Follow current defaults otherwise.
