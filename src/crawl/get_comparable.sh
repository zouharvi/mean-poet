#!/usr/bin/bash

mkdir -p crawl/
# TODO: wget metadata.json to crawl/

SCRIPT_LOCATION=$( dirname -- "$0";)

python3 "$SCRIPT_LOCATION/ptc.py" --metadata crawl/metadata.json
python3 "$SCRIPT_LOCATION/ruverses.py" --metadata crawl/metadata.json

# TODO: merge together