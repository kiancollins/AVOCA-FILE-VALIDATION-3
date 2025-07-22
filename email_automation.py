import os
import base64
import re
from io import BytesIO
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from email.message import EmailMessage

# === Constants ===
BASE_DIR = os.path.dirname(__file__)
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(BASE_DIR, 'token.json')
SAVE_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "test_uploads"))
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']





def list_labels():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    service = build('gmail', 'v1', credentials=creds)
    results = service.users().labels().list(userId='me').execute()
    for label in results.get('labels', []):
        print(f"{label['name']} => {label['id']}")




# === Main function: Test email read ===
def main():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh()
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    # List latest 5 messages (for debugging)
    results = service.users().messages().list(userId='me', maxResults=5).execute()
    messages = results.get('messages', [])

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        snippet = msg_data.get('snippet')
        print(f"Snippet: {snippet}\n")




def get_sender_email(headers):
    for header in headers:
        if header["name"].lower() == "from":
            raw = header["value"]
            match = re.search(r'<(.+?)>', raw)
            return match.group(1) if match else raw
    return None




# === Fetch Email Function ===
def fetch_attachment_from_email():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    service = build('gmail', 'v1', credentials=creds)

    # Only look for emails with this label
    result = service.users().messages().list(
        userId='me',
        q='label:AVOCA_UPLOAD has:attachment',
        maxResults=10
    ).execute()

    messages = result.get('messages', [])

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_data['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '').lower()

        if any(x in subject for x in ['product', 'clothing', 'price amendment']):
            if 'product' in subject:
                file_type = 'Product'
            elif 'clothing' in subject:
                file_type = 'Clothing'
            elif 'price amendment' in subject:
                file_type = 'Price Amendment'

            message_id = next((h['value'] for h in headers if h['name'].lower() == 'message-id'), None)
            thread_id = msg_data.get('threadId')

            for part in msg_data['payload'].get('parts', []):
                if part['filename']:
                    attachment_id = part['body'].get('attachmentId')
                    if attachment_id:
                        attachment = service.users().messages().attachments().get(
                            userId='me',
                            messageId=msg['id'],
                            id=attachment_id
                        ).execute()

                        data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))

                        os.makedirs(SAVE_DIR, exist_ok=True)
                        save_path = os.path.join(SAVE_DIR, part['filename'])
                        with open(save_path, 'wb') as f:
                            f.write(data)

                        buffer = BytesIO(data)
                        buffer.name = part['filename']
                        sender_email = get_sender_email(msg_data["payload"]["headers"])


                        if sender_email.lower() == "kchawks39@gmail.com":
                            continue
                        # ✅ Remove the AVOCA_UPLOAD label and add UPLOAD_COMPLETE
                        service.users().messages().modify(
                            userId='me',
                            id=msg['id'],
                            body={
                                'removeLabelIds': ['UNREAD' , 'Label_2375133861207306759'],       #Remove AVOCA_UPLOAD + unread
                                'addLabelIds': ['Label_5752259579548408339']                 # Add AVOCA_COMPLETE
                            }
                        ).execute()


                        print(f"✅ Saved: {part['filename']} | Type: {file_type}")
                        return buffer, file_type, sender_email, message_id, thread_id, subject

    print("No matching labeled emails with attachments.")
    return None, None, None, None, None, None




def send_email(to, subject, body, attachment_buffer=None, file_name="attachment.xlsx", in_reply_to=None, thread_id=None):
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    service = build('gmail', 'v1', credentials=creds)

    message = EmailMessage()
    message.set_content(body)
    message['To'] = to
    message['From'] = "me"

    if in_reply_to:
        message['In-Reply-To'] = in_reply_to
        message['References'] = in_reply_to
        final_subject = f"Re: {subject}"
    else:
        final_subject = subject

    message['Subject'] = final_subject


    if attachment_buffer:
        attachment_buffer.seek(0)  # make sure it's at start
        data = attachment_buffer.read()
        message.add_attachment(
            data,
            maintype='application',
            subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename=file_name
        )

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    send_request = {'raw': encoded_message}
    if thread_id:
        send_request['threadId'] = thread_id
    service.users().messages().send(userId='me', body=send_request).execute()
    print(f"📤 Email sent to {to}")




def build_error_summary_email(*error_lists):
    email_summary = []  

    for title, errors in error_lists:
        if errors:
            email_summary.append(f"\n❌ {title} ({len(errors)} issues):")
            for line in errors:  # Show only first 5
                email_summary.append(f"   - {line}")


    if not email_summary:
        return "✅ All checks passed. File is ready for upload."

    return "\n".join(email_summary)



def build_auto_fix_summary(auto_changes: dict) -> str:
    summary = []

    for category, changes in auto_changes.items():
        if changes:
            summary.append(f"\n🛠️ {category} ({len(changes)} fixes):")
            for change in changes:
                summary.append(f"   - {change}")


    if not summary:
        return "✅ No automatic fixes were applied."

    return "\n".join(summary)



# === Run test fetch ===
if __name__ == '__main__':

    # list_labels()

    # main()  # optional debug email fetch
    filename, file_type = fetch_attachment_from_email()

    if filename:
        print(f"Loaded {file_type} file: {filename}")
        # Hook into validator here
