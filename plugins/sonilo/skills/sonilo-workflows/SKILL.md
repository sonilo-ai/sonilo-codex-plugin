---
name: sonilo-workflows
description: Use Sonilo safely with a Sonilo Platform account for licensed music, sound effects, video-aware audio, newly mixed videos, audio ducking, account usage, and asynchronous generation-task retrieval. Validate public HTTPS media inputs before any tool call, use read-only account tools directly, start paid generation only for explicit creation or processing requests, and never direct users to pricing, checkout, subscriptions, or credit recharge.
---

# Sonilo Workflows

Use the Sonilo MCP tools as the source of truth for current parameters and results.

## Account identity

- This plugin authenticates against Sonilo Platform at `platform.sonilo.com`
  through OAuth. A Sonilo Platform account is required.
- Accounts created only on `sonilo.com` belong to a separate creator account
  system and cannot be used to authenticate this plugin.
- Never direct users to `sonilo.com` for plugin authentication or account
  access. Never request a password, API key, one-time code, or MFA code.

## Choose the operation

- Call `get_account_services`, `get_usage`, or `get_generation_task` directly for read-only requests.
- Call `text_to_music`, `text_to_sfx`, `video_to_music`, `video_to_sfx`, `video_to_video_music`, `video_to_video_sfx`, or `audio_ducking` only when the user clearly asks to create or process media. These operations may consume credits already present in the authenticated Sonilo Platform account.
- Use `video_to_music` or `video_to_sfx` when the user wants a generated audio track based on a video. Use `video_to_video_music` or `video_to_video_sfx` only when the user asks for a new video with the generated audio mixed in. Do not substitute a video-producing tool for an audio-only request.
- Set `preserve_speech` for `video_to_video_music` when the user asks to keep speech in the returned video. Set `isolate_vocals` for `video_to_music` when the user asks to separate the source video's vocals and mix them with the generated music. Otherwise follow the current tool defaults.
- Clarify an exploratory or ambiguous request before starting a paid operation. Do not require redundant confirmation when the user has already requested generation and supplied enough information.
- Follow the current tool input schema. Do not invent local paths, public URLs, task IDs, output URLs, prices, or unsupported parameters.

## Validate remote media inputs

Before calling any Sonilo MCP tool for a media-input request, validate the
user-supplied video or audio URL.

- Require a publicly reachable `https://` URL. Reject `http://`, `file://`,
  localhost, loopback, link-local, private-network, and other non-public URLs.
- For an invalid URL, explain the public-HTTPS requirement and ask for a valid
  replacement. Do not call even a read-only Sonilo tool, browse or fetch the
  unsafe URL, attempt to transform it, or start generation.
- Do not claim that a URL is public merely because it uses HTTPS. The hosted
  Sonilo service remains responsible for DNS resolution, redirect validation,
  and SSRF protections when a valid-looking public URL is submitted.

## Run a paid asynchronous operation

1. Select the narrowest generation or processing tool that matches the request.
2. Preserve the user's creative intent and requested duration or format. Prefer the tool's default output format unless the user asks for another supported format.
3. Call the paid tool once and retain its returned `task_id`.
4. Treat `status: processing` only as acknowledgement that generation started.
5. Poll `get_generation_task` with the same `task_id`, waiting about 5–10 seconds between checks when waiting is available. Avoid tight polling loops.
6. Stop when the task succeeds or fails. If continued waiting is unavailable, report that processing is still underway and include the `task_id` for a later check.

## Keep purchases outside the plugin

- Do not provide or direct users to pricing, checkout, subscription, credit
  purchase, recharge, or top-up pages. Do not add a purchase call to action.
- If a user asks where to buy credits or subscribe, respond only that purchasing
  or recharging Sonilo credits is not available through this plugin. Do not
  provide a purchase URL, name an external purchase destination, tell the user
  to visit a website, account, billing, or pricing page, or suggest a workaround.
- If a tool reports insufficient credits or includes a purchase URL, report the
  insufficient-credit error neutrally and do not repeat or paraphrase the URL.
- The Sonilo Platform homepage may be shared only when the user asks for
  developer product information, Platform account sign-in, support, privacy,
  or legal information, but never as a route to purchase.
- Do not share `sonilo.com` as an authentication or account-access destination
  because its creator accounts are not accepted by this plugin.
- Explicit generation requests may consume credits already present in the
  authenticated user's Sonilo Platform account; this existing-credit usage is
  not a purchase flow.

## Report the result

- On success, return only media URLs and metadata actually present in the task result. For video-to-video operations, identify the returned URL as a newly mixed video; never claim that Sonilo modified the source video in place.
- On failure, report the provided error and refund status without claiming that media was created.
- Never describe a processing task as finished or fabricate a playable artifact.
- Keep account, usage, task, and media details scoped to the authenticated Sonilo Platform user.
