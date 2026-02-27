# 🛡️ AI Honeypot: Automated Fraud Intelligence System

An AI-driven honeypot designed to trap scammers, waste their time, and extract forensic evidence (UPI IDs, Bank Accounts) automatically.

## 🚀 System Architecture
- **Backend**: FastAPI & LangChain (Llama-3.3-70B via Groq)
- **Frontend**: Streamlit Real-time Dashboard
- **Logic**: Mrs. Sharma (Persona) based Social Engineering

## 📂 Project Structure
- `agent_core_engine.py`: The "Brain" (FastAPI & LLM Logic).
- `dashboard.py`: The "Eyes" (Live Monitoring UI).
- `captured_intelligence.json`: Raw evidence log.
- `final_trapped_scammers.json`: High-level victory reports.

## 🛠️ How to Run
1. Start the Backend: `python agent_core_engine.py`
2. Start the Dashboard: `streamlit run dashboard.py`
3. Run the Test: `python test_env.py`