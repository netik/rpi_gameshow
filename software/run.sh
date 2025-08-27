#!/bin/bash

if [ -z ${VIRTUAL_ENV} ]; then
    echo "loading venv."
    source .venv/bin/activate
fi

python3 ./main.py
    
