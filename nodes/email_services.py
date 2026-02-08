# %%
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
# Copy and paste this into your configuration section
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    creds = None
    # 1. Look for existing token
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # 2. If no token, use credentials.json to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            # This opens your browser
            creds = flow.run_local_server(port=0)
        
        # 3. Save the token for next time
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # 4. Return the authorized Gmail service
    return build('gmail', 'v1', credentials=creds)


