from email_tools.email_automation import fetch_attachment_from_email
from email_processor import *
import time



def check_and_process():
    new_file, file_type, sender_email, message_id, thread_id, subject = fetch_attachment_from_email()

    if new_file and file_type == "Product":
        process_product_file(new_file, sender_email, message_id, thread_id, subject)
        
    elif new_file and file_type == "Clothing":
        process_clothing_file(new_file, sender_email, message_id, thread_id, subject)

    elif new_file and file_type == "Price Amendment":
        process_price_amendment_file(new_file, sender_email, message_id, thread_id, subject)


if __name__ == "__main__":
    while True:
        print("🔁 Checking for new uploads...")
        check_and_process()
        time.sleep(15)
