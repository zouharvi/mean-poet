#!/usr/bin/bash

SCRIPT_LOCATION=$( dirname -- "$0";)

python3 "$SCRIPT_LOCATION/ptc.py" --metadata ""
python3 "$SCRIPT_LOCATION/ruverses.py" --metadata ""

# builds jsonl from local tomls
./src/dataset_manipulation/toml_to_jsonl.py -i data_raw/wikics/*.toml -t computed/wikics_txt.jsonl

cat crawl/ptc_meta.jsonl crawl/ruverses_meta.jsonl > crawl/metadata_custom.jsonl
