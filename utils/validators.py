"""
Validators

Common validation checks done on uploaded files
"""
from classes.product_class import *
from classes.clothing_class import *
from utils.normalizer import *
from utils.contants import *
from collections import defaultdict, Counter
import pandas as pd



def check_duplicates(items: list[Product | Clothing], full_list: list, attr: str) -> dict[str, list[int]]:
    """
    Returns a dictionary mapping each value in items (based on attr) that already exists 
    in full_list to a list of 0-based row indexes where it appears in the new file.
    This helps highlight all duplicate lines, not just the first one.
    """
    duplicates = {}
    full_list_cleaned = set(normalizer(str(x)) for x in full_list)

    for item in items:
        value = normalizer(getattr(item, attr, None))
        if value in full_list_cleaned:
            duplicates.setdefault(value, []).append(item.excel_line - 2)

    return duplicates



def duplicate_internal_barcodes(items: list[Product | Clothing], attr: str) -> tuple[list[str], list[int]]:
    """Checks for duplicate barcodes among uploaded items.
       Returns error strings and a list of affected row indexes.
    """
    barcode_to_entries = defaultdict(list)
    error_list = []
    coords = []

    for item in items:
        if item.barcode:
            id_val = normalizer(getattr(item, attr, None))
            barcode = str(item.barcode).strip()
            barcode_to_entries[barcode].append((id_val, item.excel_line))

    for barcode, entries in barcode_to_entries.items():
        if len(entries) > 1:
            detail = ", ".join([f"{id_val} (line {line})" for id_val, line in entries])
            error_list.append(f"Barcode {barcode} is shared by: {detail}")
            coords.extend([line - 2 for _, line in entries])  # row index (0-based)

    return error_list, coords





def check_internal_duplicates(items: list[Product | Clothing], attr: str) -> list[int]:
    """Return the row indices (zero-based) of all internal duplicates based on the given attribute."""
    values = [normalizer(getattr(item, attr, None)) for item in items]
    counts = Counter(values)

    duplicates = []
    for code, count in counts.items():
        if code and count > 1:
            lines = [item.excel_line - 2 for item in items if normalizer(getattr(item, attr, None)) == code]
            duplicates.extend(lines)
    return duplicates




def check_clothing_duplicates(items: list[Clothing]) -> tuple[list[str], list[tuple[int, int]]]:
    """Check if there are duplicate clothing items (same style, size, colour) in new upload."""
    combo_to_lines = defaultdict(list)
    errors = []
    coords = []

    for item in items:
        key = (item.style_code, item.size, item.colour)
        combo_to_lines[key].append(item.excel_line)

    for key, lines in combo_to_lines.items():
        if len(lines) > 1:
            style_code, size, _ = key
            for line in lines:
                errors.append(f"Duplicate Style {style_code} with size {size} on line {line}")
                coords.append((line - 2, None))  # 0-based row, column set later

    return errors, coords




def check_exist(items: list[Product | Clothing], full_list: list, attr: str) -> tuple[list[str], list[tuple[int, int]]]:
    """ Returns list of error strings and the coordinates of cells with codes not in the full list. """
    nonexist = []
    coords = []

    # Normalize full list once
    full_list_cleaned = [normalizer(str(x)) for x in full_list]

    for idx, item in enumerate(items):
        code = normalizer(str(getattr(item, attr, "")))  # Make sure it's a str before normalizing
        if code not in full_list_cleaned:
            nonexist.append(f"Line {idx+2} \u00A0\u00A0|\u00A0\u00A0 '{code}' does not currently exist in data base.")
            coords.append((idx, None))  # will fill in col index in interface

    return nonexist, coords


