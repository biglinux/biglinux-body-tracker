#!/bin/bash

# Install virtual environment
if [[ ! -e venv ]]; then
    python -m venv venv
fi

source venv/bin/activate

pip install -r requirements.txt
