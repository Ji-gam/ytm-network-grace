// SPDX-License-Identifier: GPL-3.0-only
import app.morphe.patcher.patch.Compatibility;
import app.morphe.patcher.patch.Patch;
import app.morphe.patcher.patch.PatchLoader;

import java.io.File;
import java.util.Set;

/** Fails unless every loadable patch in the bundle targets YouTube Music or all apps. */
public final class WireGuardBundleSmoke {
    private static final String MUSIC = "com.google.android.apps.youtube.music";

    public static void main(String[] args) {
        Set<Patch> patches = new PatchLoader.Jar(Set.of(new File(args[0])));
        int music = 0, universal = 0;
        boolean wireGuard = false, crossfade = false;
        for (Patch patch : patches) {
            if (patch.getCompatibility() == null) {
                universal++;
                continue;
            }
            for (Compatibility c : patch.getCompatibility()) {
                if (!MUSIC.equals(c.getPackageName())) {
                    throw new AssertionError("Non-Music patch left in bundle: " + patch.getName()
                            + " (" + c.getPackageName() + ")");
                }
            }
            music++;
            if ("WireGuard proxy (experimental)".equals(patch.getName())) wireGuard = true;
            if ("Crossfade".equalsIgnoreCase(patch.getName())) crossfade = true;
        }
        if (music == 0) throw new AssertionError("No Music patches found");
        if (!wireGuard) throw new AssertionError("Music WireGuard patch missing");
        System.out.println("PASS " + music + " Music patches + " + universal + " universal patches, nothing else"
                + (crossfade ? " (Crossfade present)" : ""));
    }
}
