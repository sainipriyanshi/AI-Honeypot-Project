import streamlit as st
import pandas as pd
import json
import os
import time

# UI CONFIGURATION: Sets the browser tab title and wide layout for better data visibility
st.set_page_config(page_title="Honeypot Admin Panel", layout="wide")

st.title("🛡️ AI Honeypot: Scammer Intelligence Dashboard")
st.markdown("This dashboard displays real-time data captured from trapped scammers.")


# --- DATA PERSISTENCE LAYER ---
def load_data(filename):

    """
    Reads Newline Delimited JSON (JSONL). 
    This is memory efficient as it processes the log file line-by-line.
    """

    if not os.path.exists(filename):
        return []
    data = []
    try:
        with open(filename, "r") as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
    except Exception:
        pass # Handle empty/corrupt files gracefully
    return data


# Load existing intelligence and victory reports
raw_data = load_data("captured_intelligence.json")
victory_data = load_data("final_trapped_scammers.json")

# --- SIDEBAR: SYSTEM HEALTH ---
st.sidebar.title("System Stats")
st.sidebar.metric("Total Intel Captured", len(raw_data))
st.sidebar.metric("Scammers Fully Trapped", len(victory_data))


# --- VICTORY LOG: SCAMMER ATTRIBUTES ---
st.header("🎯 Trapped Scammers (Victory Log)")
if victory_data:
    df = pd.DataFrame(victory_data)
   
    # DATA WRANGLING: Extracts nested evidence list into a readable comma-separated string
    df['UPI IDs'] = df['evidence_gathered'].apply(lambda x: ", ".join(x.get('upiIds', [])))
    df['Bank Accounts'] = df['evidence_gathered'].apply(lambda x: ", ".join(x.get('bankAccounts', [])))
    
    # Show only the most critical forensic columns for the dashboard view
    display_cols = ['session_id', 'conversation_depth', 'UPI IDs', 'Bank Accounts', 'final_verdict']
    st.table(df[display_cols])  

else:
    st.info("No scammers trapped yet. Run a test to see data here!")

st.divider()


# --- FORENSIC VIEWER: HISTORICAL DATA ---
st.header("📜 Historical Conversation Viewer")
if raw_data:
    # Use a set to get unique session IDs for the dropdown menu
    session_list = list(set([d['session_id'] for d in raw_data]))
    selected_session = st.selectbox("Select a past session to view history:", session_list)
    
    # Retrieve the specific session object based on the selected session ID
    session_details = next((item for item in raw_data if item["session_id"] == selected_session), None)
    
    if session_details and "history" in session_details:
        for msg in session_details["history"]:

            # Renders chat bubbles based on the sender's role
            role = "user" if msg['sender'] == "scammer" else "assistant"
            with st.chat_message(role):
                st.write(msg['text'])
else:
    st.write("No historical data available.")

st.divider()

# --- REAL-TIME MONITORING LAYER ---
st.header("⚡ Live Monitoring Mode")
st.caption("Auto-refreshing every 3 seconds...")

# ST.EMPTY: Creates a placeholder that we can overwrite every refresh to prevent screen flickering
live_chat_container = st.empty()

if os.path.exists("live_monitor.json"):
    try:
        with open("live_monitor.json", "r") as f:
            live_data = json.load(f)
        
        with live_chat_container.container():
            st.warning(f"🔴 LIVE SESSION ACTIVE: {live_data['session_id']}")
            for msg in live_data['history']:
                role = "user" if msg['sender'] == "scammer" else "assistant"
                with st.chat_message(role):
                    st.write(msg['text'])

    except Exception as e:
        # Graceful handling for 'File-in-Use' errors during high-speed logging
        st.error("Waiting for live data sync...")

# --- CONTROL LOOP ---
# This forces the script to re-run from the top every 3 seconds, 
# simulating a real-time socket connection.
time.sleep(3)
st.rerun()