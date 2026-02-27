import os
import requests
from fastapi import FastAPI, Header, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# --- Configuration ---
GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
MY_API_KEY = "YOUR_SECRET_API_KEY"
OPENAI_API_KEY = "sk-..." # Your LLM Key

# --- Data Models ---
class Message(BaseModel):
    sender: str
    text: str
    timestamp: int

class MetaData(BaseModel):
    channel: str
    language: str
    locale: str

class ScamRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Message]
    metadata: MetaData

# --- The "Decoy" Agent Logic ---
def get_agent_response(history_text, current_msg):
    """
    Combines Beelzebub's adaptive persona & SMTPLLMPot's victim logic.
    """
    prompt = f"""
    You are an AI Honeypot acting as a naive human victim. 
    Role: Do NOT reveal you are an AI. 
    Goal: Keep the scammer talking to extract their UPI ID, Bank details, or Phishing links.
    Context: {history_text}
    Scammer says: {current_msg}
    Your Reply (keep it human, slightly worried):
    """
    # Use OpenAI or Llama here to generate the "reply" string
    # For now, we'll simulate a response:
    return "I am worried about my account. What do I need to do exactly?"

def extract_intelligence(history: List[Message]):
    """
    Logic inspired by MINERVA's extraction agents.
    Use Regex or LLM to pull details.
    """
    all_text = " ".join([m.text for m in history])
    return {
        "bankAccounts": [], # Implement Regex for account numbers
        "upiIds": [],      # Implement Regex for @upi
        "phishingLinks": [],
        "phoneNumbers": [],
        "suspiciousKeywords": ["block", "verify", "urgent"]
    }

def finalize_session(session_id, history):
    """The mandatory GUVI Callback"""
    intel = extract_intelligence(history)
    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": len(history),
        "extractedIntelligence": intel,
        "agentNotes": "Scammer attempted banking fraud via urgency."
    }
    requests.post(GUVI_CALLBACK_URL, json=payload)

# --- API Endpoints ---
@app.post("/process-message")
async def handle_scam(
    data: ScamRequest, 
    background_tasks: BackgroundTasks,
    x_api_key: str = Header(None)
):
    # 1. Auth Check
    if x_api_key != MY_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # 2. Scam Detection (Simplification: If keywords exist, it's a scam)
    is_scam = any(word in data.message.text.lower() for word in ["block", "bank", "upi"])
    
    if not is_scam:
        return {"status": "ignored", "reply": "Hello, how can I help you?"}

    # 3. Generate Agent Reply (Persona engagement)
    history_str = "\n".join([f"{m.sender}: {m.text}" for m in data.conversationHistory])
    ai_reply = get_agent_response(history_str, data.message.text)

    # 4. Trigger Final Callback if engagement is deep enough (e.g., 5+ messages)
    if len(data.conversationHistory) >= 10:
        background_tasks.add_task(finalize_session, data.sessionId, data.conversationHistory + [data.message])

    return {
        "status": "success",
        "reply": ai_reply
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)