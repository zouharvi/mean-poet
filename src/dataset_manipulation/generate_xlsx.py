#!/usr/bin/env python3

import sys
sys.path.append("src")
import json
import argparse
import random
from openpyxl import Workbook
from openpyxl.styles import Alignment, Color, PatternFill
from xlsx_constants import *

FIELDNAMES = [
    "title",
    "t_key",
    "translator",
    "translator_level",
    "stanza_i",
    "src",
    "hyp",
]

ATTRIBUTES = [
    "Meaning", "Poeticness", "Overall"
]


def ord_to_col(i):
    if i < 0:
        raise Exception(f"Attempted to transform {i} into a column name")
    if i < 26:
        return chr(ord("A") + i)
    if i < 26 * 26:
        return ord_to_col(i // 26 - 1) + ord_to_col(i % 26)
    raise Exception(f"Too large a column number {i}")


def get_height_for_row(sheet, row_number):
    row = list(sheet.rows)[row_number - 1]
    return max(
        30,
        max([
            (
                cell.value.count("\n") +
                len([x for x in cell.value.split("\n") if len(x.strip()) > 60])
            ) * 20 if cell.value is not None else 0
            for cell in row
        ])
    )


def add_sheet(workbook, poem, poem_i):
    t_keys = [x for x in poem.keys() if "translation-" in x]

    sheet = workbook.create_sheet(f"{poem_i:0>2}")
    sheet["A1"].value = "Source"
    sheet["A1"].font = FONT_BOLD

    for i in range(len(t_keys)):
        for a_i, a in enumerate(ATTRIBUTES):
            col = ord_to_col(i * (len(ATTRIBUTES) + 1) + a_i + 2)
            cell = sheet[f"{col}1"]
            cell.value = a
            cell.font = FONT_BOLD
            cell.alignment = Alignment(
                textRotation=90, horizontal="center"
            )
            sheet.column_dimensions[col].width = 3
    sheet.row_dimensions[1].height = 85
    sheet.freeze_panes = sheet["B2"]

    for t_key_i, t_key in enumerate(t_keys):
        for stanza_i, stanza_hyp in enumerate(poem[t_key]["poem"].split("\n\n")):
            col = ord_to_col(t_key_i * (len(ATTRIBUTES) + 1) + 1)

            for a_i, a in enumerate(ATTRIBUTES):
                col_a = ord_to_col(t_key_i * (len(ATTRIBUTES) + 1) + 1 + a_i)
                cell_a = sheet[f"{col_a}{stanza_i+2}"]
                cell_a.font = FONT_BOLD

            cell = sheet[f"{col}{stanza_i+2}"]
            cell.value = stanza_hyp.strip()
            if stanza_i % 2 == 0:
                cell.fill = FILL_PAIRS[t_key_i][0]
            else:
                cell.fill = FILL_PAIRS[t_key_i][1]
            cell.font = FONT_NORMAL
            sheet.column_dimensions[col].width = 45
            cell.alignment = Alignment(wrap_text=True)

        # stanza_i+3 points to the last empty row
        for a_i, a in enumerate(ATTRIBUTES):
            col_a = ord_to_col(t_key_i * (len(ATTRIBUTES) + 1) + 1 + a_i)
            cell_a = sheet[f"{col_a}{stanza_i+3}"]
            cell_a.font = FONT_BOLD

    for stanza_i, stanza_hyp in enumerate(poem["poem"].split("\n\n")):
        cell = sheet[f"A{stanza_i+2}"]
        cell.value = stanza_hyp.strip()
        if stanza_i % 2 == 0:
            cell.fill = FILL_0A
        else:
            cell.fill = FILL_0B
        cell.font = FONT_NORMAL

        sheet.row_dimensions[stanza_i +
                             2].height = get_height_for_row(sheet, stanza_i + 2)
        sheet.column_dimensions["A"].width = 45

    # stanza_i+3 points to the last empty row
    cell = sheet[f"A{stanza_i+3}"]
    cell.value = "Overall"
    cell.font = FONT_BOLD


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        "-d", "--dataset", default="data_raw/dataset.jsonl",
        help="Path to dataset file"
    )
    args.add_argument(
        "-o", "--out", default="data_raw/dataset.xlsx",
        help="Path to annotation dataset xlsx file"
    )
    args = args.parse_args()

    with open(args.dataset, "r") as f:
        data = [json.loads(x) for x in f.readlines()]

    # generate XLSX document
    workbook = Workbook()
    # remove default sheet
    workbook.remove(workbook.active)

    for poem_i, poem in enumerate(data):
        add_sheet(workbook, poem, poem_i)

    workbook.save(args.out)
