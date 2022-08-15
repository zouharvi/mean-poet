#!/usr/bin/bash

SCRIPT_LOCATION=$( dirname -- "$0";)

python3 "$SCRIPT_LOCATION/ptc.py"
python3 "$SCRIPT_LOCATION/ruverses.py"

# TODO: merge together