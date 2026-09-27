#!/usr/bin/env python3
"""Pin the newest published stable and nightly Linux AppImages."""

import base64
import json
import re
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "releases.json"
API = "https://api.github.com/repos/pingdotgg/t3code/releases"
NIGHTLY = re.compile(r"^v\d+\.\d+\.\d+-nightly\.\d{8}\.\d+$")
STABLE = re.compile(r"^v\d+\.\d+\.\d+$")
ASSETS = {"x86_64-linux": "x86_64", "aarch64-linux": "arm64"}


def get_json(url):
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "t3code-nix-flake-updater",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def release_data(release):
    tag = release["tag_name"]
    version = tag.removeprefix("v")
    assets = {asset["name"]: asset for asset in release["assets"]}
    hashes = {}
    for system, arch in ASSETS.items():
        filename = f"T3-Code-{version}-{arch}.AppImage"
        asset = assets.get(filename)
        if asset is None:
            raise ValueError(f"{tag}: missing {filename}")
        digest = asset.get("digest") or ""
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
            raise ValueError(f"{tag}: missing SHA-256 digest for {filename}")
        hashes[system] = "sha256-" + base64.b64encode(
            bytes.fromhex(digest.removeprefix("sha256:"))
        ).decode("ascii")
    return {"tag": tag, "version": version, "hashes": hashes}


def latest_nightly(releases):
    candidates = [
        release for release in releases
        if not release["draft"] and NIGHTLY.fullmatch(release["tag_name"])
    ]
    if not candidates:
        raise ValueError("No published nightly release found")
    return max(candidates, key=lambda release: release["published_at"])


def main():
    stable = get_json(API + "/latest")
    if not STABLE.fullmatch(stable["tag_name"]):
        raise ValueError("GitHub's latest release is not a stable T3 Code release")
    releases = get_json(API + "?per_page=100")
    data = {
        "stable": release_data(stable),
        "nightly": release_data(latest_nightly(releases)),
    }
    updated = json.dumps(data, indent=2) + "\n"
    if not OUTPUT.exists() or OUTPUT.read_text() != updated:
        OUTPUT.write_text(updated)
        print("Updated releases.json")
    else:
        print("Already current")


if __name__ == "__main__":
    main()
