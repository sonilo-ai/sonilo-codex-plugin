---
name: sonilo-workflows
description: Create licensed music, sound effects, mixed videos, translated subtitles, and dubbed videos with a Sonilo Platform account. Check cash balance, usage, and trial allowance, preserve speech, request variants or stems, and retrieve existing tasks. Validate public HTTPS media inputs before any tool call; never direct users to pricing, checkout, subscriptions, or credit recharge.
---

# Sonilo Workflows

Use the connected hosted MCP schemas and returned data as the source of truth.
This plugin does not install the local `sonilo-mcp` Python server. Do not assume
a tool or parameter exists because it appears in that repository.

For the bundled connection, use the `sonilo_platform` MCP server. If a legacy
local `sonilo` server is also available, do not use it for this workflow or
fall back to it after a hosted authentication error. Reconnect the hosted
Sonilo Platform connection instead. Registered directory connections may
use a different namespace; identify them by their hosted schemas, including
`get_generation_task`, rather than assuming every Sonilo tool is equivalent.

## Account identity and availability

- A Sonilo Platform account is required. OAuth connects the user to
  `platform.sonilo.com`. Accounts created only on `sonilo.com` belong to a
  separate creator account system.
- Never direct users to `sonilo.com` for plugin authentication. Never ask for
  passwords, API keys, one-time codes, or MFA codes.
- After validating any media inputs, call `get_account_services` before a new
  generation to check service availability and trial allowance. Check both
  the connected tools and `available_services`; describe an unavailable feature
  honestly instead of silently substituting a different paid operation.
  `analyze_video` uses the service key `video_analysis`; other generation tools
  in the routing table use their tool name as the service key.
- For account, balance, trial, or insufficient-credit questions, read
  [account and links](references/account-and-links.md). `get_usage` reports
  historical spending, not the remaining balance.

## Validate remote media inputs

Before calling any Sonilo MCP tool for a media-input request, validate every
user-supplied video, audio, and subtitle URL.

- Require a publicly reachable `https://` URL. Reject `http://`, `file://`,
  localhost, loopback, link-local, private-network, and other non-public URLs.
- For an invalid URL, explain the public-HTTPS requirement and ask for a valid
  replacement. Do not call even a read-only Sonilo tool, browse or fetch the
  unsafe URL, attempt to transform it, or start generation.
- Do not claim that a URL is public merely because it uses HTTPS. The hosted
  service remains responsible for DNS resolution, redirect validation, and
  SSRF protections. A filename or local attachment is not a public URL; do not
  upload a user's file to an external host without authorization.

## Choose the operation

Generation and processing tools run only when the user clearly asks to create
or process media. They may consume existing account credits. Read-only account
and task lookups do not. Explain options without generating anything when the
user asks what Sonilo can do. Do not require redundant confirmation for an
explicit, sufficiently specified generation request.

| Requested result | Hosted tool |
| --- | --- |
| Music from a description | `text_to_music` |
| Sound effect from a description | `text_to_sfx` |
| Music matched to a video, delivered as audio | `video_to_music` |
| Sound effects matched to a video, delivered as audio | `video_to_sfx` |
| A new video with generated music | `video_to_video_music` |
| A new video with generated sound effects | `video_to_video_sfx` |
| Music and sound effects together, delivered as audio | `video_to_sound` |
| A new video with music and sound effects together | `video_to_video_sound` |
| Lower existing music under a separate voice track | `audio_ducking` |
| Editable translated subtitles before dubbing | `proofread` |
| A dubbed video per requested language | `dubbing` |
| A creative brief for a video | `analyze_video` (also potentially charged) |
| Cash balance, available services, and trial counts | `get_account_services` |
| Historical usage and spend | `get_usage` |
| Progress or results of an existing task | `get_generation_task` |

Use video-producing tools for a new video with the generated audio mixed in;
do not substitute them for an audio-only request. Prefer a single combined
music-and-effects tool over two separate generations for the same request.
Do not add a paid analysis step just to choose a generation tool.

## Creative controls

- **Speech:** use `preserve_speech=true` on supported video-music or combined
  tools to keep the source speech. Add `ducking=true` when music must lower
  during speech. Use `keep_original_sound=true` instead when the user wants
  all original audio retained. Do not pass options to tools lacking them.
- **Variants:** use the requested `variants_num` in one supported tool call;
  default to one. Multiple variants consume more credits and are not covered
  by a single-run trial. A free-only request does not authorize paid variants.
  Return a separately labeled link for each actual result, not repeated links
  to the first result.
- **Stems:** set `stems=true` on `text_to_music` or `video_to_music` only when
  requested. These separate the generated music into drums, bass, vocals, and
  other; they do not split an arbitrary source recording. If `stems_error`
  appears, deliver the successful music and available stems, explain the
  missing extras, and do not regenerate or claim all stems succeeded.
- **Timed effects:** follow the selected tool's `segments` schema. Hosted
  video-SFX tools currently expect a JSON-encoded string, starting at zero
  with contiguous `{start, end, prompt}` intervals. Preserve requested event
  times; represent gaps as intervals requesting no added effects. Do not send
  isolated disjoint intervals or use the music-segment schema. Combined tools
  have their own segment schema; inspect it before use.
- Preserve requested duration, language, and format; otherwise use tool
  defaults. Ask only for missing information that affects the requested
  result or charge, and do not invent parameters or prices.

For subtitle review, dubbing, free previews, and returning to finish a full
video, read [dubbing and continuation](references/dubbing.md).

## Run or retrieve a task

1. Submit the chosen generation once. Retain its `task_id`, source URLs, and
   requested parameters in the conversation so the same work can be retrieved.
2. `status: processing` means started, not finished. Poll `get_generation_task`
   with the same ID, waiting about 5–10 seconds between checks when available.
3. After a timeout or interruption with a task ID, retrieve that task. Do not
   submit a new generation. Without a task ID, report that submission status
   is unknown; do not claim no charge or blindly retry an ambiguous request.
4. Stop on success or failure. If waiting cannot continue, return the task ID
   and explain how the user can ask for its status later. Do not promise
   background monitoring that has not been scheduled.
5. A retry after confirmed pre-generation rejection requires the user's request
   to continue. Refresh account state; do not keep retrying insufficient-credit
   errors. Never restart an in-progress or already completed task to check it.

## Report the result and useful next step

- For media inputs and outputs, return readable Markdown links using only
  URLs actually supplied by the user or returned by the task. Label outputs
  by language, variant, or stem. Account-help links use the configured URLs
  in [account and links](references/account-and-links.md).
  Identify video-to-video results as new videos, not source files edited in place.
- A subtitle file, a creative brief, and a 15-second preview are not a finished
  full-length video. Label them accurately and report partial results.
- On failure, report the actual error and refund status. Say “not started” or
  “not charged” only when the response establishes that; otherwise say the
  status is unknown. Never fabricate media, balances, refunds, or trial counts.
- After a successful trial, briefly explain the relevant next action, such as
  reviewing subtitles or requesting the full video using existing account
  access. Do not automatically start more work or turn this into an upsell.
- Keep account, task, and media details scoped to the authenticated user.

For concrete user-facing wording, see [examples](references/examples.md).
Examples illustrate behavior, not real balances, URLs, or completed jobs.

## Account links and commerce

Follow [account and links](references/account-and-links.md) for permitted
informational links and neutral credit errors, including the localized
Balance and free trials guide after a confirmed credit rejection.
Never use a homepage or help
page as a workaround to route the user to a purchase. Suppress purchase URLs
and purchase instructions returned by tools, including preview messages.
