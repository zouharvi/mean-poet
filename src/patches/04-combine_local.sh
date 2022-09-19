#!/usr/bin/bash

./src/dataset_manipulation/toml_to_jsonl.py \
    --overwrite \
    -o computed/dataset_local.jsonl;

./src/dataset_manipulation/crawl_to_jsonl.py \
    --overwrite \
    --lang-filter hi \
    -o computed/dataset_hi.jsonl;

cat computed/dataset_{hi,local}.jsonl > computed/dataset.jsonl;
rm computed/dataset_{hi,local}.jsonl

./src/dataset_manipulation/add_translate_google.py \
    -o computed/dataset.jsonl;

./src/dataset_manipulation/add_translate_lindat.py \
    -o computed/dataset.jsonl;

./src/dataset_manipulation/generate_xlsx.py \
    -d computed/dataset.jsonl;