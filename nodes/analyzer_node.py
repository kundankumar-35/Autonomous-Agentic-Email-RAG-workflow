
from agent_state import AgentState
from database import already_handled
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from llm_node import llm

import json

def analyzer(state: AgentState):
    print("\n--- 🧠 AGENT: DEEP ANALYZER & SKIP-FILTER ---")

    thread_id = state['thread_id']
    body = state['raw_email']
    

   # (Assuming you just fetched messages from Gmail)
    msg_id = state.get("message_id") 

    # 2. Database Guard: Check if specific message_id was already handled
    if already_handled(msg_id):
        print(f"🛑 Skipping: Message {msg_id} already reply sent")
        return {
            "needs_reply": False,
            "final_decision": "SKIPPED_ALREADY_PROCESSED",
            "steps": [f"Database check: {msg_id} was already replied."]
        }
    
    # We include the sender_email in the prompt to help the LLM identify automated addresses
    prompt = f"""
    You are a Senior Email Strategist. Analyze this email and return JSON.

    ### EMAIL CONTEXT:
    Sender: {state['sender_email']}
    Subject: {state['subject']}
    Body: {state['raw_email']}

    ### TASK:
    1. CATEGORY: [Interview, Support, Business, Spam, Notification]
    2. NEEDS_REPLY: Boolean. Set to 'false' if:
       - The sender is a 'no-reply' or 'noreply' address.
       - The email is an automated receipt, newsletter, or system alert.
       - The content is purely informational (e.g., "Your order has shipped").
    3. PRIORITY: 1-5.
    4. DRAFT_REPLY: ONLY write a draft if NEEDS_REPLY is 'true'. Otherwise, leave empty.

    ### OUTPUT FORMAT (JSON ONLY):
    {{
        "category": "string",
        "tone": "string",
        "is_spam": boolean,
        "needs_reply": boolean,
        "priority": integer,
        "draft_reply": "string"
    }}
    """

    try:
        response = llm.invoke(prompt).content.strip()
        
        # Clean potential Markdown artifacts
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        
        data = json.loads(response)
        
        # logic-level override: if the address literally contains 'noreply', we force skip
        if "noreply" in state['sender_email'].lower() or "no-reply" in state['sender_email'].lower():
            data["needs_reply"] = False
            data["category"] = "Notification"

        status_msg = f"Target: {state['sender_email']} | Needs Reply: {data.get('needs_reply')}"
        print(f"✅ {status_msg}")

        return {
            "category": data.get("category"),
            "tone": data.get("tone"),
            "is_spam": data.get("is_spam", False),
            "needs_reply": data.get("needs_reply", True),
            "priority": data.get("priority", 3),
            "draft_reply": data.get("draft_reply", ""),
            "steps": [f"Deep Analysis: {status_msg}"] 
        }

    except Exception as e:
        print(f"⚠️ Error: {e}")
        return {"needs_reply": False, "steps": ["Analysis failed; skipping email."]}


