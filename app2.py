import os
from datetime import datetime
import pandas as pd
import streamlit as st
try:
    from streamlit_autorefresh import st_autorefresh
    AUTOREFRESH_AVAILABLE=True
except Exception: AUTOREFRESH_AVAILABLE=False
st.set_page_config(page_title="Principal Dashboard",page_icon="🛡️",layout="wide",initial_sidebar_state="collapsed")
DATA_DIR="data"; os.makedirs(DATA_DIR,exist_ok=True)
REPORT_FILE=os.path.join(DATA_DIR,"student_reports.csv"); REG_FILE=os.path.join(DATA_DIR,"student_registrations.csv"); AUDIT_FILE=os.path.join(DATA_DIR,"audit_log.csv"); TUTOR_FILE=os.path.join(DATA_DIR,"tutor_profiles.csv"); CARD_FILE=os.path.join(DATA_DIR,"smart_card_registrations.csv")
PRINCIPAL_USERNAME="Principle"; PRINCIPAL_PASSWORD="2026"
DEPARTMENTS=["Computer Science and Engineering","Artificial Intelligence and Data Science","Artificial Intelligence and Machine Learning","Information Technology","Electronics and Communication Engineering","Electrical and Electronics Engineering","Civil Engineering","Mechanical Engineering"]; SEMESTERS=[f"S{i}" for i in range(1,9)]
REG_COLS=["University_ID","Student_Name","Department","Semester","Tutor_Username","Registered_Time"]; AUDIT_COLS=["Timestamp","Role","Username","Action","University_ID","Department","Semester","Details"]; TUTOR_COLS=["Tutor_Username","Tutor_Name","Department","Credit_Score","Updated_Time"]; CARD_COLS=["Registration_ID","University_ID","Student_Name","DOB","Blood_Group","Address","PIN_Code","Studied_College","Department","Semester","CGPA","University_Name","Submitted_Time"]

def load_csv(path,cols):
    if not os.path.exists(path): return pd.DataFrame(columns=cols)
    try:
        d=pd.read_csv(path)
        for c in cols:
            if c not in d.columns:d[c]=""
        return d[cols]
    except Exception:return pd.DataFrame(columns=cols)

def visual():return ["🛡️","🎓","📊"][datetime.now().minute%3]

def css():
    st.markdown("""<style>.stApp{background:#020617;color:#eef2ff;overflow-x:hidden}.stApp:before{content:"";position:fixed;inset:-15%;z-index:-5;background:radial-gradient(circle at 20% 20%,rgba(34,211,238,.18),transparent 25%),radial-gradient(circle at 80% 25%,rgba(99,102,241,.16),transparent 25%),linear-gradient(125deg,#020617,#0b1024,#020617);animation:bg 16s ease-in-out infinite alternate}.stApp:after{content:"";position:fixed;inset:0;z-index:-4;opacity:.15;background-image:linear-gradient(rgba(125,211,252,.15) 1px,transparent 1px),linear-gradient(90deg,rgba(125,211,252,.15) 1px,transparent 1px);background-size:58px 58px;transform:perspective(700px) rotateX(58deg) scale(1.7);transform-origin:center bottom;animation:grid 10s linear infinite}@keyframes bg{from{transform:scale(1)}to{transform:scale(1.05)}}@keyframes grid{from{background-position:0 0,0 0}to{background-position:0 116px,116px 0}}.login-box{min-height:370px;display:flex;align-items:center;justify-content:center;border:1px solid rgba(255,255,255,.12);border-radius:28px;background:rgba(15,23,42,.68);backdrop-filter:blur(14px);position:relative;overflow:hidden}.login-grid{position:absolute;inset:0;opacity:.16;background-image:linear-gradient(rgba(255,255,255,.12) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.12) 1px,transparent 1px);background-size:44px 44px;transform:perspective(520px) rotateX(62deg) scale(1.7);transform-origin:center bottom;animation:grid2 9s linear infinite}.login-emoji{font-size:4rem;animation:float 3.5s ease-in-out infinite}@keyframes grid2{from{background-position:0 0,0 0}to{background-position:0 88px,88px 0}}@keyframes float{50%{transform:translateY(-9px)}}</style>""",unsafe_allow_html=True)

def login():
    if AUTOREFRESH_AVAILABLE:st_autorefresh(interval=60000,key="principal_login")
    css(); st.markdown(f'<div class="login-box"><div class="login-grid"></div><div style="position:relative;text-align:center"><div class="login-emoji">{visual()}</div><h1>Principal Dashboard</h1><p>Restricted academic monitoring</p><small>Visual changes every minute</small></div></div>',unsafe_allow_html=True)
    with st.form("login"):
        u=st.text_input("Username"); p=st.text_input("Password",type="password"); ok=st.form_submit_button("🔐 Login",type="primary",use_container_width=True)
    if ok:
        if u==PRINCIPAL_USERNAME and p==PRINCIPAL_PASSWORD:st.session_state.auth=True;st.rerun()
        else:st.error("Invalid username or password.")

def dashboard():
    css(); st.title("🛡️ Principal Academic Dashboard"); st.caption(f"Updated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if st.button("🚪 Logout"):st.session_state.auth=False;st.rerun()
    regs=load_csv(REG_FILE,REG_COLS); tutors=load_csv(TUTOR_FILE,TUTOR_COLS); cards=load_csv(CARD_FILE,CARD_COLS); reports=load_csv(REPORT_FILE,["Username","Student_Name","University_ID","Semester","Department","Created_Time","Subjects_JSON"]); audit=load_csv(AUDIT_FILE,AUDIT_COLS)
    a,b,c,d,e=st.columns(5);a.metric("👨‍🎓 Students",len(regs));b.metric("👨‍🏫 Tutors",len(tutors));c.metric("🪪 Smart Cards",len(cards));d.metric("📝 Mark Submissions",len(reports));e.metric("📡 Activity",len(audit))
    t1,t2,t3,t4,t5=st.tabs(["👨‍🎓 Students","👨‍🏫 Tutors","🪪 Smart Cards","📝 Marks","📡 Activity"])
    with t1:
        if regs.empty:st.info("No student registrations yet.")
        else:
            dept=st.selectbox("Department",["All"]+DEPARTMENTS,key="pdept");sem=st.selectbox("Semester",["All"]+SEMESTERS,key="psem");x=regs.copy()
            if dept!="All":x=x[x.Department.eq(dept)]
            if sem!="All":x=x[x.Semester.eq(sem)]
            st.dataframe(x,use_container_width=True,hide_index=True)
    with t2:
        if tutors.empty:st.info("No tutor profiles yet.")
        else:st.dataframe(tutors,use_container_width=True,hide_index=True)
    with t3:
        if cards.empty:st.info("No smart card registrations yet.")
        else:
            st.dataframe(cards,use_container_width=True,hide_index=True);st.download_button("📥 Download Smart Card Details CSV",cards.to_csv(index=False).encode(),"smart_card_details.csv","text/csv",use_container_width=True)
    with t4:
        if reports.empty:st.info("No mark submissions yet.")
        else:st.dataframe(reports.sort_values("Created_Time",ascending=False),use_container_width=True,hide_index=True)
    with t5:
        if audit.empty:st.info("No activity yet.")
        else:st.dataframe(audit.sort_values("Timestamp",ascending=False),use_container_width=True,hide_index=True)

if not st.session_state.get("auth",False):login()
else:dashboard()
