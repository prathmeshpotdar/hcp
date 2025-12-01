from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models, crud, langgraph_tools

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI-First CRM - HCP Module")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------
# 1️⃣ MAIN INTERACTION LOGGING ENDPOINT
# ---------------------------------------------------------
@app.post("/api/interactions/chat")
async def log_interaction(payload: dict, db: Session = Depends(get_db)):
    text = payload.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="text field required")

    # Run full extraction pipeline (6 tools → merged output)
    extracted = langgraph_tools.run_extraction(text)

    # Save interaction to DB
    saved = crud.create_interaction(db, extracted, raw_text=text)

    message = (
        "✔️ Interaction logged successfully! The details (HCP Name, Date, Sentiment, and Materials) "
        "have been automatically populated based on your summary. Would you like me to suggest a specific follow-up action, such as scheduling a meeting?"
    )

    return {
        "success": True,
        "message": message,
        "interaction_id": saved.id,
        "data": extracted
    }


# ---------------------------------------------------------
# 2️⃣ EDIT INTERACTION (RE-RUN EXTRACTOR OR SINGLE TOOL)
# ---------------------------------------------------------
@app.post("/api/interactions/edit/{interaction_id}")
async def edit_interaction(interaction_id: str, payload: dict, db: Session = Depends(get_db)):
    correction = payload.get("text", "").strip()
    if not correction:
        raise HTTPException(status_code=400, detail="text required")

    existing = crud.get_interaction(db, interaction_id)
    if not existing:
        raise HTTPException(status_code=404, detail="interaction not found")

    # Run extraction on edited text
    updates = langgraph_tools.run_extraction(correction)
    saved = crud.update_interaction(db, interaction_id, updates)

    return {
        "success": True,
        "updated": {
            "interaction_id": saved.id,
            "hcp_name": saved.hcp_name,
            "date": saved.date,
            "time": saved.time,
            "sentiment": saved.sentiment,
            "sentiment_source": saved.sentiment_source,
            "materials_shared": saved.materials_shared,
            "topics_discussed": saved.topics_discussed,
            "summary": saved.summary
        }
    }


# ---------------------------------------------------------
# 3️⃣ SUMMARIZER TOOL ENDPOINT
# ---------------------------------------------------------
@app.post("/api/interactions/summarize")
async def summarize(payload: dict):
    text = payload.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="text required")

    summary = langgraph_tools.summarize_interaction(text).get("summary")
    return {"summary": summary}


# ---------------------------------------------------------
# 4️⃣ NEXT BEST ACTION (Based on sentiment)
# ---------------------------------------------------------
@app.post("/api/interactions/next-best-action")
async def next_best_action(payload: dict):
    extracted = payload.get("data") or {}
    actions = []

    if extracted.get("sentiment") == "Positive":
        actions.append("Schedule product trial / follow-up meeting")
    else:
        actions.append("Send additional informational materials")

    return {"next_best_actions": actions}


# ---------------------------------------------------------
# 5️⃣ ENTITY EXTRACTION TOOL
# ---------------------------------------------------------
@app.post("/api/interactions/entities")
async def entities(payload: dict):
    text = payload.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="text required")

    entities = langgraph_tools.dispatch_tool("materials", text)
    return {"entities": entities}


# ---------------------------------------------------------
# ROOT
# ---------------------------------------------------------
@app.get("/")
async def root():
    return {"status": "CRM HCP Backend Running"}
