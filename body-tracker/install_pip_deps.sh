#!/bin/bash

# Install virtual environment
if [[ ! -e venv ]]; then
    python -m venv venv
fi

source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

#if [[ -e /home/runner/work ]]; then
#    cp -R dist/big_head_tracker/ /home/runner/work/ubuntu-compiled
#    rm -R build
#    rm -R venv
#fi
