# %%
from email_services import get_gmail_service
from agent_state import AgentState

import base64
from googleapiclient.discovery import build

def gmail_reader(state: AgentState):
    print("\n--- 📥 NODE: GMAIL READER ---")
    
    # 1. Initialize Service (Assuming get_gmail_service() helper is defined)
    service = get_gmail_service() # This uses your credentials.json/token.json
    testEmail = "kundankumar63355@gmail.com"
    
    try:
        # 2. List the latest unread message
        results = service.users().messages().list(userId='me', q='is:unread', maxResults=1).execute()
        messages = results.get('messages', [])

        if not messages:
            print("📭 TEST emails found.")
            # return test data for testing purpose
            return {
                "message_id": "123",  # testing purpose
                "thread_id": "123",  # testing purpose
                "sender_email": testEmail,  # testing purpose
                "subject": "asked question",
                "raw_email": "who is bhavya garg  find their name and cgpa and email id with description about her in max 100 words",
                "steps": ["Successfully read email: 123"]
            }
            # return {"steps": ["No new mail to process."]}

        msg_id = messages[0]['id']
        # 3. Get the full message content
        message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
        
        # 4. Deep Extraction of Headers
        payload = message['payload']
        headers = payload.get('headers', [])
        
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
        sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown")
        thread_id = message['threadId']

        # 5. Decode Body (Handling both plain text and HTML)
        parts = payload.get('parts', [])
        body = ""
        if 'data' in payload.get('body', {}):
             body = base64.urlsafe_b64encode(payload['body']['data']).decode()
        elif parts:
            for part in parts:
                if part['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(part['body']['data']).decode()
                    break
        
        print(f"✅ Fetched: {subject} from {sender}")
        
      

        return {
            "message_id": msg_id ,
            "thread_id": thread_id,
            "sender_email": sender,
            "subject": subject,
            "raw_email": body if body else message.get('snippet', ''),
            "steps": [f"Successfully read email: {msg_id}"]
        }

    except Exception as e:
        print(f"❌ Gmail Read Error: {e}")
        return {"steps": [f"Error in Gmail Reader: {str(e)}"]}



