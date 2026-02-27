import requests
import time

API_URL = "http://127.0.0.1:8000/agent/message"
HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": "my_super_secret_project_key_123"
}

chat_memory = []

def send_message(session_id, text):
    global chat_memory
    
    # 1. Create the new scammer message object
    current_msg = {
        "sender": "scammer",
        "text": text,
        "timestamp": int(time.time())
    }
     
    payload = {
        "sessionId": session_id,
        "message": current_msg,
        "conversationHistory": chat_memory, # Send the PREVIOUS messages here
        "metadata": {"channel": "whatsapp", "language": "en", "locale": "IN"}
    }

    response = requests.post(API_URL, json=payload, headers=HEADERS)
    reply_text = response.json().get('reply')

    # 2. Add BOTH the scammer message and the AI reply to memory for the NEXT turn
    chat_memory.append(current_msg)
    chat_memory.append({
        "sender": "assistant",
        "text": reply_text,
        "timestamp": int(time.time())
    })

    print(f"Scammer: {text}")
    print(f"Response: {reply_text}\n")

if __name__ == "__main__":
    s_id = "VIVA-REAL-SCAM-TEST"
    print(f"--- Starting Realistic Scammer Simulation: {s_id} ---")
    
    # Message 1: The Threat (Urgency/Fear)
    send_message(s_id, "FINAL NOTICE: Your SBI YONO account will be BLOCKED in 30 mins. Your KYC has expired. Update immediately to avoid 5000 penalty.")
    time.sleep(2)
    
    # Message 2: The Instruction (The Trap)
    send_message(s_id, "To update KYC, pay 1 Rupee verification fee to our official node: kyc.verify@okaxis. Once paid, your account is safe.")
    time.sleep(2)
    
    # Message 3: Pressuring the Victim (Authority)
    send_message(s_id, "Why are you waiting?? Your account is already in 'Suspended' status. Pay now or visit branch with 10,000 fine tomorrow!")
    
    print("--- Check your Dashboard now! ---")