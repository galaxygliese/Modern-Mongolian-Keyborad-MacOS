#!/bin/bash
# Install (or remove) the Modern Mongolian keyboards for the current user.
# No administrator password, no restart.
#
#   curl -fsSL https://raw.githubusercontent.com/galaxygliese/Modern-Mongolian-Keyborad-MacOS/main/install.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/galaxygliese/Modern-Mongolian-Keyborad-MacOS/main/install.sh | bash -s -- --uninstall
#
# From a clone: ./install.sh  or  ./install.sh --uninstall
set -euo pipefail

REPO="galaxygliese/Modern-Mongolian-Keyborad-MacOS"
BUNDLE="ModernMongolian.bundle"
USER_DIR="$HOME/Library/Keyboard Layouts"
SYSTEM_DIR="/Library/Keyboard Layouts"

main() {
  local action="install"
  case "${1:-}" in
    "") ;;
    --uninstall) action="uninstall" ;;
    *) echo "usage: install.sh [--uninstall]" >&2; exit 2 ;;
  esac

  local src
  src="$(clone_dir)"
  if [[ -z "$src" ]]; then
    DOWNLOAD="$(mktemp -d)"
    trap 'rm -rf "$DOWNLOAD"' EXIT
    echo "Downloading $REPO…"
    curl -fsSL "https://github.com/$REPO/archive/refs/heads/main.tar.gz" |
      tar -xz -C "$DOWNLOAD" --strip-components 1
    src="$DOWNLOAD"
  fi

  if [[ "$action" == "uninstall" ]]; then
    uninstall "$src"
  else
    install "$src"
  fi
}

# The clone this script runs from, if any (empty when piped from curl).
clone_dir() {
  local here="${BASH_SOURCE[0]:-}"
  if [[ -n "$here" && -f "$here" ]]; then
    here="$(cd "$(dirname "$here")" && pwd)"
    if [[ -d "$here/$BUNDLE" ]]; then
      echo "$here"
    fi
  fi
}

# Run scripts/tis.js; drop the harmless cache chatter macOS prints on stderr.
tis() {
  osascript -l JavaScript "$1/scripts/tis.js" "$2" "$3" </dev/null \
    2> >(grep -v -e '^Keyboard Layouts:' -e 'TISFileInterrogator' >&2)
}

install() {
  local src="$1"
  mkdir -p "$USER_DIR"
  rm -rf "$USER_DIR/$BUNDLE"
  cp -R "$src/$BUNDLE" "$USER_DIR/"
  xattr -dr com.apple.quarantine "$USER_DIR/$BUNDLE" 2>/dev/null || true

  if [[ -d "$SYSTEM_DIR/$BUNDLE" ]]; then
    echo "Note: the .pkg version is also installed in $SYSTEM_DIR; remove one copy to avoid duplicates."
  fi

  if tis "$src" enable "$USER_DIR/$BUNDLE" >/dev/null && tis "$src" status "$USER_DIR/$BUNDLE" >/dev/null; then
    cat <<'EOF'

Installed. The keyboards are now in the input menu (menu bar):
  Мн  Mongolian – Modern Cyrillic
  ᠮᠣ  Mongolian – Traditional Script
Switch with Control-Space or the Globe (fn) key.
EOF
  else
    cat <<'EOF'

Installed, but macOS has not picked the keyboards up yet.
Log out and back in, then add them in
System Settings → Keyboard → Text Input → Edit → + → Mongolian.
EOF
  fi
}

uninstall() {
  local src="$1"
  if [[ -d "$USER_DIR/$BUNDLE" ]]; then
    tis "$src" disable "$USER_DIR/$BUNDLE" >/dev/null 2>&1 || true
    rm -rf "$USER_DIR/$BUNDLE"
  fi
  if [[ -d "$SYSTEM_DIR/$BUNDLE" ]]; then
    tis "$src" disable "$SYSTEM_DIR/$BUNDLE" >/dev/null 2>&1 || true
    echo "Removing the .pkg copy from $SYSTEM_DIR (administrator password required)."
    sudo rm -rf "$SYSTEM_DIR/$BUNDLE" </dev/tty
    sudo pkgutil --forget com.galaxygliese.keyboardlayout.modernmongolian.pkg >/dev/null 2>&1 </dev/tty || true
  fi
  echo "Uninstalled. Log out and back in to clear any cached menu entries."
}

main "$@"
