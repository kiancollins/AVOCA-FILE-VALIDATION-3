from .validators import *


def display_results(title: str, errors: list[str]):
    if errors: 
        expander_title = f"{title} — {len(errors)} issue(s)"
        with st.expander(expander_title, expanded=False):
            for err in errors:
                st.markdown(f"- {err}")
    else:
        success_msg = ERROR_TYPES.get(title, f"{title} passed all checks.")
        st.success(success_msg)



def run_product_checks(df: pd.DataFrame, products: list[Product], col_map, full_list_plu, full_list_barcode, full_supplier_codes):
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
            f"Product {plu} is already in the system on lines {', '.join(str(l+2) for l in lines)}")
        for line in lines:
            cell_flags["manual"].append((line, plu_idx))

    # Internal Duplicates
    internal_duplicates = check_internal_duplicates(products, "plu_code")
    for i in internal_duplicates:
        cell_flags["manual"].append((i, plu_idx))

    # PLU Length Errors
    plu_errors = []
    for product in products:
        if (e := product.plu_len()):
            plu_errors.append(e)
            cell_flags["manual"].append((product.row, plu_idx))

    # Duplicate Barcodes Within File
    prod_barcode__internal_errors, barcode_rows = duplicate_internal_barcodes(products, "plu_code")
    for row in barcode_rows:
        cell_flags["manual"].append((row, barcode_idx))

    # Duplicate Barcodes In Database
    full_prod_barcode_errors = check_duplicates(products, full_list_barcode, "barcode")
    for code, lines in full_prod_barcode_errors.items():
        for line in lines:
            cell_flags["manual"].append((line, barcode_idx))

    # PLU Used As Barcode
    plu_in_barcodes = check_duplicates(products, full_list_barcode, "plu_code")
    for code, lines in plu_in_barcodes.items():
        for line in lines:
            cell_flags["manual"].append((line, plu_idx))

    # Barcode Used As PLU
    barcodes_in_plu = check_duplicates(products, full_list_plu, "barcode")
    for code, lines in barcodes_in_plu.items():
        for line in lines:
            cell_flags["manual"].append((line, barcode_idx))

    # Supplier Exists
    supplier_exists, supplier_coords = check_exist(products, full_supplier_codes, "main_supplier")
    for row, _ in supplier_coords:  # second value is list of coords
        cell_flags["manual"].append((row, supplier_idx))


    # Display Results (Optional)
    display_results("Duplicate PLU Code Errors", duplicate_plu_errors)
    display_results("Duplicate PLUs Within Uploaded File", internal_duplicates)
    display_results("PLU Code Length Errors", plu_errors)
    display_results("Duplicate Barcode Within New Upload", prod_barcode__internal_errors)
    display_results("Duplicate Barcodes In Database", full_prod_barcode_errors)
    display_results("Duplicate PLU's Used As Existing Barcodes", plu_in_barcodes)
    display_results("Duplicate Barcodes Used As Existing PLU's", barcodes_in_plu)
    display_results("Check If Supplier Code Exists", supplier_exists)

    # Build summary
    if duplicate_plu_errors:
        manual_summary.extend([["Duplicate PLU Code Errors", err] for err in duplicate_plu_errors])
    if internal_duplicates:
        manual_summary.extend([["Duplicate PLUs Within Uploaded File", f"Line {i+2}: Duplicate PLU"] for i in internal_duplicates])
    if plu_errors:
        manual_summary.extend([["PLU Code Length Errors", err] for err in plu_errors])
    if prod_barcode__internal_errors:
        manual_summary.extend([["Duplicate Barcode Within New Upload", err] for err in prod_barcode__internal_errors])
    if full_prod_barcode_errors:
        for code, lines in full_prod_barcode_errors.items():
            msg = f"Barcode {code} is already in the system on lines {', '.join(str(l+2) for l in lines)}"
            manual_summary.append(["Duplicate Barcodes In Database", msg])
    if plu_in_barcodes:
        for code, lines in plu_in_barcodes.items():
            msg = f"PLU {code} is already used as a barcode on lines {', '.join(str(l+2) for l in lines)}"
            manual_summary.append(["Duplicate PLU's Used As Existing Barcodes", msg])
    if barcodes_in_plu:
        for code, lines in barcodes_in_plu.items():
            msg = f"Barcode {code} is already used as a PLU on lines {', '.join(str(l+2) for l in lines)}"
            manual_summary.append(["Duplicate Barcodes Used As Existing PLU's", msg])
    if supplier_exists:
        manual_summary.extend([["Supplier Code Errors", err] for err in supplier_exists])

    return cell_flags, manual_summary




def run_clothing_checks(df: pd.DataFrame, clothes, col_map, full_list_style, full_list_barcode, full_supplier_codes):
    cell_flags = {"manual": []}
    manual_summary = []

    # Style Code Duplication
    style_code_idx = df.columns.get_loc(col_map["style_code"])
    supplier_col = df.columns.get_loc(col_map["main_supplier"])

    duplicate_styles = check_duplicates(clothes, full_list_style, "style_code")
    duplicate_style_errors = []
    for style_code, lines in duplicate_styles.items():
        duplicate_style_errors.append(
            f"Item {style_code} is already in the system on lines {', '.join(str(l+2) for l in lines)}")
        for line in lines:
            cell_flags["manual"].append((line, style_code_idx))

    # Internal Duplicates
    internal_duplicates, internal_coords = check_clothing_duplicates(clothes)
    for row, _ in internal_coords:
        cell_flags["manual"].append((row, style_code_idx))

    # Barcode Conflicts
    clothing_barcode_errors, barcode_rows = duplicate_internal_barcodes(clothes, "style_code")
    barcode_col = df.columns.get_loc(col_map["barcode"])
    for row in barcode_rows:
        cell_flags["manual"].append((row, barcode_col))

    # Full List Barcode Duplicates
    full_clothing_barcode_errors = check_duplicates(clothes, full_list_barcode, "barcode")
    for code, lines in full_clothing_barcode_errors.items():
        full_clothing_barcode_errors[code] = f"Barcode {code} is already in the system on lines {', '.join(str(l+2) for l in lines)}"
        for line in lines:
            cell_flags["manual"].append((line, barcode_col))

    # Cross-References
    style_code_in_barcodes = check_duplicates(clothes, full_list_barcode, "style_code")
    for code, lines in style_code_in_barcodes.items():
        style_code_in_barcodes[code] = f"Style Code {code} is already used as a barcode in the system on lines {', '.join(str(l+2) for l in lines)}"
        for line in lines:
            cell_flags["manual"].append((line, style_code_idx))

    barcodes_in_style_code = check_duplicates(clothes, full_list_style, "barcode")
    for code, lines in barcodes_in_style_code.items():
        barcodes_in_style_code[code] = f"Barcode {code} is already used as a style code in the system on lines {', '.join(str(l+2) for l in lines)}"
        for line in lines:
            cell_flags["manual"].append((line, barcode_col))

    # Supplier Check
    supplier_exists, supplier_coords = check_exist(clothes, full_supplier_codes, "main_supplier")
    for row, _ in supplier_coords:
        cell_flags["manual"].append((row, supplier_col))

    # Style Length Check
    style_len_errors = []
    for item in clothes:
        result = item.style_len()
        if result:
            msg, row = result
            style_len_errors.append(msg)
            cell_flags["manual"].append((row, style_code_idx))

    # Display + Summarize
    display_results("All Duplicate Style Code Code Errors", duplicate_style_errors)
    display_results("Duplicate Style Codes Within Uploaded File", internal_duplicates)
    display_results("All Style Code Length Errors", style_len_errors)
    display_results("All Duplicate Barcode Errors Within New File", clothing_barcode_errors)
    display_results("Duplicate Barcodes In Database", full_clothing_barcode_errors)
    display_results("Duplicate Style Codes Used As Existing Barcodes", style_code_in_barcodes)
    display_results("Duplicate Barcodes Used As Existing Style Codes", barcodes_in_style_code)
    display_results("Check If Supplier Code Exists", supplier_exists)

    if duplicate_style_errors:
        manual_summary.extend([["Duplicate Style Code Errors", err] for err in duplicate_style_errors])
    if internal_duplicates:
        manual_summary.extend([["Internal Duplicate Style Codes", err] for err in internal_duplicates])
    if style_len_errors:
        manual_summary.extend([["Style Code Length Errors", err] for err in style_len_errors])
    if clothing_barcode_errors:
        manual_summary.extend([["Duplicate Barcodes Within File", err] for err in clothing_barcode_errors])
    if full_clothing_barcode_errors:
        manual_summary.extend([["Duplicate Barcodes In Database", err] for err in full_clothing_barcode_errors])
    if style_code_in_barcodes:
        manual_summary.extend([["Style Codes Used As Barcodes", err] for err in style_code_in_barcodes.values()])
    if barcodes_in_style_code:
        manual_summary.extend([["Barcodes Used As Style Codes", err] for err in barcodes_in_style_code.values()])
    if supplier_exists:
        manual_summary.extend([["Supplier Code Errors", err] for err in supplier_exists])

    return cell_flags, manual_summary







def run_price_checks(df: pd.DataFrame, products: list[Product], col_map, full_list_plu, full_supplier_codes):
    cell_flags = {"manual": []}
    manual_summary = []

    # Column indexes
    plu_idx = df.columns.get_loc(col_map["plu_code"])
    supplier_idx = df.columns.get_loc(col_map["main_supplier"])


    plu_exists, plu_coords = check_exist(products, full_list_plu, "plu_code")
    for row, _ in plu_coords:
            cell_flags["manual"].append((row, plu_idx))

    supplier_exists, supplier_coords = check_exist(products, full_supplier_codes, "main_supplier")
    for row, _ in supplier_coords:
        cell_flags["manual"].append((row, supplier_idx))




    display_results("Check if PLU code exists", plu_exists)
    display_results("Check if supplier code exists", supplier_exists)


    if plu_exists[0]:
        manual_summary.extend([["PLU Code Errors", err] for err in plu_exists])
    if supplier_exists[0]:
        manual_summary.extend([["Supplier Code Errors", err] for err in supplier_exists])
    

    return cell_flags, manual_summary
