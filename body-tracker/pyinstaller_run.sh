#!/bin/bash

# Active virtual environment
if [[ -z $VIRTUAL_ENV ]]; then
    source venv/bin/activate
fi

pip install Pyinstaller

export DISPLAY=:99
sudo Xvfb -ac :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
sleep 5 

pyinstaller -y --hidden-import lib-dynload --collect-all lib-dynload --collect-submodules lib-dynload --collect-data mediapipe big_head_tracker.py

# pyinstaller -y --hidden-import lib-dynload --hidden-import _contextvars --hidden-import contextvars --collect-data mediapipe big_head_tracker.py



#cp -f "$(readlink -f /usr/lib/x86_64-linux-gnu/libpython*.so)" dist/big_head_tracker/_internal/

cp -f /usr/lib/x86_64-linux-gnu/libpython*.so dist/big_head_tracker/_internal/

if [[ -e /home/runner/work ]]; then
    rm -R build
    rm -R venv
fi
