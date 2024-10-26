#!/bin/bash

# Active virtual environment
if [[ -z $VIRTUAL_ENV ]]; then
    source venv/bin/activate
fi

exec python big_head_tracker.py $*
