// SPDX-License-Identifier: GPL-3.0-only
// Added by ytm-network-grace's build: every `import app.morphe.patcher.patch.patch` in the
// patch sources is redirected here, so a patch that targets neither YouTube Music nor all apps
// is rebuilt without a name. Unnamed patches still work as dependencies but are not loaded
// into the bundle's patch list.
package app.morphe.patches.musiconly

import app.morphe.patcher.patch.Patch
import app.morphe.patcher.patch.PatchDefinition
import app.morphe.patcher.patch.patch as upstreamPatch

private const val MUSIC_PACKAGE = "com.google.android.apps.youtube.music"

fun patch(
    name: String? = null,
    description: String? = null,
    default: Boolean = true,
    block: PatchDefinition.() -> Unit = {},
): Patch {
    val built = upstreamPatch(name, description, default, block)
    val compatibility = built.compatibility ?: return built // Universal patch.
    if (name == null || compatibility.any { it.packageName == MUSIC_PACKAGE }) return built
    return upstreamPatch(null, description, default, block)
}
