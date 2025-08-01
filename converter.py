import pandas as pd

from classes.product_class import Product
from classes.clothing_class import Clothing
from classes.price_amend_class import Price_Amend
from utils.headers import *
from utils.validators import *
from utils.normalizer import *



def load_products(df: pd.DataFrame, header_row: int) -> tuple[list[Product], list[tuple[str, str]]]:
    """Load the new product file into a list of Product class objects"""
    # expected_headers = [name for sublist in PRODUCT_HEADER_MAP.values() for name in sublist]

    messages = []
    
    # Pre-resolve all needed column names
    used_columns = set()
    col_map = {}
    for key in PRODUCT_HEADER_MAP:
        col, message, type = find_header(df, PRODUCT_HEADER_MAP[key], used_columns)
        if col:
            used_columns.add(col)
        col_map[key] = col  # May be None if not found
        if message:
            messages.append((message, type))

    # Build Product objects using resolved column names
    products = []
    for idx, row in df.iterrows():
        line_number = header_row + idx + 2
        product = Product(
            code = normalizer(row.get(col_map["plu_code"])),
            description = row.get(col_map["description"]),
            subgroup = row.get(col_map["subgroup"]),
            supplier_code = row.get(col_map["3_digit_supplier"]),
            season = row.get(col_map["season"]),
            main_supplier = row.get(col_map["main_supplier"]),
            cost_price = row.get(col_map["cost_price"]),
            barcode = barcode_normalizer(row.get(col_map["barcode"])),
            vat_rate = row.get(col_map["vat_rate"]),
            rrp = row.get(col_map["rrp"]),
            sell_price = row.get(col_map["sell_price"]),
            stg_price = row.get(col_map["stg_price"]),
            tariff = row.get(col_map["tariff"]),
            web = row.get(col_map["web"]),
            idx = line_number,
            # New Ones
            colour = row.get(col_map["colour"]),
            size = row.get(col_map["size"]),
            supplier_item_code = row.get(col_map["supplier_item_code"]),
            purchase_unit_qty = row.get(col_map["purchase_unit_qty"]),
            purchase_unit_desc = row.get(col_map["purchase_unit_desc"]),
            offer_analysis = row.get(col_map["offer_analysis"]),
            product_type = row.get(col_map["product_type"]),
            brand_in_store = row.get(col_map["brand_in_store"]),
            servicetype = row.get(col_map["servicetype"]),
            item_type = row.get(col_map["item_type"]),
            activity_indicator = row.get(col_map["activity_indicator"]),
            max_discount = row.get(col_map["max_discount"])
        )
        products.append(product)
        print(product.excel_line)

    return products, messages, col_map


def load_clothing(df: pd.DataFrame, header_row) -> tuple[list[Clothing], list[tuple[str, str]]]:
    """Load the new clothing file into a list of Clothing class objects"""
    # expected_headers = [name for sublist in CLOTHING_HEADER_MAP.values() for name in sublist]
    # header_row = detect_header_row(df, expected_headers)  # <- use your existing detection function
    # df = pd.read_excel(path, header=header_row)
    # df.columns = df.columns.str.lower().str.strip().str.replace(" ", "")
    # df.columns = [normalize_header(col) for col in df.columns]

    messages = []
    col_map = {}
    used_columns = set()

    # # Step 1: Resolve headers
    for key in CLOTHING_HEADER_MAP:
        col, message, type = find_header(df, CLOTHING_HEADER_MAP[key], used_columns)
        if col:
            used_columns.add(col)
        col_map[key] = col  # May be None if not found
        if message:
            messages.append((message, type))



    # Step 2: Check for required columns
    for key, col in col_map.items():
        if col is None and key in ["style_code", "description"]:  # Add more keys if needed
            raise ValueError(f"Missing required column: {key}")

    # Step 3: Build clothing objects
    clothes = []
    for idx, row in df.iterrows():
        line_number = header_row + idx + 2
        clothing = Clothing(
            code=normalizer(row.get(col_map["style_code"])),
            description=row.get(col_map["description"]),
            size=row.get(col_map["size"]),
            colour=row.get(col_map["colour"]),
            subgroup=row.get(col_map["subgroup"]),
            supplier_code=row.get(col_map["3_digit_supplier"]),
            season=row.get(col_map["season"]),
            main_supplier=row.get(col_map["main_supplier"]),
            cost_price=row.get(col_map["cost_price"]),
            barcode=row.get(col_map["barcode"]),
            vat_rate=row.get(col_map["vat_rate"]),
            rrp=row.get(col_map["rrp"]),
            sell_price=row.get(col_map["sell_price"]),
            stg_price=row.get(col_map["stg_price"]),
            tariff=row.get(col_map["tariff"]),
            brand=row.get(col_map["brand"]),
            product_type=row.get(col_map["product_type"]),
            web=row.get(col_map["web"]),
            country=row.get(col_map["country"]),
            country_code=row.get(col_map["country_code"]),
            idx=line_number
        )
        clothes.append(clothing)

    return clothes, messages, col_map





def load_prices(df: pd.DataFrame, header_row) -> tuple[list[Product], list[tuple[str, str]]]:
    """Load the new product file into a list of Product class objects"""
    # expected_headers = [name for sublist in PRODUCT_HEADER_MAP.values() for name in sublist]

    messages = []
    
    # Pre-resolve all needed column names
    used_columns = set()
    col_map = {}
    for key in PRICE_AMENDMENT_HEADER_MAP:
        col, message, type = find_header(df, PRICE_AMENDMENT_HEADER_MAP[key], used_columns)
        if col:
            used_columns.add(col)
        col_map[key] = col  # May be None if not found
        if message:
            messages.append((message, type))

    # Build Product objects using resolved column names
    products = []
    for idx, row in df.iterrows():
        line_number = header_row + idx + 2
        product = Price_Amend(
            code = normalizer(row.get(col_map["plu_code"])),
            description = row.get(col_map["description"]),
            main_supplier = row.get(col_map["main_supplier"]),
            cost_price = row.get(col_map["cost_price"]),
            rrp = row.get(col_map["rrp"]),
            sell_price = row.get(col_map["sell_price"]),
            stg_price = row.get(col_map["stg_price"]),
            idx = line_number
        )
        products.append(product)

    return products, messages, col_map





def read_column(df: pd.DataFrame, possible_names, used_columns=None) -> list:
    """Find the given column name and return that column as a list.
    Converts all objects to strings"""
    if isinstance(possible_names, str):
        possible_names = [possible_names]

    if used_columns is None:
        used_columns = set()

    col_name, msg, msg_type = find_header(df, possible_names, used_columns)
    if col_name is not None and col_name in df.columns:
        used_columns.add(col_name)
        return df[col_name].dropna().apply(normalizer).tolist(), msg, msg_type
    return [], msg, msg_type
