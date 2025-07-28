import pandas as pd
import io
from converter import *
from utils.headers import *
from utils.normalizer import normalize_header
from utils.validators import *
from auto_fixes.fix_products import update_all_products
from auto_fixes.fix_clothing import update_all_clothing
from auto_fixes.fix_prices import update_all_prices
from email_tools.email_automation import send_email
from email_tools.email_error_collection import *
from email_tools.excel_template import *
from classes.product_class import Product 


FULL_LIST_FILE = "1_Spreadsheets/CodesList.csv"
FULL_SUPPLIER_FILE = "1_Spreadsheets/Supplier Code List.CSV"



def process_product_file(new_file, sender_email, message_id, thread_id, subject):
    
    expected_headers = [name for sublist in PRODUCT_HEADER_MAP.values() for name in sublist]
    header_row = detect_header_row(new_file, expected_headers)
    df = df[~df.apply(lambda row: all((pd.isna(x) or str(x).strip() == "") for x in row), axis=1)]
    df = pd.read_excel(new_file, header=header_row)
    df.columns = [normalize_header(c) for c in df.columns]

    # Check headers
    check_missing_headers(df, PRODUCT_HEADER_MAP)

    # Auto-fixes
    df, auto_changes, cell_flags, vat_manual_msg = update_all_products(df)                       

    # Load products
    products, messages, col_map = load_products(df, header_row)
    missing = []
    for message, msg_type in messages:
        if msg_type == "error":
            missing.append(message)
    if missing:
        print(f"Searched for, but couldn't find columns: {missing} in new file upload.")


    # Load full PLU + supplier list
    full_list_df = pd.read_csv(FULL_LIST_FILE)
    full_list_df.columns = [normalize_header(c) for c in full_list_df.columns]
    full_list_barcode, *_ = read_column(full_list_df, PRODUCT_HEADER_MAP["barcode"])
    full_list_plu, *_ = read_column(full_list_df, PRODUCT_HEADER_MAP["plu_code"])
    full_supplier_df = pd.read_csv(FULL_SUPPLIER_FILE)
    full_supplier_codes = full_supplier_df.iloc[:, 0].dropna().tolist()


    # Error checks
    manual_flags, manual_summary = collect_product_errors(df, products, col_map, full_list_plu, full_list_barcode, full_supplier_codes)
    if vat_manual_msg:
        manual_summary.extend([["Unrecognized VAT", msg] for msg in vat_manual_msg])        
    

    cell_flags["manual"].extend(manual_flags["manual"])
    if not manual_summary:
        print("no new manual errors")
        manual_summary.append(["None", "No issues found"])
    
    
# Step 3: Build summary
    auto_summary = []
    for category, items in auto_changes.items():
        for item in items:
            auto_summary.append([category, item])
    if not auto_summary:
        auto_summary.append(["None", "No automatic fixes applied"])

    manual_checks = pd.DataFrame(manual_summary, columns=["Category", "Message"])
    auto_checks = pd.DataFrame(auto_summary, columns=["Category", "Message"])



# Step 4: Generate output file (placeholder — will replace with clothing_excel or similar)
    buffer = product_excel(df, manual_checks, auto_checks, cell_flags)
    # print(f"A BUFFER ====\n {buffer}")


# Step 5: Email summary body
    body = "✅ File validated.\n\n"

    body += "=== Unresolved Manual Errors ===\n"
    if manual_summary:
        category_counts = defaultdict(int)
        for category, _ in manual_summary:
            category_counts[category] += 1
        for category, count in category_counts.items():
            body += f"- {category}: {count} issue(s)\n"
    else:
        body += "- No manual issues found.\n"
    body += "\n"

    body += "=== Automatic Fixes ===\n"
    if any(auto_changes.values()):
        for category, issues in auto_changes.items():
            if issues:
                body += f"- {category}: {len(issues)} issue(s)\n"
    else:
        body += "- No auto-fixes applied.\n"


    body += "\n\nSee attached file for details."

    
    print("✅ Done processing product file.")
    print("📨 About to send email...")
    print("📨 body TYPE:", type(body))


    # Send Email.
    try: 
        send_email(
            to=sender_email,
            subject=subject,
            body=body,
            attachment_buffer=buffer,
            file_name=f"Fixed-{new_file.name}",
            in_reply_to=message_id,
            thread_id=thread_id
        )

    except:
        send_email(
            to=sender_email,
            subject=subject,
            body=f"There was an error processing the clothing file:\n\n",
            in_reply_to=message_id,
            thread_id=thread_id
        )





def process_clothing_file(new_file, sender_email, message_id, thread_id, subject):
# Step 1: Read and normalize new clothing file
    expected_headers = [name for sublist in CLOTHING_HEADER_MAP.values() for name in sublist]
    header_row = detect_header_row(new_file, expected_headers)
    df = pd.read_excel(new_file, header=header_row)
    df.columns = [normalize_header(c) for c in df.columns]

    print(f"OK HERE IS STEP 1 WITH THE DATAFRAME: {df.head(5)}")

    # Header validation
    check_missing_headers(df, CLOTHING_HEADER_MAP)

    # Auto-fixes
    df, auto_changes, cell_flags, vat_manual_msg = update_all_clothing(df)
    print(f"OK HERE IS DF: {df.head(5)} \n and now we have some auto change: {auto_changes}\n and also some cell flags: {cell_flags}")

    # Load clothing objects
    clothes, messages, col_map = load_clothing(df, header_row)


    missing = []
    for message, msg_type in messages:
        if msg_type == "error":
            missing.append(message)
    if missing:
        print(f"Searched for, but couldn't find columns: {missing} in clothing file upload.")

    # Load reference data
    full_list_df = pd.read_csv(FULL_LIST_FILE)
    full_list_df.columns = [normalize_header(c) for c in full_list_df.columns]
    full_list_barcode, *_ = read_column(full_list_df, CLOTHING_HEADER_MAP["barcode"])
    full_list_style, *_ = read_column(full_list_df, PRODUCT_HEADER_MAP["plu_code"])  # clothing uses product-style overlap here

    full_supplier_df = pd.read_csv(FULL_SUPPLIER_FILE)
    full_supplier_codes = full_supplier_df.iloc[:, 0].dropna().tolist()

    # print(f"full list style codes: {full_list_style[:5]}\n\n")
    # print(f"Full list of barcodes: {full_list_barcode[:5]}\n\n")
    # print(f"full list of supplier codes: {full_supplier_codes[:5]}\n\n")



# Step 2: Error checking
    manual_flags, manual_summary = collect_clothing_errors(df, clothes, col_map, full_list_style, full_list_barcode, full_supplier_codes)
    if vat_manual_msg:
        manual_summary.extend([["Unrecognized VAT", msg] for msg in vat_manual_msg])

    print(f"collecting errors\n================")
    print(f"manual_flags: {manual_flags}\n\n")
    print(f"manual summary: {manual_summary}\n\n")
        
    cell_flags["manual"].extend(manual_flags["manual"])
    print(f"just extended the cell flags with manual falgs: {cell_flags}")

    if not manual_summary:
        print("no new manual errors")
        manual_summary.append(["None", "No issues found"])



# Step 3: Build summary
    auto_summary = []
    for category, items in auto_changes.items():
        for item in items:
            auto_summary.append([category, item])
    if not auto_summary:
        auto_summary.append(["None", "No automatic fixes applied"])

    manual_checks = pd.DataFrame(manual_summary, columns=["Category", "Message"])
    auto_checks = pd.DataFrame(auto_summary, columns=["Category", "Message"])



# Step 4: Generate output file (placeholder — will replace with clothing_excel or similar)
    buffer = clothing_excel(df, manual_checks, auto_checks, cell_flags)
    # print(f"A BUFFER ====\n {buffer}")



# Step 5: Email summary body
    body = "✅ File validated.\n\n"

    body += "=== Unresolved Manual Errors ===\n"
    if manual_summary:
        category_counts = defaultdict(int)
        for category, _ in manual_summary:
            category_counts[category] += 1
        for category, count in category_counts.items():
            body += f"- {category}: {count} issue(s)\n"
    else:
        body += "- No manual issues found.\n"
    body += "\n"


    body += "=== Automatic Fixes ===\n"
    if any(auto_changes.values()):
        for category, issues in auto_changes.items():
            if issues:
                body += f"- {category}: {len(issues)} issue(s)\n"
    else:
        body += "- No auto-fixes applied.\n"


    body += "\n\nSee attached file for details."

    
    print("✅ Done processing clothing file.")
    print("📨 About to send email...")
    print("📨 body TYPE:", type(body))


    # Send Email.
    try: 
        send_email(
            to=sender_email,
            subject=subject,
            body=body,
            attachment_buffer=buffer,
            file_name=f"Fixed-{new_file.name}",
            in_reply_to=message_id,
            thread_id=thread_id
        )

    except:
        send_email(
            to=sender_email,
            subject=subject,
            body=f"There was an error processing the clothing file:\n\n",
            in_reply_to=message_id,
            thread_id=thread_id
        )




def process_price_amendment_file(new_file, sender_email, message_id, thread_id, subject):
        
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



# Step 2: Load as Product class objects ----------
    prices, messages, col_map = load_prices(df, header_row) # was new file
    missing = []
    for message, msg_type in messages:
        if msg_type == "alert":
            st.success(message)
        elif msg_type == "error":
            missing.append(message)
    if missing:
        print(f"Searched for, but couldn't find columns: {missing} in new file upload.")


# Step 3: Load PLU list ---------
    # full_list_df = pd.read_excel(full_list_file)
    full_list_df = pd.read_csv(FULL_LIST_FILE)
    full_list_df.columns = [normalize_header(column) for column in full_list_df.columns]
    full_list_plu, message, msg_type = read_column(full_list_df, PRODUCT_HEADER_MAP["plu_code"], used_columns=None)
    
    full_supplier_df = pd.read_csv(FULL_SUPPLIER_FILE)
    full_supplier_codes = full_supplier_df.iloc[:, 0].dropna().tolist()

    missing = []
    if message:
        if msg_type == "error":
            missing.append(message)
    if missing:
        print(f"Searched for, but couldn't find columns: {missing} in full list upload.")



# Checks
    st.header("Checks")

    flags_update, manual_summary = collect_price_errors(df, prices, col_map, full_list_plu, full_supplier_codes)
    cell_flags["manual"].extend(flags_update["manual"])
    print(f"FLAGS UPDATE \n {flags_update}")
    print(f"MANUAL SUMMARY\n {manual_summary}")
    print(f"CELL FLAGS \n {cell_flags}")

    print("Auto-Changes")


# Create buffer and excel

    manual_checks = pd.DataFrame(manual_summary, columns=["Category", "Message"])
    auto_checks = pd.DataFrame([
        [category, item]
        for category, items in auto_changes.items()
        for item in items
    ], columns=["Category", "Message"]) if auto_changes else pd.DataFrame([["None", "No automatic fixes applied"]], columns=["Category", "Message"])

    buffer = product_excel(df, manual_checks, auto_checks, cell_flags)


# Step 5: Email summary body
    body = "✅ File validated.\n\n"

    body += "=== Unresolved Manual Errors ===\n"
    if manual_summary:
        category_counts = defaultdict(int)
        for category, _ in manual_summary:
            category_counts[category] += 1
        for category, count in category_counts.items():
            body += f"- {category}: {count} issue(s)\n"
    else:
        body += "- No manual issues found.\n"
    body += "\n"


    body += "=== Automatic Fixes ===\n"
    if any(auto_changes.values()):
        for category, issues in auto_changes.items():
            if issues:
                body += f"- {category}: {len(issues)} issue(s)\n"
    else:
        body += "- No auto-fixes applied.\n"


    body += "\n\nSee attached file for details."

    
    print("✅ Done processing product file.")
    print("📨 About to send email...")
    print("📨 body TYPE:", type(body))


    # Send Email.
    try: 
        send_email(
            to=sender_email,
            subject=subject,
            body=body,
            attachment_buffer=buffer,
            file_name=f"Fixed-{new_file.name}",
            in_reply_to=message_id,
            thread_id=thread_id
        )

    except:
        send_email(
            to=sender_email,
            subject=subject,
            body=f"There was an error processing the clothing file:\n\n",
            in_reply_to=message_id,
            thread_id=thread_id
        )



