#!/bin/bash

# Active virtual environment
if [[ -z $VIRTUAL_ENV ]]; then
    source venv/bin/activate
fi

pip install Pyinstaller

export DISPLAY=:99
sudo Xvfb -ac :99 -screen 0 800x600x24 > /dev/null 2>&1 &
sleep 5 

pyinstaller --collect-data mediapipe big_head_tracker.py

if [[ "$(ls -1 dist/big_head_tracker/_internal/libpython*)" != "" ]]; then
    pyinstaller --collect-data mediapipe big_head_tracker.py
fi

if [[ "$(ls -1 dist/big_head_tracker/_internal/libpython*)" != "" ]]; then
    pyinstaller --collect-data mediapipe big_head_tracker.py
fi

if [[ "$(ls -1 dist/big_head_tracker/_internal/libpython*)" != "" ]]; then
    pyinstaller --collect-data mediapipe big_head_tracker.py
fi

if [[ -e /home/runner/work ]]; then
    rm -R build
    rm -R venv
fi
