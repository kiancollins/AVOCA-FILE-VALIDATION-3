import pandas as pd
import io






def product_excel(df: pd.DataFrame, manual_checks:pd.DataFrame, auto_checks:pd.DataFrame, cell_flags:dict):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Fixed Data")
        manual_checks.to_excel(writer, index=False, sheet_name="Manual Checks")
        auto_checks.to_excel(writer, index=False, sheet_name="Automatic Checks")

        workbook = writer.book
        worksheet = writer.sheets["Fixed Data"]

        header_format = workbook.add_format({
                    'bold': True, 'valign': 'center',
                    'fg_color': "#82ABD7", 'border': 1
                })
        auto_format = workbook.add_format({'bg_color': "#C8F4D1"})     # Light green
        manual_format = workbook.add_format({'bg_color': "#FBBAC2"})   # Light red


        # Apply header formatting
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Auto cell highlights
        for row, col in cell_flags.get("auto", []):
            worksheet.write(row+1, col, df.iat[row, col], auto_format)

        # Manual cell highlights
        for row, col in cell_flags.get("manual", []):
            worksheet.write(row+1, col, df.iat[row, col], manual_format)       

        writer.sheets["Fixed Data"].set_column("A:A", 15)
        writer.sheets["Fixed Data"].set_column("B:B", 50)
        writer.sheets["Fixed Data"].set_column("C:C", 8)
        writer.sheets["Fixed Data"].set_column("D:D", 12)
        writer.sheets["Fixed Data"].set_column("E:E", 8)
        writer.sheets["Fixed Data"].set_column("F:F", 12)
        writer.sheets["Fixed Data"].set_column("H:H", 15)
        writer.sheets["Fixed Data"].set_column("I:J", 8)
        writer.sheets["Fixed Data"].set_column("K:M", 10)

        writer.sheets["Manual Checks"].set_column("A:A", 40)
        writer.sheets["Manual Checks"].set_column("B:B", 150)
        writer.sheets["Automatic Checks"].set_column("A:A", 40)
        writer.sheets["Automatic Checks"].set_column("B:B", 150)

    buffer.seek(0)
    return buffer





def clothing_excel(df: pd.DataFrame, manual_checks: pd.DataFrame, auto_checks: pd.DataFrame, cell_flags: dict):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Fixed Data")
        manual_checks.to_excel(writer, index=False, sheet_name="Manual Checks")
        auto_checks.to_excel(writer, index=False, sheet_name="Automatic Checks")

        workbook = writer.book
        worksheet = writer.sheets["Fixed Data"]

        # Format styles
        header_format = workbook.add_format({
            'bold': True, 'valign': 'center',
            'fg_color': "#82ABD7", 'border': 1
        })
        auto_format = workbook.add_format({'bg_color': "#C8F4D1"})     # Light green
        manual_format = workbook.add_format({'bg_color': "#FBBAC2"})   # Light red

        # Apply header formatting
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Apply auto cell highlights
        for row, col in cell_flags.get("auto", []):
            worksheet.write(row + 1, col, df.iat[row, col], auto_format)

        # Apply manual cell highlights
        for row, col in cell_flags.get("manual", []):
            worksheet.write(row + 1, col, df.iat[row, col], manual_format)


        writer.sheets["Fixed Data"].set_column("A:A", 15)
        writer.sheets["Fixed Data"].set_column("B:B", 50)
        writer.sheets["Fixed Data"].set_column("C:C", 8)
        writer.sheets["Fixed Data"].set_column("D:D", 15)
        writer.sheets["Fixed Data"].set_column("E:E", 8)
        writer.sheets["Fixed Data"].set_column("F:F", 12)
        writer.sheets["Fixed Data"].set_column("H:H", 14)
        writer.sheets["Fixed Data"].set_column("I:I", 8)
        writer.sheets["Fixed Data"].set_column("J:J", 16)
        writer.sheets["Fixed Data"].set_column("K:L", 8)
        writer.sheets["Fixed Data"].set_column("M:O", 12)
        writer.sheets["Fixed Data"].set_column("P:P", 16)
        writer.sheets["Fixed Data"].set_column("Q:Q", 12)
        writer.sheets["Fixed Data"].set_column("S:T", 16)



        writer.sheets["Manual Checks"].set_column("A:A", 40)
        writer.sheets["Manual Checks"].set_column("B:B", 150)
        writer.sheets["Automatic Checks"].set_column("A:A", 40)
        writer.sheets["Automatic Checks"].set_column("B:B", 150)

    buffer.seek(0)
    return buffer



