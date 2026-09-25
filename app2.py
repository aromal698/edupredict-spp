import os
from datetime import datetime
import pandas as pd
import streamlit as st

try:
    from streamlit_autorefresh import st_autorefresh
    AUTOREFRESH_AVAILABLE = True
except Exception:
    AUTOREFRESH_AVAILABLE = False

st.set_page_config(page_title="Academic Monitoring Console", page_icon="🛡️", layout="wide", initial_sidebar_state="collapsed")
DATA_DIR = "data"
REPORT_FILE = os.path.join(DATA_DIR, "student_reports.csv")
REG_FILE = os.path.join(DATA_DIR, "student_registrations.csv")
AUDIT_FILE = os.path.join(DATA_DIR, "audit_log.csv")
TUTOR_FILE = os.path.join(DATA_DIR, "tutor_profiles.csv")
STUDENT_FILES_DIR = os.path.join(DATA_DIR, "student_files")
PRINCIPAL_USERNAME = os.getenv("PRINCIPAL_USERNAME", "principal_admin")
PRINCIPAL_PASSWORD = os.getenv("PRINCIPAL_PASSWORD", "ChangeThisPrincipalPassword")
DEPARTMENTS = [
    "Computer Science and Engineering", "Artificial Intelligence and Data Science",
    "Artificial Intelligence and Machine Learning", "Information Technology",
    "Electronics and Communication Engineering", "Electrical and Electronics Engineering",
    "Civil Engineering", "Mechanical Engineering"
]
SEMESTERS = [f"S{i}" for i in range(1, 9)]
REG_COLS = ["University_ID", "Student_Name", "Department", "Semester", "Tutor_Username", "Registered_Time"]
AUDIT_COLS = ["Timestamp", "Role", "Username", "Action", "University_ID", "Department", "Semester", "Details"]
TUTOR_COLS = ["Tutor_Username", "Department", "Credit_Score", "Updated_Time"]

def load_csv(path, cols):
    if not os.path.exists(path):
        return pd.DataFrame(columns=cols)
    try:
        df = pd.read_csv(path)
        for c in cols:
            if c not in df.columns:
                df[c] = ""
        return df[cols]
    except Exception:
        return pd.DataFrame(columns=cols)

def login_visual():
    return ["🛡️", "🎓", "📊"][datetime.now().minute % 3]

def inject_css():
    st.markdown("""
    <style>
    .stApp{background:#020617;color:#eef2ff;overflow-x:hidden}
    .stApp::before{content:"";position:fixed;inset:-18%;z-index:-5;background:radial-gradient(circle at 15% 20%,rgba(34,211,238,.18),transparent 22%),radial-gradient(circle at 85% 25%,rgba(99,102,241,.17),transparent 24%),linear-gradient(125deg,#020617,#0b1024,#020617);animation:bg 16s ease-in-out infinite alternate}
    .stApp::after{content:"";position:fixed;inset:0;z-index:-4;opacity:.16;background-image:linear-gradient(rgba(125,211,252,.16) 1px,transparent 1px),linear-gradient(90deg,rgba(125,211,252,.16) 1px,transparent 1px);background-size:60px 60px;transform:perspective(700px) rotateX(58deg) scale(1.7);transform-origin:center bottom;animation:grid 10s linear infinite}
    @keyframes bg{0%{transform:scale(1)}50%{transform:scale(1.05)}100%{transform:scale(1.02)}}
    @keyframes grid{from{background-position:0 0,0 0}to{background-position:0 120px,120px 0}}
    .login-box{min-height:360px;display:flex;align-items:center;justify-content:center;border:1px solid rgba(255,255,255,.12);border-radius:28px;background:rgba(15,23,42,.68);backdrop-filter:blur(15px);position:relative;overflow:hidden}
    .login-grid{position:absolute;inset:0;opacity:.18;background-image:linear-gradient(rgba(255,255,255,.12) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.12) 1px,transparent 1px);background-size:44px 44px;transform:perspective(520px) rotateX(62deg) scale(1.7);transform-origin:center bottom;animation:grid2 9s linear infinite}
    @keyframes grid2{from{background-position:0 0,0 0}to{background-position:0 88px,88px 0}}
    .login-emoji{font-size:4rem;animation:float 3.5s ease-in-out infinite}
    @keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-9px)}}
    </style>
    """, unsafe_allow_html=True)

def login():
    if AUTOREFRESH_AVAILABLE:
        st_autorefresh(interval=60_000, key="principal_login_refresh")
    inject_css()
    visual = login_visual()
    st.markdown(f'''<div class="login-box"><div class="login-grid"></div><div style="position:relative;text-align:center;width:min(560px,90%)"><div class="login-emoji">{visual}</div><h1>Academic Monitoring Console</h1><p>Restricted Principal dashboard</p></div></div>''', unsafe_allow_html=True)
    with st.form("principal_login"):
        u = st.text_input("Administrator Username")
        p = st.text_input("Administrator Password", type="password")
        ok = st.form_submit_button("🔐 Secure Login", type="primary", use_container_width=True)
    if ok:
        if u == PRINCIPAL_USERNAME and p == PRINCIPAL_PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Invalid administrator credentials.")

def dashboard():
    inject_css()
    st.title("🛡️ Principal Academic Monitoring")
    st.caption(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if st.button("🚪 Logout"):
        st.session_state.auth = False
        st.rerun()
    regs = load_csv(REG_FILE, REG_COLS)
    reports = load_csv(REPORT_FILE, ["Username", "Student_Name", "University_ID", "Semester", "Department", "Created_Time", "Subjects_JSON"])
    audit = load_csv(AUDIT_FILE, AUDIT_COLS)
    tutors = load_csv(TUTOR_FILE, TUTOR_COLS)
    a,b,c,d = st.columns(4)
    a.metric("👨‍🎓 Registered Students", len(regs))
    b.metric("📝 Mark Submissions", len(reports))
    c.metric("👨‍🏫 Tutors", len(tutors))
    d.metric("📡 Audit Events", len(audit))
    tabs = st.tabs(["👨‍🎓 Students", "👨‍🏫 Tutors", "📝 Marks", "📡 Activity", "📎 Student Files"])
    with tabs[0]:
        if regs.empty:
            st.info("No registrations yet.")
        else:
            dept = st.selectbox("Department", ["All"] + DEPARTMENTS)
            sem = st.selectbox("Semester", ["All"] + SEMESTERS)
            x = regs.copy()
            if dept != "All": x = x[x.Department.eq(dept)]
            if sem != "All": x = x[x.Semester.eq(sem)]
            st.dataframe(x, use_container_width=True, hide_index=True)
    with tabs[1]:
        if tutors.empty:
            st.info("No tutor credit scores submitted yet.")
        else:
            st.dataframe(tutors.sort_values("Credit_Score", ascending=False), use_container_width=True, hide_index=True)
    with tabs[2]:
        st.dataframe(reports.sort_values("Created_Time", ascending=False), use_container_width=True, hide_index=True)
    with tabs[3]:
        st.dataframe(audit.sort_values("Timestamp", ascending=False), use_container_width=True, hide_index=True)
    with tabs[4]:
        rows = []
        if os.path.exists(STUDENT_FILES_DIR):
            for uid in os.listdir(STUDENT_FILES_DIR):
                folder = os.path.join(STUDENT_FILES_DIR, uid)
                if os.path.isdir(folder):
                    for f in os.listdir(folder):
                        rows.append({"University_ID": uid, "File": f})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True) if rows else st.info("No student files yet.")

if not st.session_state.get("auth", False):
    login()
else:
    dashboard()
