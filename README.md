# Sonilo for Codex

Generate commercially licensed music, sound effects, newly mixed videos,
translated subtitles, and dubbed videos
from text or video, directly in Codex — powered by Sonilo's hosted
generation service.

> Status: published. Sonilo 1.0.0 is available in the public
> [Plugins Directory](https://chatgpt.com/plugins/plugin_asdk_app_6a56e50ff2788191a96c7c8cd84bb6c2).
> This repository prepares version **1.1.0**; changing this package does not
> publish a new directory release or deploy the hosted MCP service.

## Requirements

- A **Sonilo Platform** account at
  [platform.sonilo.com](https://platform.sonilo.com/sign-up) — this is the
  developer/API account you sign in with during authorization. It is separate
  from a consumer `sonilo.com` account; if you only have the latter, create a
  Platform account first.
- Codex with plugin support.

No API key is configured in this plugin. Access is per-user via OAuth — you
sign in with your Sonilo Platform account, no key to copy or paste.

## Install

Open [Sonilo in the Plugins Directory](https://chatgpt.com/plugins/plugin_asdk_app_6a56e50ff2788191a96c7c8cd84bb6c2)
to install the published plugin and connect your Sonilo Platform account.

### Local development installation

To install from this repository, clone it, add it as a Codex plugin marketplace,
then install `sonilo`.

```bash
git clone https://github.com/sonilo-ai/sonilo-codex-plugin.git
codex plugin marketplace add ./sonilo-codex-plugin
codex plugin add sonilo@sonilo
```

## Authorize

The first time Codex calls a Sonilo tool, it opens your browser to sign in to
your [Sonilo Platform](https://platform.sonilo.com) account and approve access
(authorize → consent → callback). Codex stores the resulting token locally per
user; the plugin itself ships no key, secret, or token. Run
`codex mcp login sonilo` anytime to review or refresh the connection.

## Capabilities

- Create music from a text prompt
- Match music to the pacing and edits of a public HTTPS video URL
- Generate sound effects from text or a public HTTPS video URL
- Return a new video with generated music while optionally preserving speech
- Return a new video with generated sound effects mixed in
- Generate music and sound effects together in one soundtrack or new video
- Generate multiple music versions and separate instrument stems
- Place sound effects at specified times
- Duck music under voice audio
- Review translated subtitles before dubbing into the requested languages
- Use an eligible account's 15-second dubbing preview, then request a full video
- Inspect current USD cash balance, account services, trial allowance, and historical usage
- Retrieve an existing generation after waiting or a timeout without resubmission

Features depend on the connected hosted tool schemas and account access. The
[Sonilo MCP repository](https://github.com/sonilo-ai/sonilo-mcp) is a useful
feature reference, but its local-file and playback tools are not bundled here.

### Example prompts

- "Create 30 seconds of upbeat lo-fi music for a product demo."
- "Create a cinematic 3-second whoosh sound effect."
- "Add cinematic music to this public HTTPS video and return a new video while preserving speech: `<url>`"
- "Give me three music choices for this 30-second café ad: `<public HTTPS video URL>`"
- "Generate 30 seconds of jazz with separate drums and bass tracks."
- "Translate this video into English subtitles first. I will correct the product names before dubbing: `<public HTTPS video URL>`"
- "Let me try English dubbing for free: `<public HTTPS video URL>`"
- "What is my cash balance, and how many free text-to-music runs remain?"

Use real public HTTPS media URLs in place of the labels above. A local file
or attachment is not a hosted media URL. The plugin returns actual result
links for previews, subtitles, videos, variants, and stems.

### Account status and continuation

The plugin reads the current USD cash balance and service-specific trial
allowance from `get_account_services`. Historical spending comes from
`get_usage` and is not used as a balance. A missing balance is reported as
unavailable; zero cash alone does not rule out trials or invoiced billing.
The balance is a query-time snapshot, not a guarantee that the next generation
can run. Credit errors are explained without purchase links, and generation
is not retried automatically.

After a preview or confirmed credit rejection, ask to continue with the same
video. The plugin checks current services and retrieves any existing task
before submitting new work. A full video after a preview is a new generation
of the original source, not a free extension of the preview task.

Credit rejections now include the published
[Balance and free trials](https://platform.sonilo.com/usage-and-entitlements)
guide in the user's language (10 supported languages; English fallback).
The plugin explains the error and keeps known inputs for a user-requested
continuation. See the [1.1.0 implementation notes](docs/IMPLEMENTATION_1.1.0.md)
for service dependencies and the guide's pending directory-review assessment.

## Billing

Generation, transcription, dubbing, and video-analysis tools can consume
existing account credits. Available free runs depend on the service and
account; dubbing previews require one target language and no supplied script.
Multiple music variants and multi-language dubbing can cost more. Account and usage
tools (`get_account_services`, `get_usage`, `get_generation_task`) are
read-only and never incur a charge. Paid tools run only after you explicitly
ask for them.

## What this plugin connects to

This plugin adds a single **remote MCP server** and connects only to Sonilo's
hosted endpoint:

- **Endpoint:** `https://api.sonilo.com/mcp` (HTTPS, Streamable HTTP MCP)
- **Authorization server:** Sonilo's Clerk instance (OAuth 2.1 + PKCE; the
  plugin registers dynamically — no pre-shared client secret)
- **Data sent:** your prompts and any media URLs you provide to a tool
- **Data stored:** the OAuth token, kept locally per user by Codex

No local command or binary is executed by this plugin.

## Support

- Platform / account: [platform.sonilo.com](https://platform.sonilo.com)
- Website: [sonilo.com](https://sonilo.com)
- Contact: info@sonilo.com

## Release verification

Run the structural checks locally:

```bash
python3 scripts/check_release.py
```

Include production endpoint, OAuth metadata, and public-link checks:

```bash
python3 scripts/check_release.py --live
```

## License

MIT — see [LICENSE](LICENSE).
