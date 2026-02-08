# %%
from typing import TypedDict, Optional, List, Annotated, Union
import operator

class AgentState(TypedDict):
    # --- IDENTIFIERS ---
    message_id: str
    thread_id: str
    sender_email: str
    subject: str
    
    # --- CONTENT ---
    raw_email: str
    
    # --- ANALYSIS ---
    category: str    # e.g., "Interview", "Support"
    tone: str        # e.g., "Professional", "Frustrated"
    is_spam: bool
    needs_reply: bool # Decision flag: True to draft/send, False to skip
    priority: int     # 1-5 scale
    
    # --- OUTPUT ---
    # Optional[str] is good, but for LLM prompts, "" (empty string) 
    # is often safer than None to avoid concatenation errors.
    draft_reply: Optional[str] 
    retrieved_context: Optional[str]
    final_reply: Optional[str]
    confidence_score: Optional[float]

    
    # Action result for the final audit log
    final_decision: str # "SENT", "SKIPPED", or "SPAM"
    
    # --- LOGGING ---
    # Annotated with operator.add is perfect—it ensures nodes 
    # APPEND to the history rather than overwriting it.
    steps: Annotated[List[str], operator.add]



