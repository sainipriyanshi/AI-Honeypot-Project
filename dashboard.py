import streamlit as st
import pandas as pd
import json
import os
import time
import requests
import re

st.set_page_config(
    page_title="Honeypot Admin Panel",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0d1117;
    color: #c9d1d9;
}
section[data-testid="stSidebar"] { background: #161b22 !important; border-right: 1px solid #30363d; }
section[data-testid="stSidebar"] * { color: #c9d1d9 !important; }

.stTabs [data-baseweb="tab-list"] { background: #161b22; border-bottom: 1px solid #30363d; gap: 0; }
.stTabs [data-baseweb="tab"] {
    background: transparent; color: #8b949e;
    font-family: 'JetBrains Mono', monospace; font-size: 13px;
    padding: 12px 24px; border: none; border-bottom: 2px solid transparent;
}
.stTabs [aria-selected="true"] { color: #58a6ff !important; border-bottom: 2px solid #58a6ff !important; background: transparent !important; }

.main .block-container { padding: 1.5rem 2rem; max-width: 1400px; }
h1, h2, h3 { font-family: 'JetBrains Mono', monospace; color: #f0f6fc !important; }

.chat-header {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 12px 12px 0 0; padding: 12px 16px;
    display: flex; align-items: center; gap: 10px;
}
.chat-container {
    background: #0d1117; border: 1px solid #30363d; border-top: none;
    height: 480px; overflow-y: auto; padding: 16px;
    display: flex; flex-direction: column; gap: 8px;
}
.avatar { width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 700; flex-shrink: 0; }
.avatar-scammer { background: #da3633; color: white; }
.avatar-agent   { background: #238636; color: white; }

.bubble-wrap { display: flex; align-items: flex-end; gap: 8px; margin: 2px 0; }
.bubble-wrap.right { flex-direction: row-reverse; }
.bubble { max-width: 68%; padding: 10px 14px; border-radius: 18px; font-size: 14px; line-height: 1.5; word-wrap: break-word; }
.bubble-scammer { background: #1c2128; border: 1px solid #30363d; border-bottom-left-radius: 4px; color: #c9d1d9; }
.bubble-agent   { background: #0f3d1a; border: 1px solid #238636; border-bottom-right-radius: 4px; color: #7ee787; }
.bubble-time  { font-size: 10px; color: #484f58; margin-top: 4px; display: block; }
.bubble-label { font-size: 11px; font-family: 'JetBrains Mono', monospace; color: #8b949e; margin-bottom: 3px; }

.typing-indicator { display: flex; align-items: center; gap: 4px; padding: 10px 14px; background: #0f3d1a; border: 1px solid #238636; border-radius: 18px; border-bottom-right-radius: 4px; width: fit-content; }
.typing-dot { width: 7px; height: 7px; background: #7ee787; border-radius: 50%; display: inline-block; animation: bounce 1.2s infinite; }
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce { 0%,60%,100% { transform: translateY(0); } 30% { transform: translateY(-5px); } }

.chat-input-area { background: #161b22; border: 1px solid #30363d; border-top: none; border-radius: 0 0 12px 12px; padding: 12px 16px; }

.metric-card { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 16px; text-align: center; margin-bottom: 8px; }
.metric-value { font-family: 'JetBrains Mono', monospace; font-size: 28px; font-weight: 600; color: #58a6ff; }
.metric-label { font-size: 11px; color: #8b949e; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }

.badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-family: 'JetBrains Mono', monospace; margin: 3px; }
.badge-red   { background: #3d1a1a; color: #f85149; border: 1px solid #da3633; }
.badge-green { background: #0f3d1a; color: #7ee787; border: 1px solid #238636; }
.badge-blue  { background: #0d2645; color: #79c0ff; border: 1px solid #388bfd; }
.badge-amber { background: #3d2e00; color: #e3b341; border: 1px solid #9e6a03; }

.intel-card { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 20px; margin-bottom: 16px; }
.intel-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; padding-bottom: 10px; border-bottom: 1px solid #30363d; }
.session-id { font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #58a6ff; }
.verdict-tag { padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; font-family: 'JetBrains Mono', monospace; }
.verdict-trapped { background: #3d1a1a; color: #f85149; border: 1px solid #da3633; }
.verdict-safe    { background: #0f3d1a; color: #7ee787; border: 1px solid #238636; }

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }

.stTextInput input { background: #0d1117 !important; border: 1px solid #30363d !important; color: #c9d1d9 !important; border-radius: 8px !important; }
.stButton button { background: #238636 !important; color: white !important; border: none !important; border-radius: 8px !important; font-family: 'JetBrains Mono', monospace !important; font-size: 13px !important; }
.stButton button:hover { background: #2ea043 !important; }
div[data-testid="metric-container"] { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 12px; }
.stSelectbox div { background: #161b22 !important; border-color: #30363d !important; color: #c9d1d9 !important; }
</style>
""", unsafe_allow_html=True)


# ── Constants ─────────────────────────────────────────────────────────────────
API_URL      = "http://localhost:8000/agent/message"
API_KEY      = "my_super_secret_project_key_123"
INTEL_FILE   = "captured_intelligence.json"
VICTORY_FILE = "final_trapped_scammers.json"
LIVE_FILE    = "live_monitor.json"


# ── Helpers ───────────────────────────────────────────────────────────────────
def load_jsonl(filename):
    if not os.path.exists(filename):
        return []
    data = []
    try:
        with open(filename, "r") as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
    except Exception:
        pass
    return data


def load_json(filename):
    if not os.path.exists(filename):
        return None
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except Exception:
        return None


def send_to_agent(session_id, message_text, history):
    payload = {
        "sessionId": session_id,
        "message": {"sender": "scammer", "text": message_text, "timestamp": int(time.time())},
        "conversationHistory": history,
        "metadata": {"channel": "demo", "language": "en", "locale": "IN"}
    }
    try:
        resp = requests.post(API_URL, json=payload,
                             headers={"Content-Type": "application/json", "x-api-key": API_KEY},
                             timeout=30)
        if resp.status_code == 200:
            return resp.json().get("reply", "..."), None
        return None, f"API error {resp.status_code}"
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to backend. Is uvicorn running on port 8000?"
    except Exception as e:
        return None, str(e)


def fmt_time(ts=None):
    import datetime
    t = datetime.datetime.fromtimestamp(ts) if ts else datetime.datetime.now()
    return t.strftime("%I:%M %p")


def bubble_html(sender, text, ts=None):
    is_agent = (sender != "scammer")
    wrap  = "bubble-wrap right" if is_agent else "bubble-wrap"
    bub   = "bubble bubble-agent" if is_agent else "bubble bubble-scammer"
    label = "Mrs. Sharma (AI Agent)" if is_agent else "Scammer"
    avcls = "avatar avatar-agent" if is_agent else "avatar avatar-scammer"
    avltr = "M" if is_agent else "S"
    return f"""
    <div class="{wrap}">
        <div class="{avcls}">{avltr}</div>
        <div>
            <div class="bubble-label">{label}</div>
            <div class="{bub}">{text}<span class="bubble-time">{fmt_time(ts)}</span></div>
        </div>
    </div>"""


def typing_html():
    return """
    <div class="bubble-wrap right">
        <div class="avatar avatar-agent">M</div>
        <div>
            <div class="bubble-label">Mrs. Sharma is typing...</div>
            <div class="typing-indicator">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
            </div>
        </div>
    </div>"""


def badges_html(items, cls):
    if not items:
        return '<span style="color:#484f58;font-size:12px;">—</span>'
    return "".join([f'<span class="badge {cls}">{i}</span>' for i in items])


def extract_intel_from_text(text):
    return {
        "upiIds":    list(set(re.findall(r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}', text))),
        "phoneNumbers": list(set(re.findall(r'(?:\+91|0)?[6-9]\d{9}\b', text))),
        "bankAccounts": list(set(re.findall(r'\b\d{9,18}\b', text))),
        "phishingLinks": list(set(re.findall(r'https?://[^\s]+', text))),
        "suspiciousKeywords": list(set(re.findall(r'(?i)\b(block|verify|account|urgent|kyc|otp|winner)\b', text))),
    }


# ── Session state ─────────────────────────────────────────────────────────────
defaults = {
    "chat_history":   [],
    "api_history":    [],
    "session_id":     f"demo-{int(time.time())}",
    "is_typing":      False,
    "session_ended":  False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛡️ Honeypot")
    st.markdown("---")

    intel_data   = load_jsonl(INTEL_FILE)
    victory_data = load_jsonl(VICTORY_FILE)

    st.metric("Sessions logged", len(intel_data))
    st.metric("Scammers trapped", len(victory_data))
    st.metric("Messages this session", len(st.session_state.chat_history))

    st.markdown("---")
    st.markdown("**Current session ID**")
    st.code(st.session_state.session_id, language=None)

    if st.button("🔄 New Session"):
        for k, v in defaults.items():
            st.session_state[k] = v if k != "session_id" else f"demo-{int(time.time())}"
        st.rerun()

    st.markdown("---")
    try:
        r = requests.get("http://localhost:8000/docs", timeout=2)
        ok = r.status_code == 200
    except Exception:
        ok = False
    color = "#7ee787" if ok else "#f85149"
    label = "Backend online" if ok else "Backend offline"
    st.markdown(f'<span style="color:{color};font-size:13px;">⬤ {label}</span>', unsafe_allow_html=True)


# ── Title ─────────────────────────────────────────────────────────────────────
st.markdown("# 🛡️ AI Honeypot — Scam Intelligence Platform")

tab1, tab2 = st.tabs(["💬  Live Demo", "📊  Intelligence Reports"])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — LIVE DEMO
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    chat_col, intel_col = st.columns([3, 1])

    with chat_col:
        # Header
        st.markdown("""
        <div class="chat-header">
            <div class="avatar avatar-agent">M</div>
            <div>
                <div style="font-weight:600;color:#f0f6fc;font-size:14px;">Mrs. Sharma</div>
                <div style="font-size:12px;color:#7ee787;">AI Honeypot Persona Active</div>
            </div>
            <div style="margin-left:auto;font-size:12px;color:#8b949e;font-family:'JetBrains Mono',monospace;">🔒 Honeypot Running</div>
        </div>
        """, unsafe_allow_html=True)

        # Build chat HTML
        bubbles = ""
        if not st.session_state.chat_history:
            bubbles = """
            <div style="text-align:center;color:#484f58;margin-top:100px;font-size:14px;">
                <div style="font-size:36px;margin-bottom:12px;">🎭</div>
                Type a scam message below to start the session.<br>
                Mrs. Sharma will respond as your AI honeypot agent.
            </div>"""
        else:
            for msg in st.session_state.chat_history:
                bubbles += bubble_html(msg["sender"], msg["text"], msg.get("timestamp"))
            if st.session_state.is_typing:
                bubbles += typing_html()

        st.markdown(f'<div class="chat-container">{bubbles}</div>', unsafe_allow_html=True)

        # Input area
        st.markdown('<div class="chat-input-area">', unsafe_allow_html=True)

        if not st.session_state.session_ended:
            with st.form("msg_form", clear_on_submit=True):
                c1, c2 = st.columns([6, 1])
                with c1:
                    user_msg = st.text_input(
                        "msg", label_visibility="collapsed",
                        placeholder="Type scam message... e.g. 'Your KYC has expired, share OTP urgently'"
                    )
                with c2:
                    submitted = st.form_submit_button("Send ➤")

            if submitted and user_msg.strip():
                st.session_state.chat_history.append({
                    "sender": "scammer",
                    "text": user_msg.strip(),
                    "timestamp": int(time.time())
                })
                st.session_state.is_typing = True
                st.rerun()
        else:
            st.markdown("""
            <div style="text-align:center;color:#e3b341;font-size:14px;padding:10px;">
                ✅ Session ended — view Intelligence Reports tab for full analysis.
            </div>""", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # End session button
        if st.session_state.chat_history and not st.session_state.session_ended:
            if st.button("🏁 End Session & Extract Intelligence"):
                st.session_state.session_ended = True
                st.rerun()

    # ── Typing → call API ────────────────────────────────────────────────
    if st.session_state.is_typing:
        last_msg = st.session_state.chat_history[-1]
        reply, error = send_to_agent(
            st.session_state.session_id,
            last_msg["text"],
            st.session_state.api_history
        )
        st.session_state.is_typing = False
        if error:
            st.error(f"⚠️ {error}")
        else:
            st.session_state.api_history.append({
                "sender": "scammer", "text": last_msg["text"], "timestamp": last_msg["timestamp"]
            })
            agent_msg = {"sender": "assistant", "text": reply, "timestamp": int(time.time())}
            st.session_state.chat_history.append(agent_msg)
            st.session_state.api_history.append(agent_msg)
        st.rerun()

    # ── Live intel panel ─────────────────────────────────────────────────
    with intel_col:
        st.markdown("### Live Intel")

        full_text = " ".join(m["text"] for m in st.session_state.chat_history)
        live_intel = extract_intel_from_text(full_text)

        def show_section(title, items, cls):
            st.markdown(f'<div style="font-size:11px;color:#8b949e;text-transform:uppercase;letter-spacing:.05em;margin-top:12px;margin-bottom:4px;">{title}</div>', unsafe_allow_html=True)
            st.markdown(badges_html(items, cls), unsafe_allow_html=True)

        if full_text.strip():
            show_section("UPI IDs", live_intel["upiIds"], "badge-red")
            show_section("Phone numbers", live_intel["phoneNumbers"], "badge-amber")
            show_section("Bank accounts", live_intel["bankAccounts"], "badge-blue")
            show_section("Phishing links", live_intel["phishingLinks"], "badge-red")
            show_section("Keywords flagged", live_intel["suspiciousKeywords"], "badge-green")

            n = len(st.session_state.chat_history)
            st.markdown(f'<div class="metric-card" style="margin-top:16px;"><div class="metric-value">{n}</div><div class="metric-label">Messages</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#484f58;font-size:13px;margin-top:24px;">Send a message to see live intel here.</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — INTELLIGENCE REPORTS
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    intel_data   = load_jsonl(INTEL_FILE)
    victory_data = load_jsonl(VICTORY_FILE)

    # Metrics row
    m1, m2, m3, m4 = st.columns(4)
    total_msgs = sum(d.get("conversationdepth", 0) for d in victory_data)
    all_upi    = sum(len(d.get("evidencegathered", {}).get("upiIds", [])) for d in victory_data)

    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(intel_data)}</div><div class="metric-label">Total sessions</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#f85149">{len(victory_data)}</div><div class="metric-label">Scammers trapped</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#e3b341">{total_msgs}</div><div class="metric-label">Total messages</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#7ee787">{all_upi}</div><div class="metric-label">UPI IDs extracted</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    rep_col, hist_col = st.columns(2)

    # ── Trapped scammers ──────────────────────────────────────────────────
    with rep_col:
        st.markdown("### 🎯 Trapped Scammers")
        if not victory_data:
            st.markdown('<div style="color:#484f58;font-size:14px;padding:20px 0;">No scammers trapped yet.</div>', unsafe_allow_html=True)
        else:
            for v in reversed(victory_data):
                ev     = v.get("evidencegathered", {})
                sid    = v.get("sessionid", "unknown")
                depth  = v.get("conversationdepth", 0)
                verdict = v.get("finalverdict", "Scammer trapped")
                st.markdown(f"""
                <div class="intel-card">
                    <div class="intel-card-header">
                        <span class="session-id"># {sid}</span>
                        <span class="verdict-tag verdict-trapped">TRAPPED</span>
                    </div>
                    <div style="font-size:12px;color:#8b949e;margin-bottom:10px;">{depth} messages exchanged</div>
                    <div style="margin-bottom:8px;">
                        <span style="font-size:11px;color:#8b949e;text-transform:uppercase;letter-spacing:.05em;">UPI IDs</span><br>
                        {badges_html(ev.get('upiIds',[]), 'badge-red')}
                    </div>
                    <div style="margin-bottom:8px;">
                        <span style="font-size:11px;color:#8b949e;text-transform:uppercase;letter-spacing:.05em;">Phone numbers</span><br>
                        {badges_html(ev.get('phoneNumbers',[]), 'badge-amber')}
                    </div>
                    <div style="margin-bottom:8px;">
                        <span style="font-size:11px;color:#8b949e;text-transform:uppercase;letter-spacing:.05em;">Bank accounts</span><br>
                        {badges_html(ev.get('bankAccounts',[]), 'badge-blue')}
                    </div>
                    <div style="margin-bottom:8px;">
                        <span style="font-size:11px;color:#8b949e;text-transform:uppercase;letter-spacing:.05em;">Phishing links</span><br>
                        {badges_html(ev.get('phishingLinks',[]), 'badge-red')}
                    </div>
                    <div style="margin-bottom:8px;">
                        <span style="font-size:11px;color:#8b949e;text-transform:uppercase;letter-spacing:.05em;">Keywords</span><br>
                        {badges_html(ev.get('suspiciousKeywords',[]), 'badge-green')}
                    </div>
                    <div style="margin-top:12px;padding-top:10px;border-top:1px solid #30363d;font-size:12px;color:#8b949e;font-style:italic;">{verdict}</div>
                </div>
                """, unsafe_allow_html=True)

    # ── Conversation history ──────────────────────────────────────────────
    with hist_col:
        st.markdown("### 📜 Conversation History")
        if not intel_data:
            st.markdown('<div style="color:#484f58;font-size:14px;padding:20px 0;">No conversation history yet.</div>', unsafe_allow_html=True)
        else:
            session_ids = list({d.get("session_id", "unknown") for d in intel_data})
            selected    = st.selectbox("Select session", session_ids, key="hist_sel")
            entry       = next((d for d in intel_data if d.get("session_id") == selected), None)

            if entry:
                ts    = entry.get("timestamp", "")
                intel = entry.get("intelligence", {})

                kws        = intel.get("suspiciousKeywords", [])
                upi_found  = bool(intel.get("upiIds"))
                scam_likely = len(kws) >= 2 or upi_found
                slabel = "SCAM DETECTED" if scam_likely else "POSSIBLY SAFE"
                scls   = "verdict-trapped" if scam_likely else "verdict-safe"

                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                    <span style="font-size:12px;color:#8b949e;font-family:'JetBrains Mono',monospace;">{ts[:19] if ts else ''}</span>
                    <span class="verdict-tag {scls}">{slabel}</span>
                </div>""", unsafe_allow_html=True)

                history = entry.get("history", [])
                if history:
                    bubbles = "".join(bubble_html(m.get("sender","scammer"), m.get("text",""), m.get("timestamp")) for m in history)
                    st.markdown(f'<div class="chat-container" style="height:320px;">{bubbles}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="color:#484f58;font-size:13px;background:#161b22;border:1px solid #30363d;border-radius:8px;padding:20px;">No messages stored for this session yet.</div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**Extracted intelligence**")
                st.markdown(f"""
                <div class="intel-card">
                    <div style="margin-bottom:8px;">
                        <span style="font-size:11px;color:#8b949e;text-transform:uppercase;letter-spacing:.05em;">UPI IDs</span><br>
                        {badges_html(intel.get('upiIds',[]), 'badge-red')}
                    </div>
                    <div style="margin-bottom:8px;">
                        <span style="font-size:11px;color:#8b949e;text-transform:uppercase;letter-spacing:.05em;">Phone numbers</span><br>
                        {badges_html(intel.get('phoneNumbers',[]), 'badge-amber')}
                    </div>
                    <div style="margin-bottom:8px;">
                        <span style="font-size:11px;color:#8b949e;text-transform:uppercase;letter-spacing:.05em;">Phishing links</span><br>
                        {badges_html(intel.get('phishingLinks',[]), 'badge-red')}
                    </div>
                    <div>
                        <span style="font-size:11px;color:#8b949e;text-transform:uppercase;letter-spacing:.05em;">Keywords</span><br>
                        {badges_html(intel.get('suspiciousKeywords',[]), 'badge-green')}
                    </div>
                </div>""", unsafe_allow_html=True)