#!/bin/bash

set -e
exec 3< <(sudo /home/phthisis/anaconda3/bin/python arcadestick_backend.py)
PYTHON_PID=$!
grep -m1 'connected' <&3 || exit
mame &
MAME_PID=$!
wait $PYTHON_PID
kill -9 $MAME_PID
