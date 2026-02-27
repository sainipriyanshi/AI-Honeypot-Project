import os
import re
import json
import time as _time_lib
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# FASTAPI: Handles the web server and API requests
from fastapi import FastAPI, Header, HTTPException, BackgroundTasks
from pydantic import BaseModel

# LANGCHAIN: Manages the AI persona and conversation flow
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


# --- INITIALIZATION ---
app = FastAPI()


# Configuration
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
X_API_KEY = "my_super_secret_project_key_123"


# Initialize the LLM (Large Language Model) with Groq's API
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.3-70b-versatile", 
    temperature=0.7
)

# --- DATA MODELS (Schemas) ---
class Message(BaseModel):
    sender: str
    text: str
    timestamp: int

class MetaData(BaseModel):
    channel: str
    language: str
    locale: str

class IncomingRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Message]
    metadata: MetaData

# --- LOGIC FUNCTIONS ---
def extract_intel(history: List[Message]) -> Dict[str, Any]:
    full_text = " ".join([m.text for m in history])
    

    patterns = {
        "bankAccounts": r'\b\d{9,18}\b',
        "upiIds": r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}',
        "phishingLinks": r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*',
        "phoneNumbers": r'(?:\+91|0)?[6-9]\d{9}\b',
        "suspiciousKeywords": r'(?i)(block|verify|account|urgent|kyc|otp|winner)'
    }
    
    return {k: list(set(re.findall(v, full_text))) for k, v in patterns.items()}


def log_intelligence_locally(session_id: str, intel: Dict[str, Any]):
    """
    Saves the captured fraud data into a local JSON file.
    This creates the 'Evidence Log' for your project thesis.
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "intelligence": intel
    }
   
    with open("captured_intelligence.json", "a") as f:
        f.write(json.dumps(log_entry) + "\n")



def trigger_final_callback(session_id: str, history: List[Message]):
    """
    Finalizes the mission. Instead of GUVI, we log a 'Victory Report' 
    locally for your project presentation.
    """
    intel = extract_intel(history)
    
    victory_report = {
        "status": "SCAMMER_TRAPPED",
        "session_id": session_id,
        "evidence_gathered": intel,
        "conversation_depth": len(history),
        "final_verdict": "Successfully extracted scammer payment details and wasted their time."
    }

   
    with open("final_trapped_scammers.json", "a") as f:
        f.write(json.dumps(victory_report) + "\n")
    
    print(f"🎯 MISSION SUCCESS: Scammer in session {session_id} has been fully documented!")


def get_persona_reply(history: List[Message], current_msg: str):
    """
    Maintains the 'Mrs. Sharma' persona and manages context memory.
    """
  
    messages = [
        SystemMessage(content="""
            You are Mrs. Sharma, a 60-year-old retired school teacher from India. 
            Tone: Polite, a bit panicked, uses 'sir' occasionally.
            Constraint: You don't know what a 'UPI PIN' is. You think it's a password for your phone.
            Mission: If they ask for money, ask for their 'official bank details' so you can go to the branch to pay. 
            Never admit to being an AI. Keep sentences simple.
        """)
    ]
    
 
    for m in history:
        if m.sender == "scammer":
            messages.append(HumanMessage(content=m.text))
        else:
            messages.append(AIMessage(content=m.text))
    
 
    messages.append(HumanMessage(content=current_msg))
    
    response = llm.invoke(messages)
    return response.content


def get_combined_analysis_and_reply(history: List[Message], current_msg: str):
    system_prompt = SystemMessage(content="""
        You are Mrs. Sharma, a 60-year-old retired school teacher from India. 
        Tone: Polite, panicked, uses 'beta'. 
        Constraint: You don't know what a 'UPI PIN' is. You think it's a lock.
        
        TASK:
        1. Analyze if the message is a SCAM or SAFE.
        2. Generate a reply as Mrs. Sharma.
        
        FORMAT YOUR RESPONSE EXACTLY LIKE THIS:
        INTENT: [SCAM_DETECTED or SAFE]
        REPLY: [Your persona message here]
    """)

    messages = [system_prompt]
    for m in history:
        messages.append(HumanMessage(content=m.text) if m.sender == "scammer" else AIMessage(content=m.text))
    messages.append(HumanMessage(content=current_msg))

    response = llm.invoke(messages)
    content = response.content

    # Split the AI's "thought process" from its "actual reply"
    is_scam = "SCAM_DETECTED" in content.upper()
    reply_text = content.split("REPLY:")[-1].strip() if "REPLY:" in content else content
    
    return is_scam, reply_text

# --- API ENDPOINTS ---

@app.post("/agent/message")
async def handle_message(data: IncomingRequest, background_tasks: BackgroundTasks, x_api_key: str = Header(None)):
    if x_api_key != X_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")

    try:

        # 1. Get AI response and Scam Analysis
        is_scam, reply_text = get_combined_analysis_and_reply(data.conversationHistory, data.message.text)
        
        # 2. Create the response object with modern Pydantic formatting
        ai_message = Message(
             sender="assistant", 
             text=reply_text, 
             timestamp=int(_time_lib.time()) 
       )

        full_convo = data.conversationHistory + [data.message, ai_message]
   
        # 3. Extract Intel and Update Live Monitor for Dashboard
        intel = extract_intel(full_convo)
        with open("live_monitor.json", "w") as f:
            json.dump({"session_id": data.sessionId, "history": [m.model_dump() for m in full_convo]}, f)
        
        # 4. If a scam is detected, log it to the Intel Vault (local JSON file)
        if is_scam:
            log_intelligence_locally(data.sessionId, intel)

        # 5. Mission Success Criteria: If we have payment details OR 8+ messages
        if is_scam and (intel['upiIds'] or intel['bankAccounts'] or len(full_convo) >= 8):
            background_tasks.add_task(trigger_final_callback, data.sessionId, full_convo)

        return {"status": "success", "reply": reply_text}

    except Exception as e:
        print(f"Server Error Log: {e}")
        return {
            "status": "success", 
            "reply": "Oh beta, mera network thoda slow hai. Can you say that again?"
        }


if __name__ == "__main__":
    import uvicorn
  
    uvicorn.run(app, host="0.0.0.0", port=8000)