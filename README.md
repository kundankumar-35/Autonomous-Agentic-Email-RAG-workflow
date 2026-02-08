# Autonomous Agentic Email RAG Workflow

## Project Overview
The Autonomous Agentic Email RAG Workflow is an innovative solution designed to streamline email management through advanced AI techniques. It automates the retrieval of relevant information and generates intelligent responses using Retrieval-Augmented Generation (RAG).

## Architecture
The architecture comprises several interconnected nodes that process emails through a LangGraph-based workflow:

1. **Gmail Reader Node** (`gmail_reader`) - Fetches unread emails from Gmail
2. **Analyzer Node** (`analyzer`) - Analyzes email for category, tone, spam detection, and priority
3. **Retriever Node** (`retriever`) - Performs semantic search on knowledge base using RAG
4. **Response Generator Node** (`response_generator`) - Generates intelligent responses using LLM
5. **Sender Node** (`sender_node`) - Sends replies and logs interactions
6. **Log & Ignore Node** (`log_and_ignore_node`) - Handles spam and non-reply emails

## Features
- Automated email retrieval and intelligent response generation
- Spam detection and priority classification
- RAG-powered knowledge base integration
- Gmail API integration with OAuth2 authentication
- Conversation history tracking in SQLite database
- Message deduplication to prevent duplicate processing
- Chain-of-Thought reasoning with multi-model support
- Professional email tone and formatting

## Installation
To install the Autonomous Agentic Email RAG Workflow, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/kundankumar-35/Autonomous-Agentic-Email-RAG-workflow.git
   ```

2. Navigate to the project directory:
   ```bash
   cd Autonomous-Agentic-Email-RAG-workflow
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment variables in the `.env` file

5. Configure your Gmail credentials:
   - Place `credentials.json` in the project root (from Google Cloud Console)

## Usage
To run the workflow, execute the following command:

```bash
python main.py
```

The agent will start polling Gmail every 20 seconds for unread emails and process them autonomously.

## Project Structure
```
Autonomous-Agentic-Email-RAG-workflow/
│
├── .env                              # Environment variables (API keys, secrets)
├── .gitignore                        # Git ignore rules
├── .python-version                   # Python version specification
├── agent_memory.db                   # SQLite database for conversation history
├── credentials.json                  # Gmail OAuth credentials
├── token.json                        # Gmail OAuth token (auto-generated)
├── ingest.py                         # Data ingestion script for knowledge base
├── main.py                           # Main entry point
├── pyproject.toml                    # Python project configuration
├── rag_working_test.py              # Testing script for RAG functionality
├── requirements.txt                 # Python dependencies
├── uv.lock                          # Dependency lock file
│
├── .pycache_/                        # Python cache directory
│
├── knowledge_base/                   # Vector store for RAG embeddings
│
├── nodes/                            # Core node implementations
│   ├── __init__.py                   # Package initialization
│   ├── agent_state.py               # AgentState TypedDict definition
│   ├── analyzer_node.py             # analyzer() - Email analysis logic
│   ├── database.py                  # Database utilities (SQLite operations)
│   ├── email_services.py            # get_gmail_service() - Gmail API integration
│   ├── gmail_reader_node.py         # gmail_reader() - Email retrieval
│   ├── llm_node.py                  # LLM initialization (ChatGroq)
│   ├── log_ignore_node.py           # log_and_ignore_node() - Spam handling
│   ├── response_generator_node.py   # response_generator() - Reply generation
│   ├── retriever_node.py            # retriever() - RAG semantic search
│   ├── sender_reply_node.py         # sender_node() - Email sending
│   ├── starting_node.py             # starting_node() - Workflow initialization
│   └── workflow.py                  # StateGraph workflow definition
│
├── rag_data/                        # RAG training data and documents
│
└── README.md                        # This file
```

## Core Variable Naming Conventions

### AgentState Variables
The `AgentState` TypedDict maintains consistency across all nodes with these key variables:

**Identifiers:**
- `message_id: str` - Unique Gmail message ID
- `thread_id: str` - Gmail thread ID for conversation grouping
- `sender_email: str` - Email sender's address

**Content:**
- `subject: str` - Email subject line
- `raw_email: str` - Full email body content

**Analysis:**
- `category: str` - Email category (e.g., "Interview", "Support")
- `tone: str` - Detected tone (e.g., "Professional", "Frustrated")
- `is_spam: bool` - Spam detection flag
- `needs_reply: bool` - Decision flag for reply generation
- `priority: int` - Priority level (1-5 scale)

**Output:**
- `draft_reply: Optional[str]` - Generated email response
- `retrieved_context: Optional[str]` - RAG-retrieved knowledge base content
- `final_reply: Optional[str]` - Final processed reply
- `confidence_score: Optional[float]` - Confidence metric

**Logging:**
- `steps: Annotated[List[str], operator.add]` - Append-only execution history
- `final_decision: str` - Final action ("SENT", "SKIPPED", or "SPAM")

### Node Function Names
- `gmail_reader(state: AgentState)` - Reads email from Gmail
- `analyzer(state: AgentState)` - Analyzes email attributes
- `retriever(state: AgentState)` - Retrieves RAG context
- `response_generator(state: AgentState)` - Generates response
- `sender_node(state: AgentState)` - Sends response
- `log_and_ignore_node(state: AgentState)` - Logs skipped emails

### Database Functions
- `init_db()` - Initialize SQLite database
- `already_handled(msg_id)` - Check if message was processed
- `mark_as_processed(msg_id)` - Blacklist a message ID
- `log_interaction(thread_id, msg_id, sender, role, content)` - Save conversation history
- `get_thread_history(thread_id)` - Retrieve conversation context
- `should_skip_message(message_id, thread_id, current_body)` - Deduplication check

## Contribution Guidelines
We welcome contributions from the community! To contribute:

1. Fork the repository
2. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature/my-feature
   ```
3. Make your changes and commit them following the variable naming conventions
4. Push to the branch:
   ```bash
   git push origin feature/my-feature
   ```
5. Open a pull request and describe your changes

For significant changes, please open an issue first to discuss what you would like to change.

## Configuration
Update your `.env` file with the following variables:
```
GROQ_API_KEY=your_groq_api_key
HUGGINGFACE_API_KEY=your_huggingface_api_key
```

## Dependencies
Key dependencies include:
- `langchain` - LLM orchestration framework
- `langchain-groq` - Groq LLM integration
- `langchain-chroma` - Vector store integration
- `google-auth-oauthlib` - Gmail API authentication
- `sqlite3` - Local database for conversation history
- `langgraph` - State graph workflow engine

Thank you for your interest and contributions!