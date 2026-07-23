#!/bin/bash
set +x
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="$SAMPLE_JWMRC"

sed "s|JWMSANDBOX_DIR|$SCRIPT_DIR|g" "$CONFIG" > /tmp/jwm_resolved.jwmrc

pkill -f "Xephyr :1" 2>/dev/null
pkill jwm 2>/dev/null
pkill picom 2>/dev/null
pkill tint2 2>/dev/null
sleep 0.5

Xephyr :1 -screen 1280x720 &
sleep 1

DISPLAY=:1 picom -b --backend xrender &
sleep 0.5

DISPLAY=:1 jwm -f /tmp/jwm_resolved.jwmrc &
sleep 0.5
DISPLAY=:1 pasystray &

DISPLAY=:1 tint2 -c "$SCRIPT_DIR/tint2rc" &
sleep 0.5

DISPLAY=:1 xterm &
DISPLAY=:1 xeyes &
DISPLAY=:1 feh --bg-fill wallpaper.jpg
set -x