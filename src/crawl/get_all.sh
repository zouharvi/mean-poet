#!/usr/bin/bash

SCRIPT_LOCATION=$( dirname -- "$0";)

python3 "$SCRIPT_LOCATION/ptc.py" --metadata ""
python3 "$SCRIPT_LOCATION/ruverses.py" --metadata ""

# TODO: merge together