"""Keep only YouTube Music (and universal) patches in the bundle's patch list.

Redirects every `import app.morphe.patcher.patch.patch` to the music-only wrapper and
swaps the bundle smoke test for one that asserts nothing but Music/universal patches load.
Usage: music-only.py <this repo> <morphe-patches checkout>
"""
import pathlib
import re
import shutil
import sys

repo, tree = map(pathlib.Path, sys.argv[1:3])
src = tree / "patches/src/main/kotlin"
old = re.compile(r"^import app\.morphe\.patcher\.patch\.patch$", re.M)
new = "import app.morphe.patches.musiconly.patch"

changed = 0
for f in src.rglob("*.kt"):
    text = f.read_text(encoding="utf-8")
    out, n = old.subn(new, text)
    if n:
        f.write_text(out, encoding="utf-8", newline="")
        changed += 1
if changed < 100:
    sys.exit(f"only {changed} files import patch(); upstream layout changed?")

dest = src / "app/morphe/patches/musiconly"
dest.mkdir(parents=True, exist_ok=True)
shutil.copy(repo / "music-only/MusicOnlyPatch.kt", dest / "MusicOnlyPatch.kt")
shutil.copy(repo / "music-only/MusicOnlyCheck.java", tree / "tests/wireguard-bundle/WireGuardBundleSmoke.java")

# Bundle metadata shown in Morphe Manager.
gradle = tree / "patches/build.gradle.kts"
g = gradle.read_text(encoding="utf-8")
g = re.sub(r'(\n\s*name = )"[^"]*"', r'\1"YouTube Music network grace (unofficial)"', g, count=1)
g = re.sub(r'(\n\s*description = )"[^"]*"', r'\1"YouTube Music only: seo-rii WireGuard patches + crossfade network grace"', g, count=1)
gradle.write_text(g, encoding="utf-8", newline="")
print(f"redirected patch() in {changed} files")
