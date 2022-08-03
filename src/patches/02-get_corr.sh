#!/usr/bin/bash

./src/generate_features.py -i data/farewell_boston.csv data/katze_aegypt.csv -o data/all_f.csv

./src/run_lr.py -i data/all_f.csv