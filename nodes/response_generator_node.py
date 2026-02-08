import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from database import get_thread_history
from agent_state import AgentState

def response_generator(state: AgentState):
    print("\n--- 🧠 AGENT: HIGH-REASONING RESPONSE GENERATOR ---")
    
    # 1. Prepare Context Sources
    chat_history = get_thread_history(state['thread_id'])
    print("RAG Context: in high reasoning node",state['retrieved_context'])
    retrieved_docs = state.get('retrieved_context', [])
    
    # 2. Advanced Context Formatting
    if len(retrieved_docs) == 0:
        context_source = "INTERNAL_REASONING"
        print("No specific internal documents found. Rely on core logic and general knowledge.")
        formatted_context = "No specific internal documents found. Rely on core logic and general knowledge."
    else:
        context_source = "RAG_KNOWLEDGE_BASE"
        print("RAG DATA FOUND")
        print("Specific internal documents found. Rely on core logic and general knowledge.")
        formatted_context = retrieved_docs


    system_message = f"""
    You are a Recursive Reasoning AI Assistant specializing in {state['category']}.
    Current Date: 2026. Context Mode: {context_source}.

    ### OPERATIONAL PROTOCOLS:
    - **MATH/LOGIC:** Break down problems step-by-step. Use LaTeX for equations (e.g., $$x = \\frac{{{{-b \\pm \\sqrt{{{{d}}}}}}}}{{{{2a}}}}$$).
    - **REASONING:** Use Chain-of-Thought. State assumptions before conclusions.
    - **CODING:** Provide modular, secure snippets with comments. Use triple backticks.
    - **RAG USAGE:** If context is provided, prioritize it. Cite sources as [Source Name].

    ### BEHAVIORAL CONSTRAINTS:
    - START the reply directly. NO "I hope this finds you well" or "As an AI...".
    - If the context is missing and you aren't 100% sure, admit it and offer human escalation.
    - TONE: {state.get('tone', 'Professional and helpful')}.
    - Ensure output is scannable with Markdown bolding and lists.
    """

    user_message = """
    ### MEMORY (Past Interactions):
    {chat_history}

    ### KNOWLEDGE BASE (Reference Material):
    {context}

    ### INCOMING REQUEST:
    Subject: {subject}
    Body: {email_body}

    ### DRAFT THE RESPONSE:
    """

    try:
        # Initial attempt with the high-reasoning model
        llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.3) 
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", user_message)
        ])
        
        # Using format_messages to safely inject variables into the template
        formatted_prompt = prompt.format_messages(
            chat_history=chat_history,
            context=formatted_context,
            subject=state['subject'],
            email_body=state['raw_email']
        )
        
        response = llm.invoke(formatted_prompt)

        return {
            "draft_reply": response.content,
            "steps": state.get("steps", []) + [f"Generated {state['category']} response via {context_source}."]
        }

    except Exception as e:
        print(f"⚠️ Primary Model Failed, trying fallback: {str(e)}")
        # FALLBACK: Try the faster 8B model if 70B is rate-limited
        try:
            fallback_llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.5)
            response = fallback_llm.invoke(formatted_prompt)
            return {
                "draft_reply": response.content,
                "steps": state.get("steps", []) + ["Generated response using Fallback Model."]
            }
        except Exception as final_error:
            print(f"❌ Critical Error: {str(final_error)}")
            return {
                "draft_reply": "I'm currently looking into this and will provide a detailed update shortly.",
                "steps": state.get("steps", []) + [f"Generation failed: {str(final_error)}"]
            }