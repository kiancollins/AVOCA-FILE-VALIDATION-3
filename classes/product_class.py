import streamlit as st


class Product:
    def __init__(self, code, description, subgroup, supplier_code, season, 
                main_supplier, cost_price, barcode, vat_rate, rrp, sell_price, stg_price, tariff, web, idx=None,
                # New Ones
                colour=None, size=None, supplier_item_code=None, purchase_unit_qty=None, purchase_unit_desc=None, 
                offer_analysis=None, product_type=None, brand_in_store=None, servicetype=None, item_type=None, 
                activity_indicator=None, max_discount=None,):
        

        self.plu_code = code
        self.description = description
        self.subgroup = subgroup
        self.supplier_code = supplier_code
        self.season = season
        self.main_supplier = main_supplier
        self.cost = cost_price
        self.barcode = barcode
        self.vat_rate = vat_rate
        self.rrp = rrp
        self.sell_price = sell_price
        self.stg_price = stg_price
        self.tariff = tariff
        self.web = web
        self.excel_line = idx
        # New Ones
        self.colour = colour
        self.size = size
        self.supplier_item_code = supplier_item_code
        self.purchase_unit_qty = purchase_unit_qty
        self.purchase_unit_desc = purchase_unit_desc
        self.offer_analysis = offer_analysis
        self.product_type = product_type
        self.brand_in_store = brand_in_store
        self.servicetype = servicetype
        self.item_type = item_type
        self.activity_indicator = activity_indicator
        self.max_discount = max_discount


    def __repr__(self):
        return f"Product {self.plu_code}: {self.description}"


    def __str__(self):
        return f"Product: {self.plu_code} | {self.description}"


    def plu_len(self):
        """ Checks if any products have a PLU Code length over 15"""
        if len(str(self.plu_code)) > 15:
            msg = f"Line {self.excel_line} \u00A0\u00A0|\u00A0\u00A0 Product: {self.plu_code} has PLU Code length of {len(str(self.plu_code))}. Must be under 15."
            return (msg, (self.excel_line - 2))

        

# Commented out because we have auto-fixing


    # def desc_len(self):
    #     """ Checks if any products have a Description length over 50"""
    #     if len(self.description) > 50:
    #         return(f"Line {self.excel_line} \u00A0\u00A0|\u00A0\u00A0 Product: {self.plu_code} has description length of {len(str(self.description))}. Must be under 50.")
    #         # print(f"Product: {self.plu_code} has description length of {len(str(self.description))}. Must be under 50.")
    #         # st.write(f"Product: {self.plu_code} has description length of {len(str(self.plu_code))}. Must be under 15.")


# Commented out because we have auto-fixing

    # def decimal_format(self):
    #     """Cost price, RRP, selling price, and trade price must all be 2 decimal places or less."""
    #     errors = []
    #     fields = { # Avoid errors if the field is empty with getattr
    #         'cost price': self.cost,
    #         'rrp': getattr(self, 'rrp', None),
    #         'selling price': getattr(self, 'sell_price', None),
    #         'trade price': getattr(self, 'stg_price', None)
    #     }

    #     for key, value in fields.items():
    #         if value != None:
    #             try:
    #                 decimal_value = Decimal(str(value))
    #                 if -(decimal_value.as_tuple().exponent) > 2:
    #                     errors.append(key)
    #             except Exception as e:
    #                 ... # Often times trade price (stg_price) will just be empty

    #     if len(errors) > 0:
    #         return f"Line {self.excel_line} \u00A0\u00A0|\u00A0\u00A0 Product: {self.plu_code} has decimal place error in {errors}. Must be 2 decimal places or less"
    #         # print(f"Product: {self.plu_code} has decimal place error in {errors}. Must be 2 decimal places or less")
    #         # st.write(f"Product: {self.plu_code} has decimal place error in {errors}. Must be 2 decimal places or less")










