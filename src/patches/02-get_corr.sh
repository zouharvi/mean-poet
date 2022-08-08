#!/usr/bin/bash

CUBLAS_WORKSPACE_CONFIG=:4096:8 ./src/generate_features.py -i data/farewell_boston.csv data/katze_aegypt.csv -o data/all_f.csv -H

./src/run_lr.py -i data/all_f.csv