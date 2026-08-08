[app]
title = Bardo
package.name = bardo
package.domain = org.isolatedmind
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1.0
requirements = python3,pygame
orientation = landscape
fullscreen = 1
android.permissions = RECORD_AUDIO, MODIFY_AUDIO_SETTINGS
android.api = 33
android.minapi = 21
android.ndk = 25b

[buildozer]
log_level = 2
warn_on_root = 1