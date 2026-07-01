[app]
title = Predictor PRO
package.name = predictorpro
package.domain = org.tuempresa

source.dir = app
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

requirements = python3,kivy==2.1.0,kivymd==1.1.1,requests==2.31.0,plyer==2.9,setuptools,cython

orientation = portrait
fullscreen = 0

android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

android.api = 30
android.minapi = 21
android.ndk = 23b
android.sdk = 30

android.gradle_dependencies = 'com.google.android.material:material:1.6.1'

# Para el icono (opcional)
# icon.filename = %(source.dir)s/icon.png
# presplash.filename = %(source.dir)s/presplash.png

android.archs = arm64-v8a, armeabi-v7a

# Para debug
android.ignore_setup = False

[buildozer]
log_level = 2
warn_on_root = 1
