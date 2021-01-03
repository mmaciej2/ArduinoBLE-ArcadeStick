#!/bin/bash

set -e

if [ -z "$(pgrep qjoypad)" ]; then
  qjoypad &
  sleep 3
fi
python arcadestick_hog.py &
PYTHON_PID=$!
sleep 3
trap "kill -9 $PYTHON_PID" ERR
sudo ./attach_usbip.sh || exit;
mame &
MAME_PID=$!
wait $PYTHON_PID
kill -9 $MAME_PID
