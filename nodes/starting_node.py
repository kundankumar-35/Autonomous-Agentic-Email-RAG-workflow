# %%
from agent_state import AgentState
from analyzer_node import analyzer
from gmail_reader_node import gmail_reader
from sender_reply_node import sender_node
from response_generator_node import response_generator
from retriever_node import retriever
from email_services import get_gmail_service
from log_ignore_node import log_and_ignore_node
from langgraph.graph import StateGraph
from langgraph.graph import END , START
from database import should_skip_message, init_db, get_thread_history, log_interaction
from dotenv import load_dotenv
from llm_node import llm



# %%
# 1. Initialize the Graph
workflow = StateGraph(AgentState)

# 2. Add Functional Nodes
workflow.add_node("reader", gmail_reader)
workflow.add_node("analyzer", analyzer)
workflow.add_node("retriever", retriever) # NEW: RAG Node
workflow.add_node("generator", response_generator)
workflow.add_node("sender", sender_node) # Updated to save history
workflow.add_node("ignore", log_and_ignore_node)

# 3. Define Flow
workflow.set_entry_point("reader")
workflow.add_edge("reader", "analyzer")



# Updated Routing Logic
def routing_logic(state: AgentState):
    print("--- 🛣️ ROUTING LOGIC ---")
    
    # 1. THE DATABASE GUARD (The absolute first check)
    # We check if the ID is handled OR if the AI was the last speaker
    if should_skip_message(state['message_id'], state['thread_id'], state['raw_email']):
        print("Result: SKIP (Already handled or AI last speaker)")
        return "skip"

    # 2. SPAM FILTER
    # If your analyzer node flagged it as spam, don't waste tokens/effort
    if state.get("is_spam") is True:
        print("Result: SPAM (Terminating)")
        return "spam"

    # 3. INTENT CHECK
    # Does this email actually need an answer? (e.g., 'Thanks!' or 'Ooo')
    if state.get("needs_reply") is False:
        print("Result: SKIP (No reply needed)")
        return "skip"

    # 4. LEGIT
    print("Result: PROCEED TO RETRIVER")
    return "legit"


workflow.add_conditional_edges(
    "analyzer",
    routing_logic,
    {
        "spam": "ignore",
        "skip": "ignore",
        "legit":"retriever"
    }
)

workflow.add_edge("retriever", "generator") # Pass retrieved facts to AI
workflow.add_edge("generator", "sender")
workflow.add_edge("sender", END)
workflow.add_edge("ignore", END)

app = workflow.compile()

# %%
import time
import sys

# --- RAG/Agent Helper Imports ---
# Make sure load_dotenv() is called at the top of your script
load_dotenv()

if __name__ == "__main__":
    init_db()
    print("🚀 AI Email Agent Service Started...")
    print("Mode: Fully Autonomous (Checking every 20s)")
    print("Press Ctrl+C to stop the agent.")
    
    # 1. Main infinite loop
   
    try:
            print("\n🔍 Polling Gmail for new unread messages...")
            
            # 2. Define the fresh initial state matching your AgentState
            initial_state = {
                "message_id": "",
                "thread_id": "",
                "sender_email": "",
                "subject": "",
                "raw_email": "",
                "category": "Pending",
                "tone": "Neutral",
                "is_spam": False,
                "needs_reply": True,
                "priority": 3,
                "draft_reply": "",
                "retrieved_context": "",
                "confidence_score": 0.0,
                "final_decision": "PENDING",
                "steps": []
            }
            
            # 3. Invoke the compiled LangGraph App
            # Ensure 'app' is your compiled graph: app = workflow.compile()
            final_output = app.invoke(initial_state)
            
            # 4. Print the Audit Log
            if final_output.get('steps') and len(final_output['steps']) > 0:
                print("\n" + "━" * 40)
                print(f"🏁 WORKFLOW COMPLETE")
                print(f"📡 Decision: {final_output.get('final_decision')}")
                print(f"📧 From:     {final_output.get('sender_email', 'N/A')}")
                print(f"📊 Priority: {final_output.get('priority', 'N/A')}/5")
                print("-" * 40)
                
                for i, step in enumerate(final_output['steps'], 1):
                    print(f" {i}. {step}")
                print("━" * 40)
            else:
                print("😴 Inbox clean. No new messages to process.")

    except KeyboardInterrupt:
            print("\n🛑 Agent stopped by user. Goodbye!")
            sys.exit()
    except Exception as e:
            print(f"⚠️ Loop Error: {e}")
            print("💡 Tip: Ensure your 'get_gmail_service' helper and 'app' are defined.")

  


