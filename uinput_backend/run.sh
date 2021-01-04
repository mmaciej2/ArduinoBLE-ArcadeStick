#!/bin/bash

set -e
exec 3< <(sudo /home/phthisis/anaconda3/bin/python arcadestick_backend.py)
PYTHON_PID=$!
sed '/connected/q' <&3
mame &
MAME_PID=$!
wait $PYTHON_PID
kill -9 $MAME_PID
