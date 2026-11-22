#!/usr/bin/env python3
"""Find the official MorpheApp/morphe-patches commit that seo-rii's
wireguard-prototype.patch was made against.

Candidates are every 40-hex string in seo-rii's README.md,
docs/wireguard-source-build.md and the README-WIREGUARD.md section of the
patch header. A candidate is accepted only if it can be fetched from the
upstream repo AND every pre-image blob id (`index <old>..<new>` lines) in the
patch matches the file at that commit. Exactly one candidate must pass,
otherwise the script exits non-zero.

Prints the accepted commit on stdout and, if GITHUB_OUTPUT is set, writes
`base_commit=<sha>` there.
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HEX40 = re.compile(r"(?<![0-9a-fA-F])[0-9a-f]{40}(?![0-9a-fA-F])")
DOC_FILES = ["README.md", "docs/wireguard-source-build.md"]
HEADER_FILE = "README-WIREGUARD.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def patch_sections(patch_text: str):
    """Yield (path, section_text) for every `diff --git` section."""
    parts = re.split(r"(?m)^(?=diff --git )", patch_text)
    for part in parts:
        m = re.match(r"diff --git a/(\S+) b/\S+", part)
        if m:
            yield m.group(1), part


def preimage_blobs(patch_text: str):
    """(path, old-blob-abbrev) for files that exist before the patch."""
    result = []
    for path, section in patch_sections(patch_text):
        header = section.split("\n@@", 1)[0]
        if re.search(r"(?m)^new file mode", header):
            continue
        m = re.search(r"(?m)^index ([0-9a-f]+)\.\.([0-9a-f]+)", header)
        if m and set(m.group(1)) != {"0"}:
            result.append((path, m.group(1)))
    return result


def git(*args, cwd=None, check=True):
    return subprocess.run(["git", *args], cwd=cwd, check=check, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seo", type=Path, required=True, help="seo-rii checkout")
    ap.add_argument("--upstream", required=True, help="official repo URL")
    ap.add_argument("--patch", default="wireguard-prototype.patch")
    args = ap.parse_args()

    patch_text = read(args.seo / args.patch).replace("\r\n", "\n")
    if not patch_text:
        sys.exit(f"ERROR: {args.seo / args.patch} not found or empty")

    texts = [read(args.seo / f) for f in DOC_FILES]
    texts += [section for path, section in patch_sections(patch_text) if path == HEADER_FILE]
    candidates = []
    for text in texts:
        for sha in HEX40.findall(text):
            if sha not in candidates:
                candidates.append(sha)
    if not candidates:
        sys.exit("ERROR: no 40-hex commit found in seo-rii docs or patch header")

    blobs = preimage_blobs(patch_text)
    if not blobs:
        sys.exit("ERROR: no pre-image blob ids in patch; cannot verify base commit")
    print(f"{len(candidates)} candidate(s), verifying against {len(blobs)} pre-image blobs",
          file=sys.stderr)

    verified = []
    with tempfile.TemporaryDirectory() as tmp:
        git("init", "--quiet", tmp)
        git("remote", "add", "origin", args.upstream, cwd=tmp)
        for sha in candidates:
            fetched = git("fetch", "--quiet", "--depth=1", "origin", sha, cwd=tmp, check=False)
            if fetched.returncode != 0:
                print(f"  {sha}: not in upstream (skipped)", file=sys.stderr)
                continue
            bad = []
            for path, old in blobs:
                r = git("rev-parse", "--verify", "--quiet", f"{sha}:{path}", cwd=tmp, check=False)
                if r.returncode != 0 or not r.stdout.strip().startswith(old):
                    bad.append(path)
            if bad:
                print(f"  {sha}: blob mismatch on {len(bad)} file(s), e.g. {bad[0]}", file=sys.stderr)
            else:
                print(f"  {sha}: all {len(blobs)} blobs match", file=sys.stderr)
                verified.append(sha)

    if len(verified) != 1:
        sys.exit(f"ERROR: expected exactly one verified base commit, found {len(verified)}: {verified}")

    sha = verified[0]
    print(sha)
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(f"base_commit={sha}\n")


if __name__ == "__main__":
    main()
