#!/bin/bash
set +x
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="$SAMPLE_JWMRC"

# Replace JWMSANDBOX_DIR placeholder with actual path
sed "s|JWMSANDBOX_DIR|$SCRIPT_DIR|g" "$CONFIG" > /tmp/jwm_resolved.jwmrc

pkill -f "Xephyr :1" 2>/dev/null
pkill jwm 2>/dev/null
sleep 0.5

Xephyr :1 -screen 1280x720 &
sleep 1

DISPLAY=:1 jwm -f /tmp/jwm_resolved.jwmrc &
sleep 0.5

DISPLAY=:1 xterm &
DISPLAY=:1 xeyes &
DISPLAY=:1 xload &
DISPLAY=:1 xterm &
# DISPLAY=:1 python3 src/beasdock.py &
set -x