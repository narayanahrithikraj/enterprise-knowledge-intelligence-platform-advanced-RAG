import streamlit as st
import requests
import plotly.express as px
import pandas as pd
import time
import re

# Core configuration configurations matching standard layout requirements
st.set_page_config(page_title="Enterprise Knowledge Platform", page_icon="🛡️", layout="wide")
BACKEND_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000")

# --- 1️⃣ STATE INITIALIZATION MATRIX ---
if "token" not in st.session_state: st.session_state.token = None
if "user_email" not in st.session_state: st.session_state.user_email = None
if "user_name" not in st.session_state: st.session_state.user_name = None  
if "user_role" not in st.session_state: st.session_state.user_role = None
if "active_session_id" not in st.session_state: st.session_state.active_session_id = None

# --- GLOBAL SYSTEM UI HIGHLIGHTING & REMOVAL INJECTION ---
st.markdown("""
<style>
    /* 🛠️ REMOVE STREAMLIT CLOUD HEADER & VISUAL UTILITIES (Star, Edit, Menu) */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    /* Hide the bottom footer text block */
    footer {
        visibility: hidden !important;
        display: none !important;
    }

    /* Premium green glow highlight for validated, active submit buttons */
    div.stButton > button:enabled, .auth-btn-container button.activated-glow {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important; 
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 600 !important;
        box-shadow: 0 0 18px rgba(16, 185, 129, 0.55) !important;
        transform: translateY(-1px) !important;
        transition: all 0.25s ease-in-out !important;
        pointer-events: auto !important;
        cursor: pointer !important;
    }
    
    div.stButton > button:enabled:hover, .auth-btn-container button.activated-glow:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        box-shadow: 0 0 25px rgba(16, 185, 129, 0.8) !important;
        transform: translateY(-2px) scale(1.005) !important;
    }
    
    div[data-testid="stWidgetLabel"] {
        margin-bottom: 0px !important;
        padding-bottom: 2px !important;
    }
    div[data-testid="stWidgetLabel"] p {
        font-size: 14.5px !important;
        font-weight: 500 !important;
    }
    div[data-baseweb="input"] {
        background-color: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 6px !important;
        color: #FFFFFF !important;
        height: 40px !important; 
        font-size: 15px !important;
        transition: all 0.2s ease !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #4A90E2 !important;
        box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.25) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SYSTEM STABILIZATION UTILITIES ---
def is_valid_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

# --- 2️⃣ IDENTITY VERIFICATION WORKSPACE LAYER (LOGGED OUT STATE) ---
if st.session_state.token is None:
    st.markdown("""
    <style>
        [data-testid="stHorizontalBlock"] {
            margin-top: 3vh !important; 
            padding-bottom: 2vh !important;
        }
        .single-line-header {
            white-space: nowrap !important;
            font-size: 28px !important;
            font-weight: 700 !important;
            letter-spacing: -0.5px !important;
            margin: 0 !important;
            text-align: center !important;
        }
        div[data-testid="stVerticalBlock"] > div {
            gap: 0.15rem !important; 
        }
        div.stTabs {
            padding: 20px 32px !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
        }
        button[data-baseweb="tab"] p {
            font-size: 15.5px !important;
            font-weight: 600 !important;
        }
        
        .auth-btn-container button {
            background-color: rgba(255, 255, 255, 0.05) !important;
            color: rgba(255, 255, 255, 0.25) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            pointer-events: none !important;
            box-shadow: none !important;
            transform: none !important;
            transition: all 0.2s ease-in-out !important;
        }
    </style>

    <script>
        /* FIXED: Isolated key-event walker that triggers green glow ONLY on the identity portal page inputs */
        const traceLiveValidationInputs = () => {
            const workspaceTabs = parent.document.querySelectorAll('div[data-testid="stVerticalBlock"]');
            workspaceTabs.forEach(tab => {
                const textFields = Array.from(tab.querySelectorAll('input')).filter(i => i.type === 'text' || i.type === 'password');
                const submitBtn = tab.querySelector('div.stButton > button');
                
                if (submitBtn && textFields.length > 0) {
                    submitBtn.parentElement.classList.add('auth-btn-container');
                    
                    let formIsCompliant = true;
                    textFields.forEach(field => {
                        const secureValue = field.value.trim();
                        if (secureValue === '') formIsCompliant = false;
                        if (field.type === 'password' && secureValue.length < 6) formIsCompliant = false;
                        if (field.placeholder && field.placeholder.includes('company.com') && !secureValue.includes('@')) formIsCompliant = false;
                    });
                    
                    if (formIsCompliant) {
                        submitBtn.classList.add('activated-glow');
                        submitBtn.disabled = false;
                    } else {
                        submitBtn.classList.remove('activated-glow');
                    }
                }
            });
        };
        setInterval(traceLiveValidationInputs, 100);
    </script>
    """, unsafe_allow_html=True)

    left_space, center_card, right_space = st.columns([0.6, 1.8, 0.6])
    
    with center_card:
        st.markdown("<div style='text-align: center; margin-bottom: 12px;'><h2 class='single-line-header'>🛡️ ENTERPRISE IDENTITY PORTAL</h2><p style='color: gray; font-size: 13.5px; margin: 4px 0 0 0;'>Enterprise Knowledge Intelligence Platform (Advanced RAG)</p></div>", unsafe_allow_html=True)
        auth_tabs = st.tabs(["🔑 Sign In", "📝 Register"])
        
        with auth_tabs[0]:
            login_email = st.text_input("Corporate Email", placeholder="name@company.com", key="login_email_input").strip()
            login_password = st.text_input("Security Password", type="password", placeholder="••••••••", key="login_pass_input")
            
            if login_email and not is_valid_email(login_email):
                st.markdown("<style>div[data-testid='stTextInput']:nth-of-type(1) div[data-baseweb='input'] { border: 2px solid #FF4B4B !important; }</style>", unsafe_allow_html=True)
                st.error("⚠️ Invalid email format structure.")
            if login_password and len(login_password) < 6:
                st.markdown("<style>div[data-testid='stTextInput']:nth-of-type(2) div[data-baseweb='input'] { border: 2px solid #FF4B4B !important; }</style>", unsafe_allow_html=True)
                st.error("⚠️ Password must be ≥ 6 characters.")

            st.write("")
            if st.button("Authenticate Session", type="primary", width="stretch"):
                if login_email and login_password:
                    try:
                        res = requests.post(f"{BACKEND_URL}/auth/login", json={"email": login_email, "password": login_password}, timeout=5)
                        if res.status_code == 200:
                            data = res.json()
                            st.session_state.token = data["access_token"]
                            st.session_state.user_email = data["user"]["email"]
                            st.session_state.user_name = data["user"].get("full_name", data["user"]["email"])
                            st.session_state.user_role = data["user"]["role"]
                            st.success("Access Authorized! Opening workspace analytics...")
                            time.sleep(0.5)
                            st.rerun()
                        else: st.error("❌ Authentication Blocked: Invalid email or password.")
                    except Exception as e: st.error(f"Network processing exception: {e}")
                
        with auth_tabs[1]:
            reg_name = st.text_input("Full Name", placeholder="Username", key="reg_name_input").strip()
            reg_email = st.text_input("Enterprise Email", placeholder="name@company.com", key="reg_email_input").strip()
            reg_password = st.text_input("Choose Password", type="password", placeholder="Minimum 6 characters", key="reg_pass_input")
            reg_confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-type password", key="reg_confirm_input")
            reg_role = st.selectbox("Requested Clearance", ["User", "Admin"])
            
            admin_token_input = ""
            if reg_role == "Admin":
                admin_token_input = st.text_input("Authorization Token", type="password", placeholder="••••••••", key="reg_token_input").strip()

            if reg_name and len(reg_name) < 2:
                st.markdown("<style>div[data-testid='stTextInput']:nth-of-type(1) div[data-baseweb='input'] { border: 2px solid #FF4B4B !important; }</style>", unsafe_allow_html=True)
                st.error("⚠️ Username must contain at least 2 characters.")
            if reg_email and not is_valid_email(reg_email):
                st.markdown("<style>div[data-testid='stTextInput']:nth-of-type(2) div[data-baseweb='input'] { border: 2px solid #FF4B4B !important; }</style>", unsafe_allow_html=True)
                st.error("⚠️ Invalid enterprise registry email pattern format.")
            if reg_password and len(reg_password) < 6:
                st.markdown("<style>div[data-testid='stTextInput']:nth-of-type(3) div[data-baseweb='input'] { border: 2px solid #FF4B4B !important; }</style>", unsafe_allow_html=True)
                st.error("⚠️ Password must contain at least 6 characters.")
            if reg_password and reg_confirm_password and reg_password != reg_confirm_password:
                st.markdown("<style>div[data-testid='stTextInput']:nth-of-type(4) div[data-baseweb='input'] { border: 2px solid #FF4B4B !important; }</style>", unsafe_allow_html=True)
                st.error("❌ Passwords do not match.")

            st.write("")
            if st.button("Register Corporate Identity", type="primary", width="stretch"):
                if reg_name and reg_email and reg_password:
                    if reg_role == "Admin":
                        try:
                            val_res = requests.post(f"{BACKEND_URL}/tokens/validate", json={"token": admin_token_input}, timeout=5)
                            if val_res.status_code == 200:
                                signup_res = requests.post(f"{BACKEND_URL}/auth/signup", json={"email": reg_email, "password": reg_password, "full_name": reg_name, "role": reg_role}, timeout=5)
                                if signup_res.status_code == 201:
                                    requests.post(f"{BACKEND_URL}/tokens/consume", json={"token": admin_token_input}, timeout=5)
                                    st.success("🎉 Admin identity successfully generated! Proceed to sign in.")
                                else: st.error("❌ Registration rejected: Profile identity already exists.")
                            else: st.error("❌ Authorization Rejected: Invalid or Expired Admin Token.")
                        except Exception as e: st.error(f"Security processing exception: {e}")
                    else:
                        try:
                            res = requests.post(f"{BACKEND_URL}/auth/signup", json={"email": reg_email, "password": reg_password, "full_name": reg_name, "role": reg_role}, timeout=5)
                            if res.status_code == 201: st.success("🎉 Registered successfully! Proceed to sign in.")
                            else: st.error("❌ Registration rejected: Profile identity already exists.")
                        except Exception as e: st.error(f"Handshake error: {e}")

# --- 3️⃣ NATIVE PLATFORM WORKSPACE VIEW (LOGGED IN STATE) ---
else:
    auth_headers = {"Authorization": f"Bearer {st.session_state.token}"}
    with st.sidebar:
        DISPLAY_NAME = st.session_state.user_name or "Workspace Identity"
        st.markdown(f"### 👤 `{DISPLAY_NAME}`")
        st.caption(f"Clearance Level: **{st.session_state.user_role}**")
        if st.button("Logout Session", width="stretch"):
            st.session_state.token = st.session_state.user_email = st.session_state.user_name = st.session_state.user_role = st.session_state.active_session_id = None
            st.query_params.clear()
            st.rerun()
            
        with st.expander("🔐 Update Security Password"):
            current_pass = st.text_input("Current Password", type="password", key="side_old_pass_input")
            new_pass = st.text_input("New Security Password", type="password", key="side_new_pass_input")
            confirm_new_pass = st.text_input("Confirm New Password", type="password", key="side_confirm_new_pass")
            
            submit_enabled = current_pass and new_pass and confirm_new_pass
            if st.button("Apply New Password", width="stretch", type="secondary", disabled=not submit_enabled):
                if new_pass != confirm_new_pass:
                    st.error("❌ New passwords do not match.")
                elif len(new_pass) < 6:
                    st.error("⚠️ New password must be ≥ 6 characters.")
                else:
                    try:
                        pwd_payload = {
                            "email": st.session_state.user_email,
                            "old_password": current_pass,
                            "new_password": new_pass
                        }
                        change_res = requests.post(f"{BACKEND_URL}/auth/change-password", json=pwd_payload, timeout=5)
                        if change_res.status_code == 200:
                            st.success("🎉 Password updated successfully!")
                            time.sleep(0.6)
                            st.rerun()
                        else: st.error("❌ Update Rejected: Current password is incorrect.")
                    except Exception as e: st.error(f"Network error: {e}")

        st.write("---")
        options = ["📊 Main Core Analytics", "💬 Secure Agentic Chat"]
        if st.session_state.user_role == "Admin":
            options.extend(["📤 Repository Document Controller", "👥 User Management Console", "🔍 Knowledge Gap Reports"])
        app_mode = st.radio("Select Platform Console:", options)

    if app_mode == "📊 Main Core Analytics":
        st.title("📊 Enterprise Knowledge Analytics Command")
        st.write("---")
        try:
            metrics = requests.get(f"{BACKEND_URL}/analytics", timeout=5).json()
            card1, card2, card3 = st.columns(3)
            with card1: st.metric("Total Indexed Files Base", metrics.get("total_documents_processed", 0))
            with card2: st.metric("Total System Queries Evaluated", metrics.get("total_queries_served", 0))
            with card3: st.metric("⚠️ Knowledge Base Gaps Flagged", metrics.get("system_warnings_prevented", 0))
            st.write("---")
            graph_col1, graph_col2 = st.columns(2)
            with graph_col1:
                st.subheader("📁 Document Category Index Proportions")
                cat_dict = metrics.get("category_distribution", {"General": 0})
                df_cat = pd.DataFrame(list(cat_dict.items()), columns=["Category", "Total Files"])
                st.plotly_chart(px.pie(df_cat, values="Total Files", names="Category", hole=0.4), width="stretch")
            with graph_col2:
                st.subheader("📈 Trailing 7-Day Running Evaluation Performance")
                timeline = metrics.get("timeline", [])
                if timeline:
                    df_time = pd.DataFrame(timeline)
                    st.plotly_chart(px.line(df_time, x="date", y=["queries", "gaps"], markers=True), width="stretch")
                else: st.info("Insufficient runtime log tracking database records.")
        except Exception as e: st.error(f"Error packing visual dashboard modules: {e}")

    elif app_mode == "💬 Secure Agentic Chat":
        st.title("💬 Secure Multi-Turn Agentic Assistant")
        st.write("---")
        try: chat_sessions = requests.get(f"{BACKEND_URL}/chat/sessions", headers=auth_headers, timeout=5).json()
        except Exception: chat_sessions = []
            
        chat_sidebar, chat_window = st.columns([1, 3])
        with chat_sidebar:
            st.subheader("📁 Discussion Channels")
            new_title = st.text_input("Thread Topic Subject:")
            if st.button("➕ Open Fresh Chat Stream", width="stretch") and new_title.strip():
                requests.post(f"{BACKEND_URL}/chat/sessions", json={"title": new_title}, headers=auth_headers, timeout=5)
                st.rerun()
            st.write("---")
            if chat_sessions:
                for sess in chat_sessions:
                    btn_label = f"💬 {sess['title']}"
                    if st.session_state.active_session_id == sess["id"]: btn_label = f"▶️ 【 {sess['title'].upper()} 】"
                    if st.button(btn_label, key=f"sess_{sess['id']}", width="stretch"):
                        st.session_state.active_session_id = sess["id"]
                        st.rerun()
            else: st.info("No discussions logged.")

        with chat_window:
            if st.session_state.active_session_id is None: st.info("👈 Please select or open an active conversation stream thread loop to communicate.")
            else:
                try: messages = requests.get(f"{BACKEND_URL}/chat/sessions/{st.session_state.active_session_id}/messages", headers=auth_headers, timeout=5).json()
                except Exception: messages = []
                for msg in messages:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])
                        if msg.get("citations") and msg["role"] == "assistant":
                            with st.expander("📝 View Verification Footprints"):
                                for src in msg["citations"]: st.write(f"**Doc:** `{src['file']}`\n\n*Context:* {src['snippet']}\n---")
                if prompt := st.chat_input("Enter localized query sentence context..."):
                    with st.chat_message("user"): st.markdown(prompt)
                    with st.chat_message("assistant"):
                        with st.spinner("Analyzing parameters bounds..."):
                            res = requests.post(f"{BACKEND_URL}/query", json={"question": prompt, "session_id": st.session_state.active_session_id}, headers=auth_headers, timeout=10)
                            if res.status_code == 200: st.rerun()
                            else: st.error(res.text)

    elif app_mode == "📤 Repository Document Controller":
        st.title("📤 Document Ingestion & Repository Console")
        st.write("---")
        if st.session_state.user_role != "Admin": st.error("🔒 Security Infraction: Access Denied. Administrative credentials required.")
        else:
            uploaded_file = st.file_uploader("Upload organizational files (PDF, DOCX, XLSX, TXT):", type=["pdf", "docx", "xlsx", "txt"])
            doc_category = st.selectbox("Assign Organizational Folder Category:", ["HR Policies", "Finance Reports", "Technical SOPs", "Training Manuals", "General"])
            
            if uploaded_file and st.button("Trigger High-Retention Pipeline Processing", type="primary", key="upload_processing_trigger_btn"):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/octet-stream")}
                form_payload = {"category": doc_category}
                with st.spinner("Ingesting vectors..."):
                    res = requests.post(f"{BACKEND_URL}/upload", files=files, data=form_payload, headers=auth_headers, timeout=15)
                    if res.status_code == 200: st.success(res.json()["message"]); st.rerun()
                    else: st.error(res.text)
            st.write("---")
            st.subheader("🗄️ Ingested Files Metadata Ledger Base")
            try:
                res = requests.get(f"{BACKEND_URL}/documents", headers=auth_headers, timeout=5)
                if res.status_code == 200:
                    inventory = res.json()
                    if not inventory: st.info("No documents are currently mapped to the repository vector database collection stores.")
                    else:
                        for doc in inventory:
                            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                            with col1: st.markdown(f"📄 **{doc['filename']}**")
                            with col2: st.caption(f"Category: `{doc['category']}`")
                            with col3: st.caption(f"Size: {doc['file_size_kb']} KB")
                            with col4:
                                if st.button("Delete", key=f"del_{doc['id']}", width="stretch"):
                                    if requests.delete(f"{BACKEND_URL}/documents/{doc['id']}", headers=auth_headers, timeout=5).status_code == 200: st.success("Deleted!"); st.rerun()
                else: st.error("🔒 Access Denied: Administrative clearance required.")
            except Exception as e: st.error(f"Inventory failure: {e}")

    elif app_mode == "👥 User Management Console":
        st.title("👥 Corporate Workspace Access Governance Console")
        st.write("---")
        if st.session_state.user_role != "Admin": st.error("🔒 Security Infraction: Access Denied. Administrative credentials required.")
        else:
            st.subheader("🔑 Cryptographic Single-Use Admin Token Provisioner")
            if st.button("Generate Secure Admin Token", type="primary"):
                try:
                    token_res = requests.post(f"{BACKEND_URL}/admin/generate-token", headers=auth_headers, timeout=5)
                    if token_res.status_code == 200: st.success(f"🔑 **New Admin Token Generated:** `{token_res.json()['token']}`")
                    else: st.error("Failed to compile secure network token layer.")
                except Exception as e: st.error(f"Token generation failed: {e}")
            st.write("---")
            st.markdown("### Active Workspace Identities Ledger")
            try:
                res = requests.get(f"{BACKEND_URL}/admin/users", headers=auth_headers, timeout=5)
                if res.status_code == 200:
                    user_list = res.json()
                    for u in user_list:
                        u_col1, u_col2, u_col3, u_col4 = st.columns([3, 3, 2, 1])
                        with u_col1: st.markdown(f"👤 **{u['full_name'] or 'Unnamed Profile'}**")
                        with u_col2: st.caption(f"Email: `{u['email']}`")
                        with u_col3: st.info(f"Clearance Identity: {u['role']}")
                        with u_col4:
                            if u['email'] != st.session_state.user_email:
                                if st.button("Revoke", key=f"usr_{u['id']}", width="stretch"):
                                    payload = {
                                        "admin_email": st.session_state.user_email,
                                        "target_email": u['email']
                                    }
                                    with st.spinner("Purging record..."):
                                        del_res = requests.post(f"{BACKEND_URL}/admin/users/delete", json=payload, timeout=5)
                                        if del_res.status_code == 200: 
                                            st.success("Revoked!")
                                            time.sleep(0.5)
                                            st.rerun()
                                        else:
                                            st.error("Action denied.")
                            else: st.caption("Active Session")
            except Exception as e: st.error(f"User list fetch failure: {e}")

            # --- 🛠️ OPTIMIZED: EXECUTIVE PASSWORD OVERRIDE PANEL ---
            st.write("---")
            st.markdown("### ⚙️ Executive Account Override Actions")
            st.caption("Perform direct, privileged root mutations across the live database profile registers.")

            with st.container(border=True):
                st.markdown("#### 🔑 Administrative Password Override")
                target_user_reset = st.text_input("Target Account Email", key="admin_reset_email_field", placeholder="user@company.com")
                new_password_input = st.text_input("New Core Password Value", key="admin_reset_pass_field", type="password", placeholder="••••••••")
                
                if st.button("Force Relational Rotation", use_container_width=True, key="exec_pass_rotation_btn"):
                    if target_user_reset and new_password_input:
                        payload = {
                            "admin_email": st.session_state.user_email,
                            "target_email": target_user_reset.strip().lower(),
                            "new_password": new_password_input
                        }
                        with st.spinner("Overwriting encryption fields..."):
                            try:
                                reset_res = requests.post(f"{BACKEND_URL}/admin/users/reset-password", json=payload, timeout=5)
                                if reset_res.status_code == 200:
                                    st.success(f"✅ Modified: {reset_res.json()['message']}")
                                else:
                                    st.error(f"❌ Rejected: {reset_res.json().get('detail', 'Override blocked.')}")
                            except Exception as err:
                                st.error(f"API Hook Malfunction: {err}")
                    else:
                        st.warning("Please define both target identity email and password properties.")

    elif app_mode == "🔍 Knowledge Gap Reports":
        st.title("🔍 Automated Document Coverage & Knowledge Gap Logs")
        st.write("---")
        if st.session_state.user_role != "Admin": st.error("🔒 Access Denied.")
        else:
            try:
                res = requests.get(f"{BACKEND_URL}/admin/knowledge-gaps", headers=auth_headers, timeout=5)
                if res.status_code == 200:
                    gap_logs = res.json()
                    if not gap_logs: st.success("✨ All queries matched! No document repository gaps detected.")
                    else:
                        st.info("📋 The following queries were requested by users but had no matching contextual information in the vector database. Use this ledger to identify what documents need to be added.")
                        formatted_gaps = [{"Timestamp": g["timestamp"], "Unanswered User Query": g["raw_query"]} for g in gap_logs]
                        st.dataframe(pd.DataFrame(formatted_gaps), use_container_width=True, hide_index=True)
            except Exception as e: st.error(f"Gaps retrieval failure: {e}")