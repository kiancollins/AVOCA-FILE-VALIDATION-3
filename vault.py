import pandas as pd
from collections import Counter, defaultdict
from classes.product_class import Product
from classes.clothing_class import Clothing
from utils.headers import *



def check_duplicates(products: list, all_products: list) -> dict[int, int]:
    """ Returns dictionary of what item codes are already used in the full list.
    """
    duplicates = {}
    for product in products:
        if product.plu_code in all_products:
            duplicates[product.plu_code] = all_products.index(product.plu_code)
    return duplicates



def get_all_plu(path: str) -> list[int]:
    """ Read an excel of all AVOCA products into a list of PLU codes """
    plu_df = pd.read_excel(path)
    plu_df.columns = plu_df.columns.str.lower().str.strip().str.replace(" ", "").str.replace("_", "").str.replace("-", "")
    if "plu" not in plu_df.columns:
        raise KeyError("Missing 'plu' column after normalization.")

    return plu_df["plu"].tolist()



def find_internal_duplicates(products: list[Product]) -> list[str]:
    """Checks for duplicate PLU codes within the new product file."""
    counts = Counter(product.plu_code for product in products)
    errors = []
    for plu, count in counts.items():
        if count > 1:
            lines = [product.excel_line for product in products if product.plu_code == plu]
            errors.append(f"PLU Code: {plu} appears {count} times on lines {lines}")
    return errors



def load_products(path: str) -> list[Product]:
    """Load the new product file into a list of Clothing class objects"""
    df = pd.read_excel(path)
    messages = []

    def get_col(key):
        col, msg, msg_type = find_header(df, PRODUCT_HEADER_MAP[key])
        if msg:
            messages.append((msg, msg_type))
        return col


    products = []
    for idx, row in df.iterrows():
        line_number = idx + 2
        product = Product(
            code = row.get(get_col("plu_code")),
            description = row.get(get_col("description")),
            subgroup = row.get(get_col("subgroup")),
            supplier_code = row.get(get_col("supplier_code")),
            season = row.get(get_col("season")),
            main_supplier = row.get(get_col("main_supplier")),
            cost_price = row.get(get_col("cost_price")),
            barcode = row.get(get_col("barcode")),
            vat_rate = row.get(get_col("vat_rate")),
            rrp = row.get(get_col("rrp")),
            sell_price = row.get(get_col("sell_price")),
            stg_price = row.get(get_col("stg_price")),
            tarriff = row.get(get_col("tarriff")),
            web = row.get(get_col("web")),
            idx = line_number
        )
        products.append(product)

 
    return products, messages



def load_clothing(path: str) -> list[Clothing]:

    """Load the new clothing file into a list of Clothing class objects"""
    df = pd.read_excel(path)
    clothes = []
    get_col = lambda key: find_header(df, CLOTHING_HEADER_MAP[key])
    for idx, row in df.iterrows():
        line_number = idx + 2
        clothing = Clothing(
            code = row.get(get_col("style_code")),
            description = row.get(get_col("description")),
            size = row.get(get_col("size")),
            colour = row.get(get_col("colour")),
            subgroup = row.get(get_col("subgroup")),
            supplier_code = row.get(get_col("supplier_code")),
            season = row.get(get_col("season")),
            main_supplier = row.get(get_col("main_supplier")),
            cost_price = row.get(get_col("cost_price")),  # Note: products use "cost_price"
            barcode = row.get(get_col("barcode")),
            vat_rate = row.get(get_col("vat_rate")),
            rrp = row.get(get_col("rrp")),
            sell_price = row.get(get_col("sell_price")),
            stg_price = row.get(get_col("stg_price")),  # products: "stg_price", clothing: "stgretailprice"
            tarriff = row.get(get_col("tarriff")),
            brand = row.get(get_col("brand")),
            product_type = row.get(get_col("product_type")),
            web = row.get(get_col("web")),
            country = row.get(get_col("country")),
            country_code = row.get(get_col("country_code")),
            idx = line_number
        )
        clothes.append(clothing)
    return clothes



def read_column(df: pd.DataFrame, possible_names) -> list:
    """Find the given column name and return that column as a list.
    Converts all objects to strings"""
    # if isinstance(possible_names, str):
    #     possible_names = [possible_names]
    # # try:
    #     # df = pd.read_excel(file_path)
    #     # normalized_cols = {normalize_header(col): col for col in df.columns}

    # # Exact match with key map
    #     for name in possible_names:
    #         normalized = normalize_header(name)
    #         if normalized in normalized_cols:
    #             return df[normalized_cols[normalized]].dropna().apply(normalizer).tolist(), "", "skip"

    # # Char match
    #     best_score = 0
    #     best_possible = None
    #     original_header = None
        
    #     for df_col_key, df_col_val in normalized_cols.items():
    #             for expected_name in possible_names:
    #                 score = char_match(expected_name, df_col_key)
    #                 if score > best_score:
    #                     best_score = score
    #                     best_possible = expected_name
    #                     original_header = df_col_val
        
    #     if best_score >= THRESHOLD:  # ← adjust threshold as needed
    #         msg = f"CHAR_MATCH updated the column header '{original_header}' to '{best_possible}' to match template spreadsheet"
    #         return df[best_possible].dropna().apply(normalizer).tolist(), msg, "alert"
    #     return [], possible_names[0], "error"

    # except Exception as e:
    #     return [], f"Error reading {file_path}: {e}", "error"



def update_all_products(df: pd.DataFrame):
    """Call fix functions and returns updated dataframe (a copy)"""
    df = df.copy()
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "")  # Normalize here
    new_description, desc_changes = fix_description(df)
    new_decimals, decimal_changes = fix_decimals(new_description)
    new_vat, vat_changes = fix_vat(new_decimals)
    # print("Final columns available:", df.columns.tolist())

    return new_vat, desc_changes + decimal_changes + vat_changes



def fix_decimals(df: pd.DataFrame):
    """Update the decimal rounding/format to the correct 2 decimal places"""
    columns = ['costprice', 'rrp', 'sellingprice', 'stgprice']
    changes = []
    for column in columns:
        if column not in df.columns:
            continue
        for i, num in df[column].items():
            if isinstance(num, (int, float)) and not math.isnan(num):
                decimal_val = Decimal(str(num))
                if -decimal_val.as_tuple().exponent > 2:
                    new_num = round(num, 2)
                    df.at[i, column] = new_num
                    changes.append(f"Line {i+2} \u00A0\u00A0|\u00A0\u00A0 {column} of {num} rounded to {new_num}")
    return df, changes




def bad_char(obj, id_attr: str) -> str:
    """ The characters ',% can't be in any product variables. Check if they have any and return where.
        Input for id_attr should be the code/name of item preferred when returning an error message.
    """
    bad_fields = []
    for field, value in vars(obj).items():     # Grab each variable and the value for the product
            if isinstance(value, str):          # Avoid type error
                if any(char in value for char in BAD_CHARS):    # Check if any bad chars are in the value
                    bad_fields.append(field)

    if bad_fields:
            line = getattr(obj, "excel_line", None)
            id = getattr(obj, id_attr, None)
            return f"Line {line} \u00A0\u00A0|\u00A0\u00A0 {id} contains invalid character(s) {BAD_CHARS}"







# Old Interface CLOTHING Error Checking


#     duplicate_styles = check_duplicates(clothes, full_list_style, "style_code")
#     duplicate_style_errors = []
#     style_code_idx = df.columns.get_loc(col_map["style_code"])
#     for style_code, lines in duplicate_styles.items():
#         duplicate_style_errors.append(
#             f"Item {style_code} is already in the system on lines {', '.join(str(l+2) for l in lines)}")
#         for line in lines:
#             cell_flags["manual"].append((line, style_code_idx))

#     internal_duplicates, internal_coords = check_clothing_duplicates(clothes)
#     style_code_idx = df.columns.get_loc(col_map["style_code"])
#     for row, _ in internal_coords:
#         cell_flags["manual"].append((row, style_code_idx))


#     clothing_barcode_errors, barcode_rows = duplicate_internal_barcodes(clothes, "style_code")
#     barcode_col = df.columns.get_loc(col_map["barcode"])
#     for row in barcode_rows:
#         cell_flags["manual"].append((row, barcode_col))


#     full_clothing_barcode_errors = check_duplicates(clothes, full_list_barcode, "barcode")
#     for code, lines in full_clothing_barcode_errors.items():
#         full_clothing_barcode_errors[code] = f"Barcode {code} is already in the system on lines {', '.join(str(l+2) for l in lines)}"
#         for line in lines:
#             cell_flags["manual"].append((line, barcode_col))


#     style_code_in_barcodes = check_duplicates(clothes, full_list_barcode, "style_code")
#     for code, lines in style_code_in_barcodes.items():
#         style_code_in_barcodes[code] = f"Style Code {code} is already used as a barcode in the system on lines {', '.join(str(l+2) for l in lines)}"
#         for line in lines:
#             cell_flags["manual"].append((line, style_code_idx))


#     barcodes_in_style_code = check_duplicates(clothes, full_list_style, "barcode")
#     for code, lines in barcodes_in_style_code.items():
#         barcodes_in_style_code[code] = f"Barcode {code} is already used as a style code in the system on lines {', '.join(str(l+2) for l in lines)}"
#         for line in lines:
#             cell_flags["manual"].append((line, barcode_col))



#     supplier_exists, supplier_coords = check_exist(clothes, full_supplier_codes, "main_supplier")
#     supplier_col = df.columns.get_loc(col_map["main_supplier"])
#     for row, _ in supplier_coords:
#         cell_flags["manual"].append((row, supplier_col))


        
#     style_len_errors = []

#     for item in clothes:
#         result = item.style_len()
#         if result:
#             msg, row = result
#             style_len_errors.append(msg)
#             style_col = df.columns.get_loc(col_map["style_code"])
#             cell_flags["manual"].append((row, style_col))


#     manual_summary = []

#     if any([duplicate_style_errors, internal_duplicates, style_len_errors, 
#         clothing_barcode_errors, style_code_in_barcodes, barcodes_in_style_code, 
#         full_clothing_barcode_errors, supplier_exists]):

# # Display Errors
#         display_results("All Duplicate Style Code Code Errors", duplicate_style_errors)
#         display_results("Duplicate Style Codes Within Uploaded File", internal_duplicates)
#         display_results("All Style Code Length Errors", style_len_errors)
#         display_results("All Duplicate Barcode Errors Within New File", clothing_barcode_errors)
#         display_results("Duplicate Barcodes In Database", full_clothing_barcode_errors)
#         display_results("Duplicate Style Codes Used As Existing Barcodes", style_code_in_barcodes)
#         display_results("Duplicate Barcodes Used As Existing Style Codes", barcodes_in_style_code)
#         display_results("Check If Supplier Code Exists", supplier_exists)



#         # Build manual summary from individual lists

#         if duplicate_style_errors:
#             manual_summary.extend([["Duplicate Style Code Errors", err] for err in duplicate_style_errors])
#         if internal_duplicates:
#             manual_summary.extend([["Internal Duplicate Style Codes", err] for err in internal_duplicates])
#         if style_len_errors:
#             manual_summary.extend([["Style Code Length Errors", err] for err in style_len_errors])
#         if clothing_barcode_errors:
#             manual_summary.extend([["Duplicate Barcodes Within File", err] for err in clothing_barcode_errors])
#         if full_clothing_barcode_errors:
#             manual_summary.extend([["Duplicate Barcodes In Database", err] for err in full_clothing_barcode_errors])
#         if style_code_in_barcodes:
#             manual_summary.extend([["Style Codes Used As Barcodes", err] for err in style_code_in_barcodes])
#         if barcodes_in_style_code:
#             manual_summary.extend([["Barcodes Used As Style Codes", err] for err in barcodes_in_style_code])
#         if supplier_exists:
#             manual_summary.extend([["Supplier Code Errors", err] for err in supplier_exists])








# Old Interface PRODUCT Error Checking


#     duplicate_plu_dict = check_duplicates(products, full_list_plu, "plu_code")
#     duplicate_plu_errors = [
#         f"Line: {line + 2} \u00A0\u00A0|\u00A0\u00A0 Product {plu} is already in the system."  # +2 to match Excel row (header + 0-indexed)
#         for plu, line in duplicate_plu_dict.items()
#     ]
#     internal_duplicates = check_internal_duplicates(products, "plu_code")
#     prod_barcode__internal_errors = duplicate_internal_barcodes(products, "plu_code")

#     full_prod_barcode_errors = check_duplicates(products, full_list_barcode, "barcode")
#     duplicate_barcode_errors = [
#         f"Line: {line + 2} \u00A0\u00A0|\u00A0\u00A0  Barcode {barcode} is already in the system."  # +2 to match Excel row (header + 0-indexed)
#         for barcode, line in full_prod_barcode_errors.items()
#     ]
#     plu_in_barcodes = check_duplicates(products, full_list_barcode, "plu_code")
#     barcodes_in_plu = check_duplicates(products, full_list_plu, "barcode")
#     plu_errors = []
#     prod_bad_char_errors = []
#     supplier_exists = check_exist(products, full_supplier_codes, "main_supplier")

    

# # Check all products and store in proper lists
#     for product in products:
#         if (e := product.plu_len()):
#             plu_errors.append(e)
        
# # If no errors
#     if any([duplicate_plu_errors, internal_duplicates, plu_errors, 
#                 prod_barcode__internal_errors, duplicate_barcode_errors, 
#                 plu_in_barcodes, barcodes_in_plu, supplier_exists]):
#         st.header("Unresolved Errors")
        
#         display_results("Duplicate PLU Code Errors", duplicate_plu_errors)
#         display_results("Duplicate PLUs Within Uploaded File", internal_duplicates)
#         display_results("PLU Code Length Errors", plu_errors)
#         display_results("Duplicate Barcode Within New Upload", prod_barcode__internal_errors)
#         display_results("Duplicate Barcodes In Database", duplicate_barcode_errors)
#         display_results("Duplicate PLU's Used As Existing Barcodes", plu_in_barcodes)
#         display_results("Duplicate Barcodes Used As Existing PLU's", barcodes_in_plu)
#         display_results("Check If Supplier Code Exists", supplier_exists)
        