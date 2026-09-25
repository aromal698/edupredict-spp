import os
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Academic Monitoring Console", page_icon="🛡️", layout="wide", initial_sidebar_state="collapsed")
DATA_DIR = "data"
REPORT_FILE = os.path.join(DATA_DIR, "student_reports.csv")
REG_FILE = os.path.join(DATA_DIR, "student_registrations.csv")
AUDIT_FILE = os.path.join(DATA_DIR, "audit_log.csv")

PRINCIPAL_USERNAME = os.getenv("PRINCIPAL_USERNAME", "principal_admin")
PRINCIPAL_PASSWORD = os.getenv("PRINCIPAL_PASSWORD", "ChangeThisPrincipalPassword")

DEPARTMENTS = [
    "Computer Science and Engineering", "Artificial Intelligence and Data Science",
    "Artificial Intelligence and Machine Learning", "Information Technology",
    "Electronics and Communication Engineering", "Electrical and Electronics Engineering",
    "Civil Engineering", "Mechanical Engineering",
]
SEMESTERS = [f"S{i}" for i in range(1,9)]

def load_csv(path, cols):
    if not os.path.exists(path): return pd.DataFrame(columns=cols)
    try:
        df = pd.read_csv(path)
        for c in cols:
            if c not in df.columns: df[c] = ""
        return df[cols]
    except Exception:
        return pd.DataFrame(columns=cols)

REG_COLS=["Username","University_ID","Student_Name","Department","Semester","Tutor_Username","Registered_Time"]
AUDIT_COLS=["Timestamp","Role","Username","Action","University_ID","Department","Semester","Details"]

def login():
    st.markdown("# 🛡️ Academic Monitoring Console")
    st.caption("Restricted administrative monitoring interface")
    with st.form("principal_login"):
        u=st.text_input("Administrator Username")
        p=st.text_input("Administrator Password", type="password")
        ok=st.form_submit_button("🔐 Secure Login", type="primary", use_container_width=True)
    if ok:
        if u == PRINCIPAL_USERNAME and p == PRINCIPAL_PASSWORD:
            st.session_state.auth=True; st.rerun()
        else: st.error("Invalid administrator credentials.")

def dashboard():
    st.markdown("# 🛡️ Principal Academic Monitoring")
    st.caption(f"Live monitoring console • Last opened: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if st.button("🚪 Logout", use_container_width=False):
        st.session_state.auth=False; st.rerun()
    regs=load_csv(REG_FILE, REG_COLS)
    reports=load_csv(REPORT_FILE, ["Username","Student_Name","University_ID","Semester","Department","Created_Time","Subjects_JSON"])
    audit=load_csv(AUDIT_FILE, AUDIT_COLS)
    a,b,c,d=st.columns(4)
    a.metric("👨‍🎓 Registered Students", len(regs))
    b.metric("📝 Mark Submissions", len(reports))
    c.metric("👨‍🏫 Tutors Active in Records", audit[audit.Role.eq("Tutor")]["Username"].nunique() if not audit.empty else 0)
    d.metric("📡 Audit Events", len(audit))
    st.divider()
    tab1,tab2,tab3,tab4=st.tabs(["🏫 Students","👨‍🏫 Tutor Activity","📊 Mark Activity","🛰️ Audit Timeline"])
    with tab1:
        if regs.empty: st.info("No student registrations yet.")
        else:
            dept=st.selectbox("Filter Department", ["All"]+DEPARTMENTS)
            sem=st.selectbox("Filter Semester", ["All"]+SEMESTERS)
            x=regs.copy()
            if dept!="All": x=x[x.Department.eq(dept)]
            if sem!="All": x=x[x.Semester.eq(sem)]
            st.dataframe(x, use_container_width=True, hide_index=True)
    with tab2:
        x=audit[audit.Role.eq("Tutor")].copy() if not audit.empty else audit
        st.dataframe(x.sort_values("Timestamp", ascending=False), use_container_width=True, hide_index=True)
    with tab3:
        st.dataframe(reports.sort_values("Created_Time", ascending=False), use_container_width=True, hide_index=True)
    with tab4:
        st.dataframe(audit.sort_values("Timestamp", ascending=False), use_container_width=True, hide_index=True)
    st.success("🟢 Monitoring status: connected to the local data/audit store.")
    st.caption("For separate hosted websites, use a shared database/storage service rather than relying on each Streamlit app's local filesystem.")

if not st.session_state.get("auth",False): login()
else: dashboard()
