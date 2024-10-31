#!/bin/bash

# Active virtual environment
if [[ -z $VIRTUAL_ENV ]]; then
    source venv/bin/activate
fi

pip install Pyinstaller

# Only in github actions
if [[ -e /home/runner/work ]]; then
    export DISPLAY=:99
    sudo Xvfb -ac :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
    sleep 5 
fi

pyinstaller -y --add-data icon.png:. --add-data icon.svg:. --collect-data mediapipe $1 big_head_tracker.py

# Only in github actions
if [[ -e /home/runner/work ]]; then
    rm -R build
    rm -R venv
fi
