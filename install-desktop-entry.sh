#!/bin/bash
# Generates a desktop launcher (app-menu icon) pointing at THIS checkout's
# actual path. A checked-in .desktop file can't do this -- Exec=/Icon=
# require absolute paths per the XDG spec, so one committed to git would
# only ever be correct for whoever originally wrote it.

set -e
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="$HOME/.local/share/applications"
TARGET_FILE="$TARGET_DIR/characterengine.desktop"

mkdir -p "$TARGET_DIR"

cat > "$TARGET_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=CharacterEngine
Comment=Local AI companion framework
Exec=$PROJECT_DIR/launch.sh
Icon=$PROJECT_DIR/icon.png
Terminal=false
Categories=Network;Chat;
StartupNotify=true
EOF

chmod +x "$TARGET_FILE"
echo "Desktop entry installed at $TARGET_FILE"
echo "It should now appear in your application menu as \"CharacterEngine\"."
