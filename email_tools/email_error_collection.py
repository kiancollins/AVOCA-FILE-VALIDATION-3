import pandas as pd
from utils.validators import *
from utils.contants import *



def collect_product_errors(df: pd.DataFrame, products: list[Clothing], col_map, full_list_plu, full_list_barcode, full_supplier_codes, header_row):
    """Run all product-level validation checks and return them as a dict."""

    cell_flags = {"manual": []}
    manual_summary = []

    # Column indexes
    plu_idx = df.columns.get_loc(col_map["plu_code"])
    barcode_idx = df.columns.get_loc(col_map["barcode"])
    supplier_idx = df.columns.get_loc(col_map["main_supplier"])

    # Duplicate PLU Codes
    duplicate_plu_dict = check_duplicates(products, full_list_plu, "plu_code")
    duplicate_plu_errors = []
    for plu, lines in duplicate_plu_dict.items():
        duplicate_plu_errors.append(
            f"Product {plu} is already in the system on lines {', '.join(str(l-2) for l in lines)}")
        for line in lines:
            cell_flags["manual"].append((line-header_row, plu_idx))

    # Internal Duplicates
    internal_duplicates = check_internal_duplicates(products, "plu_code")
    for i in internal_duplicates:
        cell_flags["manual"].append((i-header_row, plu_idx))

    # PLU Length Errors
    plu_errors = []
    for product in products:
        if (e := product.plu_len()):
            plu_errors.append(e)
            cell_flags["manual"].append(((product.excel_line-header_row), plu_idx))

    # Duplicate Barcodes Within File
    prod_barcode_internal_errors, barcode_rows = duplicate_internal_barcodes(products, "plu_code", header_row)
    for row in barcode_rows:
        cell_flags["manual"].append((row-header_row, barcode_idx))

    # Duplicate Barcodes In Database
    full_prod_barcode_errors = check_duplicates(products, full_list_barcode, "barcode")
    for code, lines in full_prod_barcode_errors.items():
        for line in lines:
            cell_flags["manual"].append((line-header_row, barcode_idx))

    # PLU Used As Barcode
    plu_in_barcodes = check_duplicates(products, full_list_barcode, "plu_code")
    for code, lines in plu_in_barcodes.items():
        for line in lines:
            cell_flags["manual"].append((line-header_row, plu_idx))

    # Barcode Used As PLU
    barcodes_in_plu = check_duplicates(products, full_list_plu, "barcode")
    for code, lines in barcodes_in_plu.items():
        for line in lines:
            cell_flags["manual"].append((line-header_row, barcode_idx))

    # Supplier Exists
    supplier_exists = check_exist(products, full_supplier_codes, "main_supplier")
    for _, row in supplier_exists[1]:  # second value is list of coords
        cell_flags["manual"].append((row-header_row, supplier_idx))

    # Build summary
    if duplicate_plu_errors:
        manual_summary.extend([["Duplicate PLU Code Errors", err] for err in duplicate_plu_errors])
    if internal_duplicates:
        manual_summary.extend([["Duplicate PLUs Within Uploaded File", f"Line {i-2}: Duplicate PLU"] for i in internal_duplicates])
    if plu_errors:
        manual_summary.extend([["PLU Code Length Errors", err] for err in plu_errors])
    if prod_barcode_internal_errors:
        manual_summary.extend([["Duplicate Barcode Within New Upload", err] for err in prod_barcode_internal_errors])
    if full_prod_barcode_errors:
        for code, lines in full_prod_barcode_errors.items():
            msg = f"Barcode {code} is already in the system on lines {', '.join(str(l-2) for l in lines)}"
            manual_summary.append(["Duplicate Barcodes In Database", msg])
    if plu_in_barcodes:
        for code, lines in plu_in_barcodes.items():
            msg = f"PLU {code} is already used as a barcode on lines {', '.join(str(l-2) for l in lines)}"
            manual_summary.append(["Duplicate PLU's Used As Existing Barcodes", msg])
    if barcodes_in_plu:
        for code, lines in barcodes_in_plu.items():
            msg = f"Barcode {code} is already used as a PLU on lines {', '.join(str(l-2) for l in lines)}"
            manual_summary.append(["Duplicate Barcodes Used As Existing PLU's", msg])
    if supplier_exists[0]:
        manual_summary.extend([["Supplier Code Errors", err] for err in supplier_exists[0]])

    print(manual_summary)
    return cell_flags, manual_summary








def collect_clothing_errors(df: pd.DataFrame, clothes: list[Clothing], col_map, full_list_style, full_list_barcode, full_supplier_codes, header_row):
    """Run all clothing-level validation checks and return a summary and cell highlights."""
    cell_flags = {"manual": []}
    manual_summary = []

    style_code_idx = df.columns.get_loc(col_map["style_code"])
    barcode_idx = df.columns.get_loc(col_map["barcode"])
    supplier_idx = df.columns.get_loc(col_map["main_supplier"])

    # Style Code Duplication

    duplicate_styles = check_duplicates(clothes, full_list_style, "style_code")
    duplicate_style_errors = []
    for style_code, lines in duplicate_styles.items():
        msg = f"Style Code {style_code} is already in the system on lines {', '.join(str(l-2) for l in lines)}"
        duplicate_style_errors.append(msg)
        for line in lines:
            cell_flags["manual"].append((line-header_row, style_code_idx))
        # for line in lines:
        #     cell_flags["manual"].append((line, style_code_idx))


    # Internal Duplicates
    internal_duplicates, internal_coords = check_clothing_duplicates(clothes)
    for row, _ in internal_coords:
        cell_flags["manual"].append((row-header_row, style_code_idx))


    # Barcode Conflicts
    internal_clothing_barcode_errors, barcode_rows = duplicate_internal_barcodes(clothes, "style_code")
    barcode_idx = df.columns.get_loc(col_map["barcode"])
    for row in barcode_rows:
        cell_flags["manual"].append((row-header_row, barcode_idx))


    # --- Barcode Conflicts (vs full list)
    full_clothing_barcode_errors = check_duplicates(clothes, full_list_barcode, "barcode")
    full_clothing_barcode_msgs = {}
    for code, lines in full_clothing_barcode_errors.items():
        msg = f"Barcode {code} is already in the system on lines {', '.join(str(l+2) for l in lines)}"
        full_clothing_barcode_msgs[code] = msg
        for line in lines:
            cell_flags["manual"].append((line-header_row, barcode_idx))

    # --- Cross-referencing: style_code used as barcode
    style_code_in_barcodes = check_duplicates(clothes, full_list_barcode, "style_code")
    style_code_cross_msgs = {}
    for code, lines in style_code_in_barcodes.items():
        msg = f"Style Code {code} is already used as a barcode on lines {', '.join(str(l+2) for l in lines)}"
        style_code_cross_msgs[code] = msg
        for line in lines:
            cell_flags["manual"].append((line-header_row, style_code_idx))

    # --- Cross-referencing: barcode used as style_code
    barcodes_in_style_code = check_duplicates(clothes, full_list_style, "barcode")
    barcode_cross_msgs = {}
    for code, lines in barcodes_in_style_code.items():
        msg = f"Barcode {code} is already used as a Style Code on lines {', '.join(str(l+2) for l in lines)}"
        barcode_cross_msgs[code] = msg
        for line in lines:
            cell_flags["manual"].append((line-header_row, barcode_idx))


    # Supplier Check
    supplier_exists, supplier_coords = check_exist(clothes, full_supplier_codes, "supplier_code")
    supplier_idx = df.columns.get_loc(col_map["supplier_code"])
    for row, _ in supplier_coords:
        cell_flags["manual"].append((row-header_row, supplier_idx))


    # Style Length Check
    style_len_errors = []
    for item in clothes:
        result = item.style_len()
        if result:
            msg, row = result
            style_len_errors.append(msg)
            cell_flags["manual"].append((row-header_row, style_code_idx))

    # Build summary
    if duplicate_style_errors:
        manual_summary.extend([["Duplicate Style Code Errors", err] for err in duplicate_style_errors])
    if internal_duplicates:
        manual_summary.extend([["Duplicate Style Codes Within Uploaded File", err] for err in internal_duplicates])
    if style_len_errors:
        manual_summary.extend([["Style Code Length Errors", err] for err in style_len_errors])
    if internal_clothing_barcode_errors:
        manual_summary.extend([["Duplicate Barcodes Within Uploaded File", err] for err in internal_clothing_barcode_errors])
    if full_clothing_barcode_msgs:
        manual_summary.extend([["Duplicate Barcodes In Database", err] for err in full_clothing_barcode_msgs.values()])
    if style_code_cross_msgs:
        manual_summary.extend([["Style Codes Used As Barcodes", err] for err in style_code_cross_msgs.values()])
    if barcode_cross_msgs:
        manual_summary.extend([["Barcodes Used As Style Codes", err] for err in barcode_cross_msgs.values()])
    if supplier_exists:
        manual_summary.extend([["Supplier Code Errors", err] for err in supplier_exists])



    print(manual_summary)
    return cell_flags, manual_summary







def collect_price_errors(df: pd.DataFrame, prices: list[Product], col_map, full_list_plu, full_supplier_codes, header_row):
    cell_flags = {"manual": []}
    manual_summary = []

    # Column indexes
    plu_idx = df.columns.get_loc(col_map["plu_code"])
    supplier_idx = df.columns.get_loc(col_map["main_supplier"])


    plu_exists, plu_coords = check_exist(prices, full_list_plu, "plu_code")
    for row, _ in plu_coords:
            cell_flags["manual"].append((row-header_row, plu_idx))

    supplier_exists, supplier_coords = check_exist(prices, full_supplier_codes, "main_supplier")
    for row, _ in supplier_coords:
        cell_flags["manual"].append((row-header_row, supplier_idx))


    if plu_exists[0]:
        manual_summary.extend([["PLU Code Errors", err] for err in plu_exists])
    if supplier_exists[0]:
        manual_summary.extend([["Supplier Code Errors", err] for err in supplier_exists])
    
    return cell_flags, manual_summary
