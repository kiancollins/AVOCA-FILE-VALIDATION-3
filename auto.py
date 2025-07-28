from pywinauto import Application, Desktop
from pywinauto.keyboard import send_keys
import pyautogui
import time
import os
from utils.contants import *
"""
venv312\Scripts\activate
"""



MERIDIAN = r"C:\Users\collins-kian\Desktop\LoadBulk.exe - Shortcut.lnk"
GARDEN_FRESH = r"C:\Users\collins-kian\Desktop\AVOCA-FILE-VALIDATION-3-main\fixed_files\Fixed-0107025_GARDEN_FRESH.xlsx"

def uploader(file_path):

    os.startfile(MERIDIAN)
    time.sleep(7)


    # dlg = Desktop(backend="uia").window(title="Meridian Bulk Load from File or Spreadsheet V6.35")
       
    # select sheet? > load template > desktop > product > open file > liveload


    send_keys(str(file_path), with_spaces=True)
    send_keys("{ENTER}")
    time.sleep(3)

    try:
        select_sheet = pyautogui.locateOnScreen(r"C:\Users\collins-kian\Desktop\AVOCA-FILE-VALIDATION-3-main\z_images\select_sheet.png", confidence=0.7)
        if select_sheet:
            pyautogui.click(pyautogui.center(select_sheet))
            time.sleep(2)
    except:
        print("select_sheet.png not found. Skipping.")
        time.sleep(1)

    load_template = pyautogui.locateOnScreen(r"C:\Users\collins-kian\Desktop\AVOCA-FILE-VALIDATION-3-main\z_images\load_template.png", confidence=0.7)
    pyautogui.click(pyautogui.center(load_template))
    time.sleep(1.5)

    desktop = pyautogui.locateOnScreen(r"C:\Users\collins-kian\Desktop\AVOCA-FILE-VALIDATION-3-main\z_images\desktop.png", confidence=0.7)
    pyautogui.click(pyautogui.center(desktop))
    time.sleep(1.5)

    product_template = pyautogui.locateOnScreen(r"C:\Users\collins-kian\Desktop\AVOCA-FILE-VALIDATION-3-main\z_images\product_template.png", confidence=0.7)
    pyautogui.click(pyautogui.center(product_template))
    time.sleep(1.5)

    open_file = pyautogui.locateOnScreen(r"C:\Users\collins-kian\Desktop\AVOCA-FILE-VALIDATION-3-main\z_images\open_file.png", confidence=0.7)
    pyautogui.click(pyautogui.center(open_file))
    time.sleep(1.5)

    ok = pyautogui.locateOnScreen(r"C:\Users\collins-kian\Desktop\AVOCA-FILE-VALIDATION-3-main\z_images\ok.png", confidence=0.7)
    pyautogui.click(pyautogui.center(ok))
    time.sleep(1.5)

    live_load = pyautogui.locateOnScreen(r"C:\Users\collins-kian\Desktop\AVOCA-FILE-VALIDATION-3-main\z_images\live_load.png", confidence=0.7)
    pyautogui.click(pyautogui.center(live_load))
    time.sleep(1.5)

    send_keys("testing")
    send_keys("{ENTER}")


def main():
    uploader(GARDEN_FRESH)

if __name__ == "__main__":
    main()



# time.sleep(3)Bulk.exe-Shortcut.lnk

# dlg.print_control_identifiers()

"""
Control Identifiers:

Dialog - 'Meridian Bulk Load from File or Spreadsheet V6.35'    (L320, T163, R1600, B918)
['Dialog', 'Meridian Bulk Load from File or Spreadsheet V6.35Dialog', 'Meridian Bulk Load from File or Spreadsheet V6.35']
child_window(title="Meridian Bulk Load from File or Spreadsheet V6.35", control_type="Window")
   | 
   | Pane - ''    (L1434, T225, R1585, B346)
   | ['Pane', 'Pane0', 'Pane1']
   |
   | GroupBox - 'Select File to Load'    (L334, T215, R1415, B346)
   | ['Select File to LoadGroupBox', 'GroupBox', 'Select File to Load', 'GroupBox0', 'GroupBox1']
   | child_window(title="Select File to Load", auto_id="1", control_type="Group")
   |    | 
   |    | RadioButton - 'TAB Delimited'    (L574, T245, R755, B266)
   |    | ['TAB DelimitedRadioButton', 'RadioButton', 'TAB Delimited', 'RadioButton0', 'RadioButton1']
   |    | child_window(title="TAB Delimited", auto_id="2", control_type="RadioButton")
   |    |
   |    | RadioButton - 'CSV'    (L474, T245, R595, B266)
   |    | ['CSVRadioButton', 'CSV', 'RadioButton2']
   |    | child_window(title="CSV", auto_id="3", control_type="RadioButton")
   |    |
   |    | RadioButton - 'Excel '    (L344, T245, R465, B266)
   |    | ['Excel RadioButton', 'Excel ', 'RadioButton3']
   |    | child_window(title="Excel ", auto_id="4", control_type="RadioButton")
   |    |
   |    | Edit - ''    (L344, T285, R885, B318)
   |    | ['Edit', 'Edit0', 'Edit1']
   |    | child_window(auto_id="5", control_type="Edit")
   |    | 
   |    | Pane - ''    (L894, T265, R1005, B316)
   |    | ['Pane2']
   |    |
   |    | Pane - ''    (L1024, T265, R1135, B316)
   |    | ['Pane3']
   |    |
   |    | Pane - ''    (L1254, T265, R1395, B316)
   |    | ['Pane4']
   |
   | GroupBox - 'Field assignments '    (L334, T375, R1585, B909)
   | ['GroupBox2', 'Field assignments ', 'Field assignments GroupBox']
   | child_window(title="Field assignments ", auto_id="6", control_type="Group")
   |    | 
   |    | CheckBox - 'Set as default supplier (if applicable)'    (L1074, T685, R1365, B726)
   |    | ['Set as default supplier (if applicable)', 'Set as default supplier (if applicable)CheckBox', 'CheckBox', 'CheckBox0', 'CheckBox1']
   |    | child_window(title="Set as default supplier (if applicable)", auto_id="7", control_type="CheckBox")
   |    |
   |    | Pane - ''    (L1364, T415, R1465, B456)
   |    | ['Pane5']
   |    |
   |    | CheckBox - 'Validate Supplier Codes'    (L1074, T645, R1295, B686)
   |    | ['Validate Supplier CodesCheckBox', 'Validate Supplier Codes', 'CheckBox2']
   |    | child_window(title="Validate Supplier Codes", auto_id="8", control_type="CheckBox")
   |    |
   |    | CheckBox - 'Validate analysis group codes'    (L1074, T605, R1295, B646)
   |    | ['Validate analysis group codes', 'Validate analysis group codesCheckBox', 'CheckBox3']
   |    | child_window(title="Validate analysis group codes", auto_id="9", control_type="CheckBox")
   |    |
   |    | CheckBox - 'Create new PLU if does not exist'    (L1074, T515, R1275, B556)
   |    | ['Create new PLU if does not exist', 'Create new PLU if does not existCheckBox', 'CheckBox4']
   |    | child_window(title="Create new PLU if does not exist", auto_id="10", control_type="CheckBox")
   |    |
   |    | CheckBox - 'Update RRP Price'    (L1074, T565, R1275, B596)
   |    | ['CheckBox5', 'Update RRP PriceCheckBox', 'Update RRP Price']
   |    | child_window(title="Update RRP Price", auto_id="11", control_type="CheckBox")
   |    |
   |    | GroupBox - 'Barcode Validation'    (L774, T505, R1045, B736)
   |    | ['Barcode Validation', 'GroupBox3', 'Barcode ValidationGroupBox', 'Barcode Validation0', 'Barcode Validation1']
   |    | child_window(title="Barcode Validation", auto_id="12", control_type="Group")
   |    |    | 
   |    |    | CheckBox - 'Allow Code39/128'    (L794, T625, R1025, B666)
   |    |    | ['Allow Code39/128', 'Allow Code39/128CheckBox', 'CheckBox6']
   |    |    | child_window(title="Allow Code39/128", auto_id="13", control_type="CheckBox")
   |    |    |
   |    |    | CheckBox - 'Allow UPC'    (L794, T595, R1025, B636)
   |    |    | ['Allow UPC', 'Allow UPCCheckBox', 'CheckBox7']
   |    |    | child_window(title="Allow UPC", auto_id="14", control_type="CheckBox")
   |    |    | 
   |    |    | CheckBox - 'Allow EAN13'    (L794, T565, R1025, B606)
   |    |    | ['Allow EAN13', 'Allow EAN13CheckBox', 'CheckBox8']
   |    |    | child_window(title="Allow EAN13", auto_id="15", control_type="CheckBox")
   |    |    |
   |    |    | CheckBox - 'Allow EAN8'    (L794, T535, R1025, B576)
   |    |    | ['Allow EAN8CheckBox', 'Allow EAN8', 'CheckBox9']
   |    |    | child_window(title="Allow EAN8", auto_id="16", control_type="CheckBox")
   |    |    |
   |    |    | CheckBox - 'Format UPC(12) to EAN(13)'    (L794, T685, R1025, B726)
   |    |    | ['Format UPC(12) to EAN(13)', 'Format UPC(12) to EAN(13)CheckBox', 'CheckBox10']
   |    |    | child_window(title="Format UPC(12) to EAN(13)", auto_id="17", control_type="CheckBox")
   |    |
   |    | ComboBox - 'Barcode Validation'    (L774, T425, R1345, B455)
   |    | ['ComboBox', 'Barcode Validation2', 'Barcode ValidationComboBox']
   |    | child_window(title="Barcode Validation", auto_id="18", control_type="ComboBox")
   |    |    | 
   |    |    | Edit - 'Barcode Validation'    (L778, T429, R1321, B452)
   |    |    | ['Edit2']
   |    |    | child_window(title="Barcode Validation", auto_id="1001", control_type="Edit")
   |    |    | 
   |    |    | Button - 'Open'    (L1321, T428, R1342, B453)
   |    |    | ['Button', 'OpenButton', 'Open']
   |    |    | child_window(title="Open", auto_id="DropDown", control_type="Button")
   |    |
   |    | Pane - ''    (L344, T425, R745, B896)
   |    | ['Pane6']
   |    | child_window(auto_id="82729392", control_type="Pane")
   |    |
   |    | Pane - ''    (L774, T845, R965, B896)
   |    | ['Pane7']
   |    | 
   |    | Pane - ''    (L974, T845, R1165, B896)
   |    | ['Pane8']
   |    |
   |    | Pane - ''    (L1384, T845, R1575, B896)
   |    | ['Pane9']
   |    |
   |    | Pane - ''    (L1474, T415, R1575, B456)
   |    | ['Pane10']
   |
   | TitleBar - ''    (L324, T168, R1597, B197)
   | ['TitleBar']
"""