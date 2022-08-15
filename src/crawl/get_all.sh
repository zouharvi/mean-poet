#!/usr/bin/bash

SCRIPT_LOCATION=$( dirname -- "$0";)

python3 "$SCRIPT_LOCATION/ptc.py" --metadata ""
python3 "$SCRIPT_LOCATION/ruverses.py" --metadata ""

cat crawl/ptc_meta.jsonl crawl/ruverses_meta.jsonl > crawl/metadata_custom.jsonl