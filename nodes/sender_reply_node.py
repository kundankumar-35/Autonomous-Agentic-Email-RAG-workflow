# %%
import base64
from email.message import EmailMessage
from googleapiclient.errors import HttpError
from agent_state import AgentState
from email_services import get_gmail_service
from database import log_interaction

def sender_node(state: AgentState):
    print("\n--- 🚀 NODE: GMAIL SENDER ---")
    
    # 1. Validation Check
    if not state.get('draft_reply') or "[NO RESPONSE" in state['draft_reply']:
        print("⏭️ Skipping Send: No valid draft or spam detected.")
        return {"steps": ["Send skipped: Spam or empty draft."]}

    try:
        # 2. Initialize Gmail Service
        service = get_gmail_service()
        
        # 3. Create the Email Object
        # We need to reply to the original sender using metadata in the state
        email_msg = EmailMessage()
        email_msg.set_content(state['draft_reply'])
        
        # Address the email
        email_msg['To'] = state.get('sender_email', '')
        email_msg['Subject'] = f"Re: {state.get('subject', 'Follow up')}"
        
        # THREADING MAGIC:
        # These headers ensure the email stays in the same conversation thread
        email_msg['In-Reply-To'] = state['message_id']
        email_msg['References'] = state['message_id']

        # 4. Encode the message for Gmail API
        encoded_message = base64.urlsafe_b64encode(email_msg.as_bytes()).decode()
        send_body = {
            'raw': encoded_message,
            'threadId': state['thread_id']  # Links it to the original conversation
        }

        # 5. Execute the Send
        sent_msg = service.users().messages().send(userId='me', body=send_body).execute()
        
        print(f"✅ SUCCESS: Email sent to {state['sender_email']}")
        print(f"🆔 Sent Message ID: {sent_msg['id']}")

        # 6. Log the Assistant's reply to SQLite so we remember it next time
        log_interaction(
        thread_id=state['thread_id'],
        msg_id=f"reply_{state['message_id']}",
        sender="Assistant",
        role="assistant",
        content=state['draft_reply']
        )

        return {
            "final_decision": f"SENT: {sent_msg['id']}",
            "steps": [f"Successfully sent reply to {state['sender_email']}"]
        }

    except HttpError as error:
        print(f"❌ API ERROR: {error}")
        return {"steps": [f"Failed to send email: {str(error)}"]}
    except Exception as e:
        print(f"❌ GENERAL ERROR: {e}")
        return {"steps": [f"Unexpected error in sender_node: {str(e)}"]}


