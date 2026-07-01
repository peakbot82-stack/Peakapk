[app]
title = Predictor PRO
package.name = predictorpro
package.domain = org.tuempresa

source.dir = app
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

requirements = python3,kivy==2.1.0,kivymd==1.1.1,requests==2.31.0,plyer,setuptools,cython

orientation = portrait
fullscreen = 0

# Android specific - USAR VERSIONES ESTABLES
android.api = 30
android.minapi = 21
android.ndk = 23b
android.sdk = 30
android.build_tools = 30.0.3

android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.gradle_dependencies = 'com.google.android.material:material:1.6.1'
android.archs = arm64-v8a, armeabi-v7a

# Para que acepte las licencias automáticamente
android.accept_sdk_license = True

# Para debug
android.ignore_setup = False
log_level = 2

[buildozer]
warn_on_root = 1
