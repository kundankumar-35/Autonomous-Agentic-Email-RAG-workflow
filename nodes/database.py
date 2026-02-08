# %%
import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('agent_memory.db')
    cursor = conn.cursor()
    
    # Table 1: Deduplication (Was this specific email handled?)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_messages (
            message_id TEXT PRIMARY KEY,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table 2: History (What was the conversation context?)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id TEXT,
            message_id TEXT,
            sender TEXT,
            role TEXT, -- 'user' or 'assistant'
            content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()





# %%
import sqlite3

DB_PATH = 'agent_memory.db'

def already_handled(msg_id):
    """Check if this specific message_id is in our 'skip' list."""
    if not msg_id: return False # Safety check for empty IDs
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM processed_messages WHERE message_id = ?', (msg_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def mark_as_processed(msg_id):
    """Blacklist the ID so we don't process it again."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO processed_messages (message_id) VALUES (?)', (msg_id,))
    conn.commit()
    conn.close()

# %%
def log_interaction(thread_id, msg_id, sender, role, content):
    """Stores the message in history and blacklists the ID."""
    conn = sqlite3.connect('agent_memory.db')
    cursor = conn.cursor()
    # 1. Blacklist the ID
    cursor.execute('INSERT OR IGNORE INTO processed_messages (message_id) VALUES (?)', (msg_id,))
    # 2. Save the chat history
    cursor.execute('''
        INSERT INTO conversation_history (thread_id, message_id, sender, role, content)
        VALUES (?, ?, ?, ?, ?)
    ''', (thread_id, msg_id, sender, role, content))
    conn.commit()
    conn.close()

# %%
def get_thread_history(thread_id):
    """Retrieves all previous messages in this conversation from SQLite."""
    conn = sqlite3.connect('agent_memory.db')
    cursor = conn.cursor()
    
    # Fetch all history for this thread, oldest first
    cursor.execute('''
        SELECT role, content FROM conversation_history 
        WHERE thread_id = ? 
        ORDER BY timestamp ASC
    ''', (thread_id,))
    
    rows = cursor.fetchall()
    conn.close()

    # Format history for the LLM prompt
    history_text = ""
    for role, content in rows:
        history_text += f"{role.upper()}: {content}\n---\n"
    
    return history_text if history_text else "No previous history found."

# %%


def should_skip_message(message_id, thread_id, current_body):
    """
    Returns True if the message should be ignored.
    Checks for Duplicate IDs, Assistant-as-last-speaker, and Repeated Content.
    """
    conn = sqlite3.connect('agent_memory.db')
    cursor = conn.cursor()
    
    try:
        # 1. DUPLICATE MESSAGE ID CHECK
        # If we've seen this exact ID, skip immediately.
        cursor.execute('SELECT 1 FROM processed_messages WHERE message_id = ?', (message_id,))
        if cursor.fetchone():
            return True

        # 2. LAST SPEAKER CHECK
        # Get the most recent message in this thread.
        cursor.execute('''
            SELECT role, content FROM conversation_history 
            WHERE thread_id = ? 
            ORDER BY timestamp DESC LIMIT 1
        ''', (thread_id,))
        last_entry = cursor.fetchone()

        if last_entry:
            role, last_content = last_entry
            
            # If the AI was the last one to speak, wait for a human response.
            if role == 'assistant':
                print(f"DEBUG: AI already replied to thread {thread_id}. Waiting.")
                return True
            
            # 3. CONTENT SIMILARITY CHECK
            # If the user sends the exact same text again, don't trigger the LLM.
            if current_body.strip() == last_content.strip():
                print(f"DEBUG: Repeated content in thread {thread_id}. Skipping.")
                return True

    finally:
        conn.close()

    return False


