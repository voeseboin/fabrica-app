[app]
title = Fábrica App
package.name = fabricaapp
package.domain = org.fabrica
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,html,css,js
source.exclude_dirs = tests,bin,venv*
version = 1.0
requirements = python3,flask,flask-sqlalchemy,fpdf2
orientation = landscape
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
# android.sdk = 23
android.ndk = 23b
android.accept_sdk_license = True
android.mode = webview
android.webview_url = http://localhost:5000
android.webview.debug = True

[buildozer]
log_level = 2
warn_on_root = 1
p4a.cython = False
