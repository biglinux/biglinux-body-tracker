#!/bin/bash

# Active virtual environment
if [[ -z $VIRTUAL_ENV ]]; then
    source venv/bin/activate
fi

pip install Pyinstaller

export DISPLAY=:99
sudo Xvfb -ac :99 -screen 0 800x600x24 > /dev/null 2>&1 &

pyinstaller --collect-data mediapipe big_head_tracker.py

if [[ -e /home/runner/work ]]; then
    cp -R dist/big_head_tracker/ /home/runner/work/ubuntu-compiled
    rm -R build
    rm -R venv
fi
