#!/usr/bin/bash

SCRIPT_LOCATION=$( dirname -- "$0";)

# only run the second script if the first one succeeds
python3 "$SCRIPT_LOCATION/ptc_1.py" &&
python3 "$SCRIPT_LOCATION/ptc_2.py"

# only run the second script if the first one succeeds
python3 "$SCRIPT_LOCATION/ruverses_1.py" &&
python3 "$SCRIPT_LOCATION/ruverses_2.py"