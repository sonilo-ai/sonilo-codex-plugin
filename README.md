# Sonilo for Codex

Generate licensed music, sound effects, and newly mixed videos from text or publicly reachable HTTPS video URLs in Codex.

> Status: publication development. The plugin is installable locally, but it
> is not yet listed in the public Plugins Directory.

## Requirements

- A **Sonilo Platform** account at
  [platform.sonilo.com](https://platform.sonilo.com) — this is the
  developer/API account you sign in with during authorization. It is separate
  from a consumer `sonilo.com` account; if you only have the latter, create a
  Platform account first.
- Codex with plugin support.

No API key is configured in this plugin. Access is per-user via OAuth — you
sign in with your Sonilo Platform account, no key to copy or paste.

## Install

Clone this repository, add it as a Codex plugin marketplace, then install `sonilo`.

```bash
git clone https://github.com/sonilo-ai/sonilo-codex-plugin.git
codex plugin marketplace add ./sonilo-codex-plugin
codex plugin add sonilo@sonilo
```

## Authorize

The first time Codex calls a Sonilo tool, it opens your browser to sign in to
your [Sonilo Platform](https://platform.sonilo.com) account and approve access
(authorize → consent → callback). Codex stores the resulting OAuth token
locally per user, limited to the `profile` scope; the plugin itself ships no
key, secret, or token. Run `codex mcp login sonilo` to (re)authorize, for
example after switching accounts or clearing local state.

## Capabilities

- Create music from a text prompt
- Match music to the pacing and edits of a public HTTPS video URL
- Generate sound effects from text or a public HTTPS video URL
- Return a new video with generated music while optionally preserving speech
- Return a new video with generated sound effects mixed in
- Duck music under voice audio
- Inspect Sonilo Platform account services and usage

See the [Sonilo MCP server](https://github.com/sonilo-ai/sonilo-mcp) for tool
details and limits.

### Example prompts

- "Create 30 seconds of upbeat lo-fi music for a product demo."
- "Create a cinematic 3-second whoosh sound effect."
- "Add cinematic music to this public HTTPS video and return a new video while preserving speech: `<url>`"

## Billing

Generation tools (`text_to_music`, `text_to_sfx`, `video_to_music`,
`video_to_sfx`, `video_to_video_music`, `video_to_video_sfx`, `audio_ducking`)
are **paid** and consume credits already available in your Sonilo Platform
account. Account and usage tools (`get_account_services`, `get_usage`,
`get_generation_task`) are read-only and never incur a charge. Paid tools run
only after you explicitly ask for them, and the plugin never directs you to
pricing, checkout, or credit-purchase pages.

## What this plugin connects to

This plugin adds a single **remote MCP server** and connects only to Sonilo's
hosted endpoint:

- **Endpoint:** `https://api.sonilo.com/mcp` (HTTPS, Streamable HTTP MCP)
- **Authorization:** OAuth against Sonilo Platform's identity provider,
  limited to the `profile` scope — no pre-shared client secret
- **Data sent:** your prompts and any media URLs you provide to a tool
- **Data stored:** the OAuth token, kept locally per user by Codex

No local command or binary is executed by this plugin.

## Support

- Platform / account: [platform.sonilo.com](https://platform.sonilo.com)
- Website: [sonilo.com](https://sonilo.com)
- Contact: support@sonilo.com

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
