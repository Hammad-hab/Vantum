#!/bin/bash

# Requires SAMPLE_JWMRC to be set in your .bashrc
# Example: export SAMPLE_JWMRC="/mnt/c/Users/hamma/Documents/Hammad/BeasOS/jwmsandbox/sample.jwmrc"
CONFIG="$SAMPLE_JWMRC"

# Kill existing JWM and Xephyr on :1 if running
pkill -f "Xephyr :1" 2>/dev/null
pkill jwm 2>/dev/null
sleep 0.5

# Start Xephyr
Xephyr :1 -screen 1280x720 &
sleep 1

# Start JWM with config
DISPLAY=:1 jwm -f "$CONFIG" &
sleep 0.5

# Start a terminal inside
DISPLAY=:1 xterm &

echo "JWM running on :1"
echo "Config: $CONFIG"
echo ""
echo "To restart JWM with new config:"
echo "  DISPLAY=:1 jwm -f $CONFIG"
echo "To validate config:"
echo "  DISPLAY=:1 jwm -p -f $CONFIG"
