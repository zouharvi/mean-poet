#!/usr/bin/bash

mkdir -p crawl/
# TODO: wget metadata.json from our server to crawl/

SCRIPT_LOCATION=$( dirname -- "$0";)

python3 "$SCRIPT_LOCATION/ptc.py" --metadata crawl/metadata.json
python3 "$SCRIPT_LOCATION/ruverses.py" --metadata crawl/metadata.json

# builds jsonl from local tomls
./src/dataset_manipulation/toml_to_jsonl.py -i data_raw/wikics/*.toml -t computed/wikics_txt.jsonl

cat crawl/ptc_txt.jsonl crawl/ruverses_txt.jsonl > crawl/dataset.jsonl