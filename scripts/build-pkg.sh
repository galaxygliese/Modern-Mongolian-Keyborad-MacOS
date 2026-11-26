#!/bin/bash
# Build dist/ModernMongolian-<version>.pkg (installs for all users) and a .zip of the bundle.
set -euo pipefail
cd "$(dirname "$0")/.."

BUNDLE="ModernMongolian.bundle"
version="$(/usr/libexec/PlistBuddy -c "Print CFBundleShortVersionString" "$BUNDLE/Contents/Info.plist")"
stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT

# Copy without quarantine/Finder attributes (Installer restores any that remain).
mkdir -p "$stage/root/Library/Keyboard Layouts" "$stage/scripts" dist
ditto --norsrc --noextattr --noacl "$BUNDLE" "$stage/root/Library/Keyboard Layouts/$BUNDLE"
ditto --norsrc --noextattr --noacl scripts/pkg/postinstall "$stage/scripts/postinstall"
ditto --norsrc --noextattr --noacl scripts/tis.js "$stage/scripts/tis.js"
chmod +x "$stage/scripts/postinstall"

# Installer otherwise "relocates" the bundle into any existing copy with the same id.
pkgbuild --analyze --root "$stage/root" "$stage/component.plist" >/dev/null
plutil -replace 0.BundleIsRelocatable -bool false "$stage/component.plist"

pkgbuild \
  --root "$stage/root" \
  --component-plist "$stage/component.plist" \
  --scripts "$stage/scripts" \
  --identifier com.galaxygliese.keyboardlayout.modernmongolian.pkg \
  --version "$version" \
  --install-location / \
  "dist/ModernMongolian-$version.pkg"

rm -f "dist/ModernMongolian-$version.zip"
ditto -c -k --norsrc --noextattr --keepParent "$stage/root/Library/Keyboard Layouts/$BUNDLE" \
  "dist/ModernMongolian-$version.zip"
echo "built dist/ModernMongolian-$version.pkg and .zip"
