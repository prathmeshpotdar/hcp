\# AI-First CRM HCP Module - Demo



This is a minimal end-to-end demo showing:

\- React frontend (left: structured form, right: chat UI)

\- FastAPI backend

\- LangGraph-like agent wrapper (LLM extraction) that auto-populates the structured form from chat input.



\## Run backend

1\. cd backend

2\. python -m venv venv \&\& source venv/bin/activate

3\. pip install -r requirements.txt

4\. export DATABASE\_URL="sqlite:///./test.db"  # or postgres URL

5\. uvicorn app.main:app --reload --port 8000



\## Run frontend

1\. cd frontend

2\. npm install

3\. npm start

4\. Open http://localhost:3000



\## How it works

\- Type a natural language meeting note in the chat (right pane) and click "Log".

\- The backend will run a demo `call\_llm` parser (in `langgraph\_tools.py`), store the interaction, and return structured fields.

\- The frontend will fill the left-side structured form.



\## Replace with production LLM

\- Replace `langgraph\_tools.call\_llm` with actual Groq / llama / OpenAI calls.

\- Ensure you validate LLM JSON to a schema before storing.

\- Use Postgres/MySQL DB in production (change DATABASE\_URL).



