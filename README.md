# Sonilo for Codex

Generate licensed music, sound effects, and newly mixed videos from text or publicly reachable HTTPS video URLs in Codex.

> Status: publication development. The plugin is installable locally, but it
> is not yet listed in the public Plugins Directory.

## Install

Clone this repository, add it as a Codex plugin marketplace, then install `sonilo`.

```bash
git clone https://github.com/sonilo-ai/sonilo-codex-plugin.git
codex plugin marketplace add ./sonilo-codex-plugin
codex plugin add sonilo@sonilo
```

## Configure

The plugin connects to Sonilo's production MCP endpoint at
`https://api.sonilo.com/mcp`. Codex guides each user through Sonilo Platform
OAuth. A `platform.sonilo.com` account is required; accounts created only on
`sonilo.com` are separate and cannot be used with this plugin. No API key is
embedded in this plugin.

## Capabilities

- Create music from a text prompt
- Match music to the pacing and edits of a public HTTPS video URL
- Generate sound effects from text or a public HTTPS video URL
- Return a new video with generated music while optionally preserving speech
- Return a new video with generated sound effects mixed in
- Duck music under voice audio
- Inspect Sonilo Platform account services and usage

Generation can consume credits already available in the connected Sonilo
Platform account. See the [Sonilo MCP server](https://github.com/sonilo-ai/sonilo-mcp)
for tool details and limits.

## Security

This plugin never includes an API key. The hosted service uses an OAuth access
token scoped to the connected Sonilo Platform account.

## Release verification

Run the structural checks locally:

```bash
python3 scripts/check_release.py
```

Include production endpoint, OAuth metadata, and public-link checks:

```bash
python3 scripts/check_release.py --live
```
