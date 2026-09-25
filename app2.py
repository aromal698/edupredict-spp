import os
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Academic Monitoring Console", page_icon="🛡️", layout="wide", initial_sidebar_state="collapsed")
DATA_DIR = "data"
REPORT_FILE = os.path.join(DATA_DIR, "student_reports.csv")
REG_FILE = os.path.join(DATA_DIR, "student_registrations.csv")
AUDIT_FILE = os.path.join(DATA_DIR, "audit_log.csv")
SMART_CARD_FILE = os.path.join(DATA_DIR, "smart_card_registrations.csv")

PRINCIPAL_USERNAME = os.getenv("PRINCIPAL_USERNAME", "Principal")
PRINCIPAL_PASSWORD = os.getenv("PRINCIPAL_PASSWORD", "2026")

DEPARTMENTS = [
    "Computer Science and Engineering", "Artificial Intelligence and Data Science",
    "Artificial Intelligence and Machine Learning", "Information Technology",
    "Electronics and Communication Engineering", "Electrical and Electronics Engineering",
    "Civil Engineering", "Mechanical Engineering",
]
SEMESTERS = [f"S{i}" for i in range(1,9)]
SMART_COLS=["Registration_ID","Student_Name","DOB","Blood_Group","Address","PIN_Code","Studied_College","Department","Semester","CGPA","University_Name","University_ID","Submitted_Time"]

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

def inject_wallpaper():
    import time
    minute_key=int(time.time()//60)
    palettes=[("#22d3ee","#6366f1","#a855f7","#020617"),("#34d399","#06b6d4","#3b82f6","#021014"),("#f59e0b","#ef4444","#ec4899","#16070a"),("#f472b6","#8b5cf6","#06b6d4","#0a0616"),("#60a5fa","#14b8a6","#84cc16","#04100c")]
    c1,c2,c3,base=palettes[minute_key%len(palettes)]
    try:
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=60000,key="principal_wallpaper_refresh")
    except Exception:
        pass
    st.markdown(f"""<style>
    .stApp{{background:{base};color:#eef2ff}}
    .stApp::before{{content:"";position:fixed;inset:-25%;z-index:-10;pointer-events:none;background:radial-gradient(circle at 15% 20%,{c1}33,transparent 24%),radial-gradient(circle at 82% 28%,{c2}33,transparent 25%),radial-gradient(circle at 52% 88%,{c3}2e,transparent 27%),linear-gradient(135deg,{base},#020617 55%,{base});animation:pp 16s ease-in-out infinite alternate}}
    .pd3d{{position:fixed;inset:0;z-index:-8;pointer-events:none;overflow:hidden;perspective:1200px}}
    .pdgrid{{position:absolute;left:-15%;width:130%;height:75%;bottom:-28%;opacity:.2;background-image:linear-gradient(#ffffff29 1px,transparent 1px),linear-gradient(90deg,#ffffff29 1px,transparent 1px);background-size:54px 54px;transform:rotateX(64deg) translateZ(-120px);animation:gr 7s linear infinite}}
    .pdorb{{position:absolute;border-radius:50%;transform-style:preserve-3d}} .a{{width:210px;height:210px;left:5%;top:10%;background:radial-gradient(circle at 28% 24%,#fff 0 4%,{c1} 16%,{c2} 52%,transparent 72%);animation:o1 13s ease-in-out infinite;box-shadow:0 0 90px {c1}55}} .b{{width:165px;height:165px;right:9%;top:16%;background:radial-gradient(circle at 30% 22%,#fff 0 3%,{c3} 18%,{c2} 58%,transparent 73%);animation:o2 16s ease-in-out infinite}}
    .pdring{{position:absolute;width:210px;height:210px;border:3px solid {c1}aa;border-radius:50%;transform-style:preserve-3d;box-shadow:0 0 35px {c1}44;animation:rr 12s linear infinite}} .ra{{right:22%;bottom:18%}} .rb{{left:19%;top:48%;width:145px;height:145px;border-color:{c3}aa;animation-direction:reverse}}
    .pdcube{{position:absolute;left:47%;top:34%;width:110px;height:110px;transform-style:preserve-3d;animation:cu 14s linear infinite}} .pdcube span{{position:absolute;inset:0;border:2px solid {c2}bb;background:{c2}08}} .f{{transform:translateZ(55px)}} .bk{{transform:rotateY(180deg) translateZ(55px)}} .l{{transform:rotateY(-90deg) translateZ(55px)}} .r{{transform:rotateY(90deg) translateZ(55px)}} .t{{transform:rotateX(90deg) translateZ(55px)}} .bt{{transform:rotateX(-90deg) translateZ(55px)}}
    @keyframes pp{{50%{{transform:scale(1.08) rotate(1deg)}}100%{{transform:scale(1.02) rotate(-1deg)}}}} @keyframes gr{{to{{background-position:0 108px,108px 0}}}} @keyframes o1{{50%{{transform:translate3d(100px,70px,180px) rotateX(160deg) rotateY(220deg)}}}} @keyframes o2{{50%{{transform:translate3d(-120px,80px,150px) rotateZ(180deg)}}}} @keyframes rr{{to{{transform:rotateX(425deg) rotateY(360deg) rotateZ(180deg) translateZ(130px)}}}} @keyframes cu{{to{{transform:rotateX(360deg) rotateY(360deg) rotateZ(360deg) translateZ(80px)}}}}
    </style><div class="pd3d"><div class="pdgrid"></div><div class="pdorb a"></div><div class="pdorb b"></div><div class="pdring ra"></div><div class="pdring rb"></div><div class="pdcube"><span class=f></span><span class=bk></span><span class=l></span><span class=r></span><span class=t></span><span class=bt></span></div></div>
    """,unsafe_allow_html=True)

inject_wallpaper()

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

def load_smart_cards():
    if not os.path.exists(SMART_CARD_FILE): return pd.DataFrame(columns=SMART_COLS)
    try:
        df=pd.read_csv(SMART_CARD_FILE,dtype=str).fillna("")
        for c in SMART_COLS:
            if c not in df.columns: df[c]=""
        return df[SMART_COLS]
    except Exception:
        return pd.DataFrame(columns=SMART_COLS)

def dashboard():
    st.markdown("# 🛡️ Principal Academic Monitoring")
    st.caption(f"Live monitoring console • Last opened: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if st.button("🚪 Logout", use_container_width=False):
        st.session_state.auth=False; st.rerun()
    regs=load_csv(REG_FILE, REG_COLS)
    reports=load_csv(REPORT_FILE, ["Username","Student_Name","University_ID","Semester","Department","Created_Time","Subjects_JSON"])
    audit=load_csv(AUDIT_FILE, AUDIT_COLS)
    smart=load_smart_cards()
    a,b,c,d=st.columns(4)
    a.metric("👨‍🎓 Registered Students", len(regs))
    b.metric("📝 Mark Submissions", len(reports))
    c.metric("👨‍🏫 Tutors Active in Records", audit[audit.Role.eq("Tutor")]["Username"].nunique() if not audit.empty else 0)
    d.metric("📡 Audit Events", len(audit))
    st.metric("🪪 Smart Cards", len(smart))
    st.divider()
    tab1,tab2,tab3,tab4,tab5=st.tabs(["🏫 Students","👨‍🏫 Tutor Activity","📊 Mark Activity","🛰️ Audit Timeline","🪪 Smart Cards"])
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
    with tab5:
        st.subheader("Student Smart Card Registrations")
        if smart.empty: st.info("No Smart Card registrations yet.")
        else:
            st.dataframe(smart.sort_values("Submitted_Time", ascending=False), use_container_width=True, hide_index=True)
            st.download_button("📥 Download Smart Card Details CSV", smart.to_csv(index=False).encode("utf-8"), "smart_card_registrations.csv", "text/csv", use_container_width=True)
    st.success("🟢 Monitoring status: connected to the local data/audit store.")
    st.caption("For separate hosted websites, use a shared database/storage service rather than relying on each Streamlit app's local filesystem.")

if not st.session_state.get("auth",False): login()
else: dashboard()
