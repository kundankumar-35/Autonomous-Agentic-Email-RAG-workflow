# %%
from agent_state import AgentState

def log_and_ignore_node(state: AgentState):
    reason = "Spam Detected" if state.get("is_spam") else "Informational/No-Reply email skipped"
    print(f"🗑️ LOG: {reason}")
    
    return {
        "final_decision": "IGNORED",
        "steps": [f"Action: {reason}"]
    }



