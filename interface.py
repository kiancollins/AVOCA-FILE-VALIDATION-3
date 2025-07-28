import pandas as pd
import streamlit as st
import io

from converter import * 
from auto_fixes.fix_products import update_all_products
from auto_fixes.fix_clothing import update_all_clothing
from auto_fixes.fix_prices import update_all_prices
from email_tools.excel_template import *
from utils.validators import *
from utils.headers import *
from utils.checks import *

def display_results(title: str, errors: list[str]):
    if errors: 
        expander_title = f"{title} — {len(errors)} issue(s)"
        with st.expander(expander_title, expanded=False):
            for err in errors:
                st.markdown(f"- {err}")
    else:
        success_msg = ERROR_TYPES.get(title, f"{title} passed all checks.")
        st.success(success_msg)


st.title("New Product File Validation")
file_type = st.selectbox("Select File Type", ["Product", "Clothing", "Price Amendment"], key="select_file_type")

# File uploads
new_file = st.file_uploader(f"Upload New {file_type} File", type=["xlsx", "csv"],  key=f"upload_{file_type.lower()}")
full_list_file = "1_Spreadsheets/CodesList.csv"
full_supplier_file = "1_Spreadsheets/Supplier Code List.CSV"





# Proceed only if both files uploaded
if file_type == "Product" and new_file and full_list_file and full_supplier_file:

# Step 1: Read and normalize new product file for auto fixes ---------
    try:
        expected_headers = [name for sublist in PRODUCT_HEADER_MAP.values() for name in sublist]
        header_row = detect_header_row(new_file, expected_headers)
        df = pd.read_excel(new_file, header=header_row)
        print(df.head(5))
        df = df[~df.apply(lambda row: all((pd.isna(x) or str(x).strip() == "") for x in row), axis=1)]
        print("AFTER _________________")
        print(df.head(5))
        df.columns = [normalize_header(c) for c in df.columns]

        missing = check_missing_headers(df, PRODUCT_HEADER_MAP)                         # Check missing columns
        if not missing:
            st.success(f"All expected columns found in new file.")
        
    # Keep track of unrecognized header names
        unrecognized = unexpected_headers(df, PRODUCT_HEADER_MAP)
        if unrecognized:
            st.info(f"Unrecognized columns in file: {', '.join(unrecognized)}")

    # Apply auto-changes
        df, auto_changes, cell_flags, vat_manual_msg = update_all_products(df)                       

    except Exception as e:
        st.error(f"Error reading or fixing new product file: {e}. Excel format may be incorrect.")
        with open("1_Spreadsheets/Upload Template Types.xlsx", "rb") as file:
                st.download_button(
                    label="Upload Templates",
                    data=file,
                    file_name="Upload Template Types.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        st.stop()



# Step 2: Load as Product class objects ----------
    try:
        products, messages, col_map = load_products(df, header_row) # was new file
        missing = []
        for message, msg_type in messages:
            if msg_type == "alert":
                st.success(message)
            elif msg_type == "error":
                missing.append(message)
        if missing:
            st.warning(f"Searched for, but couldn't find columns: {missing} in new file upload.")

    except Exception as e:
        st.error(f"Error loading new product file into Product objects: {e}. Excel format may be incorrect.")
        with open("1_Spreadsheets/Upload Template Types.xlsx", "rb") as file:
                st.download_button(
                    label="Upload Templates",
                    data=file,
                    file_name="Upload Template Types.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        st.stop()


# Step 3: Load PLU, Barcode list ---------
    try:
        # full_list_df = pd.read_excel(full_list_file)
        full_list_df = pd.read_csv(full_list_file)
        full_list_df.columns = [normalize_header(column) for column in full_list_df.columns]
        full_list_barcode, message, msg_type = read_column(full_list_df, PRODUCT_HEADER_MAP["barcode"], used_columns=None)
        full_list_plu, message, msg_type = read_column(full_list_df, PRODUCT_HEADER_MAP["plu_code"], used_columns=None)
    
        full_supplier_df = pd.read_csv(full_supplier_file)
        full_supplier_codes = full_supplier_df.iloc[:, 0].dropna().tolist()

        missing = []
        if message:
            if msg_type == "alert":
                st.success(message)
            elif msg_type == "error":
                missing.append(message)
        if missing:
            st.warning(f"Searched for, but couldn't find columns: {missing} in full list upload.")

    except KeyError as e:
        st.error(f"Missing PLU column in full list: {e}")
        st.stop()
    except Exception as e:
        st.error(f"Error reading PLU Active List: {e}")
        st.stop()
    


# Step 4: Check for errors
    st.title("Checks")
    # print(df.head(10))
    print(f"all barcodes: {full_list_barcode[:5]}")
    flags_update, manual_summary = run_product_checks(df, products, col_map, full_list_plu, full_list_barcode, full_supplier_codes)
    cell_flags["manual"].extend(flags_update["manual"])

    # If no errors
    if not manual_summary:
        st.success("All checks passed. File is ready for upload.")
        manual_summary.append(["None", "No issues found"])


# Step 5: Auto Changes Summary
    st.header("Automatically Fixed Errors:")

    if any(auto_changes.values()):
        st.write("\n")
        for category, changes in auto_changes.items():
            if changes:
                with st.expander(f"{category} ({len(changes)} fixes)", expanded=False):
                    for change in changes:
                        st.markdown(f"- {change}")
    else:
        st.success("No Auto-changes needed.")


# Step 6: Create Buffer and Excel

    manual_checks = pd.DataFrame(manual_summary, columns=["Category", "Message"])
    auto_checks = pd.DataFrame([
        [category, item]
        for category, items in auto_changes.items()
        for item in items
    ], columns=["Category", "Message"]) if auto_changes else pd.DataFrame([["None", "No automatic fixes applied"]], columns=["Category", "Message"])

    buffer = product_excel(df, manual_checks, auto_checks, cell_flags)

    st.download_button(
        label="Download Fixed Version",
        data=buffer.getvalue(),
        file_name=f"Fixed-{new_file.name}",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )






elif file_type == "Clothing" and new_file and full_list_file and full_supplier_file:
# Step 1: Read and normalize new clothing file for auto fixes ---------

    try:
        expected_headers = [name for sublist in CLOTHING_HEADER_MAP.values() for name in sublist]
        header_row = detect_header_row(new_file, expected_headers)
        df = pd.read_excel(new_file, header=header_row)
        df.columns = [normalize_header(c) for c in df.columns]

        missing = check_missing_headers(df, CLOTHING_HEADER_MAP)                         # Check missing columns
        if missing:
            st.warning(f"Columns not found in new file: {', '.join(missing)}")
        else:
            st.success(f"All expected columns found in new file.")
        
    # Keep track of unrecognized header names
        unrecognized = unexpected_headers(df, CLOTHING_HEADER_MAP)
        if unrecognized:
            st.info(f"Unrecognized columns in file: {', '.join(unrecognized)}")

    # Apply auto fixes
        df, auto_changes, cell_flags, vat_manual_msg = update_all_clothing(df)    

    except Exception as e:
        st.error(f"Error reading or fixing new clothing file: {e}. Excel format may be incorrect.")
        with open("1_Spreadsheets/Upload Template Types.xlsx", "rb") as file:
            st.download_button(
                label="Upload Templates",
                data=file,
                file_name="Upload Template Types.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        st.stop()

# Step 2: Load as Clothing class objects ----------
    try:
        clothes, messages, col_map = load_clothing(df, header_row)
        missing = []
        for message, msg_type, in messages:
            if msg_type == "alert":
                st.success(message)
            elif msg_type == "error":
                missing.append(message)
        if missing:
            st.warning(f"Searched for, but couldn't find columns: {missing} in clothing file upload.")

    except Exception as e:
        st.error(f"Error loading new clothing file into Clothing objects: {e}. Excel format may be incorrect.")
        with open("1_Spreadsheets/Upload Template Types.xlsx", "rb") as file:
            st.download_button(
                label="Upload Templates",
                data=file,
                file_name="Upload Template Types.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        st.stop()

# Step 3: Load Clothing list ---------
    try:
        # full_list_df = pd.read_excel(full_list_file)
        full_list_df = pd.read_csv(full_list_file)
        full_list_df.columns = [normalize_header(c) for c in full_list_df.columns]
        full_list_barcode, message, msg_type = read_column(full_list_df, CLOTHING_HEADER_MAP["barcode"])
        full_list_style, message, msg_type = read_column(full_list_df, PRODUCT_HEADER_MAP["plu_code"])

        full_supplier_df = pd.read_csv(full_supplier_file)
        full_supplier_codes = full_supplier_df.iloc[:, 0].dropna().tolist()

        if message:
            if msg_type == "alert":
                st.success(message)
            elif msg_type == "error":
                st.error(message)

    except KeyError as e:
        st.error(f"Missing Style Code column in full items list: {e}")
        st.stop()
    except Exception as e:
        st.error(f"Error reading full items list: {e}")
        st.stop()


# Step 4: Check for errors
    st.header("Checks")

    flags_update, manual_summary = run_clothing_checks(df, clothes, col_map, full_list_style, full_list_barcode, full_supplier_codes)
    cell_flags["manual"].extend(flags_update["manual"])

# If no errors
    if not manual_summary:
        st.success("All checks passed. File is ready for upload.")
        manual_summary.append(["None", "No issues found"])



# Step 5: Auto fixing ------------------
    st.header("Auto-Changes")

    if any(auto_changes.values()):
        st.write("\n")
        for category, changes in auto_changes.items():
            if changes:
                with st.expander(f"{category} ({len(changes)} fixes)", expanded=False):
                    for change in changes:
                        st.markdown(f"- {change}")

        auto_summary = []
        for category, items in auto_changes.items():
            for item in items:
                auto_summary.append([category, item])
        if not auto_summary:
            auto_summary.append(["None", "No automatic fixes applied"])

        manual_checks = pd.DataFrame(manual_summary, columns=["Category", "Message"])
        auto_checks = pd.DataFrame(auto_summary, columns=["Category", "Message"])



# Step 6: Build Excel
        buffer = clothing_excel(df, manual_checks, auto_checks, cell_flags)

        st.download_button(
            label="Download Fixed Version",
            data=buffer.getvalue(),
            file_name= f"Fixed-{new_file.name}",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.success("No Auto-changes needed.")





elif file_type == "Price Amendment" and new_file and full_list_file and full_supplier_file:
# Step 1: Read into dataframe, normalize headers, auto fixes
    try:
        expected_headers = [name for sublist in PRICE_AMENDMENT_HEADER_MAP.values() for name in sublist]
        header_row = detect_header_row(new_file, expected_headers)
        df = pd.read_excel(new_file, header=header_row)
        df.columns = [normalize_header(c) for c in df.columns]
        print(f"dataframe: {df.head(5)}")

        missing = check_missing_headers(df, PRICE_AMENDMENT_HEADER_MAP)                         # Check missing columns
        if not missing:
            st.success(f"All expected columns found in new file.")
        print(f"MISSING:\n {missing}")

    # Keep track of unrecognized header names
        unrecognized = unexpected_headers(df, PRICE_AMENDMENT_HEADER_MAP)
        if unrecognized:
            st.info(f"Unrecognized columns in file: {', '.join(unrecognized)}")
        print(f"UNRECORGNIZED:\n {unrecognized}")

    # Apply auto-changes
        df, auto_changes, cell_flags = update_all_prices(df)  
        print(f"UPDATING ALL\n\n")
        print(f"AUTO CHANGES \n{auto_changes}")
        print(f"CELL FLAGS \n{cell_flags}")  
   

    except Exception as e:
        st.error(f"Error reading or fixing new product file: {e}. Excel format may be incorrect.")
        with open("1_Spreadsheets/Upload Template Types.xlsx", "rb") as file:
            st.download_button(
                label="Upload Templates",
                data=file,
                file_name="Upload Template Types.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        st.stop()


# Step 2: Load as Product class objects ----------
    try:
        products, messages, col_map = load_prices(df, header_row) # was new file
        missing = []
        for message, msg_type in messages:
            if msg_type == "alert":
                st.success(message)
            elif msg_type == "error":
                missing.append(message)
        if missing:
            st.warning(f"Searched for, but couldn't find columns: {missing} in new file upload.")


    except Exception as e:
        st.error(f"Error loading new product file into Product objects: {e}. Excel format may be incorrect")
        with open("1_Spreadsheets/Upload Template Types.xlsx", "rb") as file:
            st.download_button(
                label="Upload Templates",
                data=file,
                file_name="Upload Template Types.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        st.stop()

# Step 3: Load PLU list ---------
    try:
        # full_list_df = pd.read_excel(full_list_file)
        full_list_df = pd.read_csv(full_list_file)
        full_list_df.columns = [normalize_header(column) for column in full_list_df.columns]
        full_list_plu, message, msg_type = read_column(full_list_df, PRODUCT_HEADER_MAP["plu_code"], used_columns=None)
        
        full_supplier_df = pd.read_csv(full_supplier_file)
        full_supplier_codes = full_supplier_df.iloc[:, 0].dropna().tolist()

        missing = []
        if message:
            if msg_type == "alert":
                st.success(message)
            elif msg_type == "error":
                missing.append(message)
        if missing:
            st.warning(f"Searched for, but couldn't find columns: {missing} in full list upload.")

    except KeyError as e:
        st.error(f"Missing PLU column in full list: {e}")
        st.stop()
    except Exception as e:
        st.error(f"Error reading PLU Active List: {e}")
        st.stop()


# Checks
    st.header("Checks")

    flags_update, manual_summary = run_price_checks(df, products, col_map, full_list_plu, full_supplier_codes)
    cell_flags["manual"].extend(flags_update["manual"])
    print(f"FLAGS UPDATE \n {flags_update}")
    print(f"MANUAL SUMMARY\n {manual_summary}")
    print(f"CELL FLAGS \n {cell_flags}")

    st.header("Auto-Changes")

    if any(auto_changes.values()):
            for category, changes in auto_changes.items():
                if changes:
                    with st.expander(f"{category} ({len(changes)} fixes)", expanded=False):
                        for change in changes:
                            st.markdown(f"- {change}")
    else:
        st.success("No Auto-changes needed.")


# Create buffer and excel

    manual_checks = pd.DataFrame(manual_summary, columns=["Category", "Message"])
    auto_checks = pd.DataFrame([
        [category, item]
        for category, items in auto_changes.items()
        for item in items
    ], columns=["Category", "Message"]) if auto_changes else pd.DataFrame([["None", "No automatic fixes applied"]], columns=["Category", "Message"])

    buffer = product_excel(df, manual_checks, auto_checks, cell_flags)

    st.download_button(
        label="Download Fixed Version",
        data=buffer.getvalue(),
        file_name=f"Fixed-{new_file.name}",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


