#!/usr/bin/env python3
"""Validate the Sonilo Codex plugin package and optional production surfaces."""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
import urllib.error
import urllib.request
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT / "plugins" / "sonilo"
MANIFEST_PATH = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
MCP_PATH = PLUGIN_ROOT / ".mcp.json"
WORKFLOW_SKILL_PATH = PLUGIN_ROOT / "skills" / "sonilo-workflows" / "SKILL.md"
WORKFLOW_AGENT_PATH = PLUGIN_ROOT / "skills" / "sonilo-workflows" / "agents" / "openai.yaml"
MARKETPLACE_PATH = ROOT / ".agents" / "plugins" / "marketplace.json"
MCP_URL = "https://api.sonilo.com/mcp"
RESOURCE_METADATA_URL = f"{MCP_URL}/.well-known/oauth-protected-resource"
RFC_RESOURCE_METADATA_URL = "https://api.sonilo.com/.well-known/oauth-protected-resource/mcp"
AUTHORIZATION_SERVER = "https://clerk.platform.sonilo.com/"
PAID_TOOL_NAMES = {
    "text_to_music",
    "text_to_sfx",
    "video_to_music",
    "video_to_sfx",
    "video_to_video_music",
    "video_to_video_sfx",
    "audio_ducking",
}


class CheckFailure(RuntimeError):
    """Raised when a release invariant is not satisfied."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def load_json(path: Path) -> dict:
    require(path.is_file(), f"missing file: {path.relative_to(ROOT)}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CheckFailure(f"invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc


def paeth_predictor(left: int, above: int, upper_left: int) -> int:
    estimate = left + above - upper_left
    left_distance = abs(estimate - left)
    above_distance = abs(estimate - above)
    upper_left_distance = abs(estimate - upper_left)
    if left_distance <= above_distance and left_distance <= upper_left_distance:
        return left
    if above_distance <= upper_left_distance:
        return above
    return upper_left


def check_opaque_white_png(path: Path, *, require_square: bool = False) -> None:
    """Verify an RGB8 PNG has no transparency and a pure-white outer background."""
    data = path.read_bytes()
    require(data.startswith(b"\x89PNG\r\n\x1a\n"), f"{path.relative_to(ROOT)} is not a PNG")

    offset = 8
    header: tuple[int, int, int, int, int] | None = None
    compressed = bytearray()
    has_transparency_chunk = False
    while offset + 12 <= len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_type = data[offset + 4 : offset + 8]
        chunk_data = data[offset + 8 : offset + 8 + length]
        require(len(chunk_data) == length, f"truncated PNG chunk in {path.relative_to(ROOT)}")
        offset += 12 + length
        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, compression, filtering, interlace = struct.unpack(
                ">IIBBBBB", chunk_data
            )
            require(compression == 0 and filtering == 0, f"unsupported PNG encoding in {path.relative_to(ROOT)}")
            require(interlace == 0, f"interlaced PNG is not allowed: {path.relative_to(ROOT)}")
            header = (width, height, bit_depth, color_type, interlace)
        elif chunk_type == b"IDAT":
            compressed.extend(chunk_data)
        elif chunk_type == b"tRNS":
            has_transparency_chunk = True
        elif chunk_type == b"IEND":
            break

    require(header is not None, f"missing PNG header: {path.relative_to(ROOT)}")
    width, height, bit_depth, color_type, _ = header
    require(width > 0 and height > 0, f"invalid PNG dimensions: {path.relative_to(ROOT)}")
    if require_square:
        require(width == height, f"plugin icon must be square: {path.relative_to(ROOT)}")
    require(bit_depth == 8 and color_type == 2, f"PNG must be opaque RGB8: {path.relative_to(ROOT)}")
    require(not has_transparency_chunk, f"PNG must not contain transparency: {path.relative_to(ROOT)}")

    bytes_per_pixel = 3
    stride = width * bytes_per_pixel
    scanlines = zlib.decompress(bytes(compressed))
    require(
        len(scanlines) == (stride + 1) * height,
        f"unexpected PNG pixel data size: {path.relative_to(ROOT)}",
    )

    previous = bytearray(stride)
    corner_pixels: list[bytes] = []
    position = 0
    for row_index in range(height):
        filter_type = scanlines[position]
        position += 1
        encoded = scanlines[position : position + stride]
        position += stride
        decoded = bytearray(stride)
        for index, value in enumerate(encoded):
            left = decoded[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
            above = previous[index]
            upper_left = previous[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
            if filter_type == 0:
                prediction = 0
            elif filter_type == 1:
                prediction = left
            elif filter_type == 2:
                prediction = above
            elif filter_type == 3:
                prediction = (left + above) // 2
            elif filter_type == 4:
                prediction = paeth_predictor(left, above, upper_left)
            else:
                raise CheckFailure(f"unsupported PNG filter in {path.relative_to(ROOT)}")
            decoded[index] = (value + prediction) & 0xFF
        if row_index in (0, height - 1):
            corner_pixels.extend((bytes(decoded[:3]), bytes(decoded[-3:])))
        previous = decoded

    require(
        corner_pixels == [b"\xff\xff\xff"] * 4,
        f"PNG corners must be pure white: {path.relative_to(ROOT)}",
    )


def check_local() -> None:
    manifest = load_json(MANIFEST_PATH)
    mcp_config = load_json(MCP_PATH)
    marketplace = load_json(MARKETPLACE_PATH)

    require(manifest.get("name") == "sonilo", "manifest name must be sonilo")
    require(
        re.fullmatch(r"\d+\.\d+\.\d+", manifest.get("version", "")) is not None,
        "manifest version must be a plain semver string",
    )
    require(manifest.get("skills") == "./skills/", "manifest must reference bundled skills")
    require(manifest.get("mcpServers") == "./.mcp.json", "manifest must reference .mcp.json")
    require(WORKFLOW_SKILL_PATH.is_file(), "bundled sonilo-workflows skill is missing")
    require(WORKFLOW_AGENT_PATH.is_file(), "bundled sonilo-workflows agent metadata is missing")
    sonilo_mcp = mcp_config.get("mcpServers", {}).get("sonilo", {})
    require(sonilo_mcp.get("type") == "http", "MCP transport type must be http")
    require(sonilo_mcp.get("url") == MCP_URL, f"MCP URL must be {MCP_URL}")
    require(sonilo_mcp.get("scopes") == ["profile"], "MCP OAuth scope must be limited to profile")
    require(
        set(sonilo_mcp) == {"type", "url", "scopes"},
        "MCP config must contain only the endpoint and least-privilege OAuth scope",
    )

    author = manifest.get("author", {})
    require(author.get("name") == "Sonilo", "public author name must be Sonilo")
    require(author.get("email") == "support@sonilo.com", "support email is missing")
    require(author.get("url") == "https://platform.sonilo.com", "author URL must use Sonilo Platform")
    require(manifest.get("homepage") == "https://platform.sonilo.com", "homepage must use Sonilo Platform")

    interface = manifest.get("interface", {})
    require(interface.get("shortDescription") == "Create music and sound effects", "portal subtitle is out of sync")
    require(len(interface["shortDescription"]) <= 30, "portal subtitle exceeds 30 characters")
    default_prompts = interface.get("defaultPrompt")
    require(
        isinstance(default_prompts, list) and len(default_prompts) == 3,
        "manifest must contain exactly three starter prompts",
    )
    require(
        all(isinstance(prompt, str) and prompt.strip() for prompt in default_prompts),
        "manifest starter prompts must be non-empty strings",
    )
    require(interface.get("category") == "Creativity", "plugin category must be Creativity")
    require(interface.get("developerName") == "Sonilo", "public developer name must be Sonilo")
    require(
        "Sonilo Platform account" in interface.get("longDescription", ""),
        "long description must name the required Sonilo Platform account",
    )
    require(
        "Sonilo.com creator accounts are separate" in interface.get("longDescription", ""),
        "long description must disclose the separate creator account system",
    )
    require(
        "newly mixed videos" in interface.get("longDescription", ""),
        "long description must describe the video-to-video workflows",
    )
    capabilities = set(interface.get("capabilities", []))
    require("Video soundtrack generation" in capabilities, "video soundtrack capability is missing")
    require("Video sound-effect generation" in capabilities, "video sound-effect capability is missing")
    expected_urls = {
        "websiteURL": "https://platform.sonilo.com",
        "privacyPolicyURL": "https://sonilo.com/privacy-policy",
        "termsOfServiceURL": "https://sonilo.com/terms-of-service",
    }
    for field, expected in expected_urls.items():
        require(interface.get(field) == expected, f"{field} must be {expected}")

    for field in ("composerIcon", "logo"):
        relative_path = interface.get(field)
        require(
            isinstance(relative_path, str) and relative_path.startswith("./"),
            f"{field} must use a ./ path",
        )
        asset_path = PLUGIN_ROOT / relative_path[2:]
        require(asset_path.is_file(), f"missing {field}: {relative_path}")
        check_opaque_white_png(asset_path, require_square=field == "composerIcon")

    skill = WORKFLOW_SKILL_PATH.read_text(encoding="utf-8")
    require(skill.startswith("---\nname: sonilo-workflows\n"), "skill frontmatter is invalid")
    require(
        "Validate public HTTPS media inputs before any tool call" in skill,
        "skill metadata must advertise media-input validation",
    )
    require(
        "never direct users to pricing, checkout, subscriptions, or credit recharge" in skill,
        "skill metadata must advertise the no-commerce boundary",
    )
    require("only when the user clearly asks" in skill, "skill must guard paid operations")
    for tool_name in PAID_TOOL_NAMES:
        require(f"`{tool_name}`" in skill, f"skill is missing paid tool guidance for {tool_name}")
    require(
        "new video with the generated audio mixed in" in skill,
        "skill must distinguish video-producing tools from audio-only tools",
    )
    require("`preserve_speech`" in skill, "skill must document speech preservation routing")
    require("`isolate_vocals`" in skill, "skill must document vocal-isolation routing")
    require("A Sonilo Platform account is required" in skill, "skill must state the required account system")
    require(
        "Accounts created only on `sonilo.com`" in skill,
        "skill must disclose that sonilo.com accounts are separate",
    )
    require(
        "Never direct users to `sonilo.com` for plugin authentication" in skill,
        "skill must not route authentication to the wrong account system",
    )
    require(
        "Before calling any Sonilo MCP tool for a media-input request" in skill,
        "skill must validate remote media before any MCP call",
    )
    require(
        "Do not call even a read-only Sonilo tool" in skill,
        "skill must reject unsafe media URLs without account lookups",
    )
    require(
        "Do not provide or direct users to pricing, checkout, subscription, credit" in skill,
        "skill must not direct users to purchase or recharge",
    )
    require(
        "do not repeat or paraphrase the URL" in skill,
        "skill must suppress purchase URLs returned by tools",
    )
    require(
        "to visit a website, account, billing, or pricing page" in skill,
        "skill must not indirectly route users to purchase destinations",
    )
    require("Poll `get_generation_task`" in skill, "skill must document asynchronous polling")
    agent_metadata = WORKFLOW_AGENT_PATH.read_text(encoding="utf-8")
    require('value: "sonilo"' in agent_metadata, "skill agent metadata must depend on Sonilo MCP")
    require(f'url: "{MCP_URL}"' in agent_metadata, "skill agent metadata has the wrong MCP URL")

    entries = marketplace.get("plugins", [])
    entry = next((item for item in entries if item.get("name") == "sonilo"), None)
    require(entry is not None, "marketplace is missing the sonilo entry")
    require(entry.get("source", {}).get("path") == "./plugins/sonilo", "marketplace source path is wrong")
    require(entry.get("policy", {}).get("installation") == "AVAILABLE", "installation policy must be AVAILABLE")
    require(entry.get("policy", {}).get("authentication") == "ON_INSTALL", "authentication policy must be ON_INSTALL")
    require(entry.get("category") == "Creativity", "marketplace category must be Creativity")


def request(url: str, *, method: str = "GET") -> tuple[int, dict[str, str], bytes]:
    req = urllib.request.Request(
        url,
        method=method,
        headers={"Accept": "application/json", "User-Agent": "sonilo-plugin-release-check/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            headers = {name.lower(): value for name, value in response.headers.items()}
            return response.status, headers, response.read()
    except urllib.error.HTTPError as exc:
        headers = {name.lower(): value for name, value in exc.headers.items()}
        return exc.code, headers, exc.read()
    except urllib.error.URLError as exc:
        raise CheckFailure(f"could not reach {url}: {exc.reason}") from exc


def check_live() -> None:
    status, headers, _ = request(MCP_URL)
    require(status == 401, f"unauthenticated MCP request returned {status}, expected 401")
    challenge = headers.get("www-authenticate", "")
    require("Bearer" in challenge, "MCP response is missing the Bearer challenge")
    require(RESOURCE_METADATA_URL in challenge, "MCP challenge points at the wrong resource metadata URL")

    def validate_resource_metadata(metadata_url: str, body: bytes) -> None:
        try:
            metadata = json.loads(body)
        except json.JSONDecodeError as exc:
            raise CheckFailure(f"resource metadata at {metadata_url} is not valid JSON") from exc
        require(metadata.get("resource") == MCP_URL, "resource metadata contains the wrong resource")
        require(AUTHORIZATION_SERVER in metadata.get("authorization_servers", []), "authorization server is missing")
        require("profile" in metadata.get("scopes_supported", []), "profile scope is missing")
        require("header" in metadata.get("bearer_methods_supported", []), "header bearer method is missing")

    status, _, body = request(RESOURCE_METADATA_URL)
    require(status == 200, f"resource metadata at {RESOURCE_METADATA_URL} returned {status}, expected 200")
    validate_resource_metadata(RESOURCE_METADATA_URL, body)

    status, _, body = request(RFC_RESOURCE_METADATA_URL)
    require(
        status == 200,
        f"RFC discovery fallback at {RFC_RESOURCE_METADATA_URL} returned {status}, expected 200",
    )
    validate_resource_metadata(RFC_RESOURCE_METADATA_URL, body)

    manifest = load_json(MANIFEST_PATH)
    interface = manifest["interface"]
    for field in ("websiteURL", "privacyPolicyURL", "termsOfServiceURL"):
        status, _, _ = request(interface[field])
        require(status == 200, f"{field} returned {status}, expected 200")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="also check production HTTP and OAuth metadata")
    args = parser.parse_args()

    try:
        check_local()
        if args.live:
            check_live()
    except CheckFailure as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    scope = "local and live" if args.live else "local"
    print(f"PASS: Sonilo release checks ({scope})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
