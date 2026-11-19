#!/usr/bin/env python3
"""Build the two release ZIPs in dist/.

- dist/sonilo-<version>.zip: the plugin package for the OpenAI Platform
  ("Create draft from ZIP"). Two rewrites, both required by the Platform
  upload (seen 2026-11-19), while the repository keeps what local Codex
  marketplace installs use:
  - manifest `name` becomes the existing plugin's package name (the repo
    keeps "sonilo": `sonilo@sonilo`, skill `sonilo:sonilo-workflows`);
  - `.mcp.json` loses its auth settings ("scopes"): the portal app already
    has its OAuth connection and rejects any auth override in the ZIP.
- dist/sonilo-workflows-<version>.zip: the skill alone, for the Platform's
  Skills section.

Neither ZIP has directory entries, matching the 1.1.0 packages.
Run scripts/check_release.py first.
"""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT / "plugins" / "sonilo"
SKILLS_ROOT = PLUGIN_ROOT / "skills"
MANIFEST = Path(".codex-plugin") / "plugin.json"
MCP_CONFIG = Path(".mcp.json")
DIST = ROOT / "dist"
PORTAL_PACKAGE_NAME = "app-6a56e50ff2788191a96c7c8cd84bb6c2"
# Fixed timestamp so the same sources always produce the same bytes.
ZIP_TIME = (2026, 1, 1, 0, 0, 0)


def _files(base: Path) -> list[Path]:
    return sorted(
        p for p in base.rglob("*")
        if p.is_file() and p.name != ".DS_Store"
    )


def _write(zf: zipfile.ZipFile, arcname: str, data: bytes) -> None:
    info = zipfile.ZipInfo(arcname, date_time=ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    zf.writestr(info, data)


def build() -> list[Path]:
    manifest = json.loads((PLUGIN_ROOT / MANIFEST).read_text(encoding="utf-8"))
    version = manifest["version"]
    DIST.mkdir(exist_ok=True)

    plugin_zip = DIST / f"sonilo-{version}.zip"
    with zipfile.ZipFile(plugin_zip, "w") as zf:
        for path in _files(PLUGIN_ROOT):
            rel = path.relative_to(PLUGIN_ROOT)
            data = path.read_bytes()
            if rel == MANIFEST:
                portal = dict(manifest, name=PORTAL_PACKAGE_NAME)
                data = (json.dumps(portal, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
            elif rel == MCP_CONFIG:
                config = json.loads(data)
                for server in config["mcpServers"].values():
                    for key in ("scopes", "extensions"):
                        server.pop(key, None)
                data = (json.dumps(config, indent=2) + "\n").encode("utf-8")
            _write(zf, rel.as_posix(), data)

    skill_zip = DIST / f"sonilo-workflows-{version}.zip"
    with zipfile.ZipFile(skill_zip, "w") as zf:
        for path in _files(SKILLS_ROOT / "sonilo-workflows"):
            _write(zf, path.relative_to(SKILLS_ROOT).as_posix(), path.read_bytes())

    return [plugin_zip, skill_zip]


def main() -> int:
    for path in build():
        print(f"built {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
