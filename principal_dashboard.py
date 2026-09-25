import pandas as pd
import streamlit as st
from datetime import datetime

from db import (
    test_connection,
    get_students,
    get_tutors,
    get_marks,
    get_smart_cards,
    get_audit_logs,
    get_files,
)

st.set_page_config(page_title="EduPredict SPP • Principal", page_icon="🛡️", layout="wide", initial_sidebar_state="collapsed")

PRINCIPAL_USERNAME = "Principal"
PRINCIPAL_PASSWORD = "2026"
DEPARTMENTS = [
    "Computer Science and Engineering", "Artificial Intelligence and Data Science",
    "Artificial Intelligence and Machine Learning", "Information Technology",
    "Electronics and Communication Engineering", "Electrical and Electronics Engineering",
    "Civil Engineering", "Mechanical Engineering",
]
SEMESTERS=[f"S{i}" for i in range(1,9)]

if "auth" not in st.session_state:
    st.session_state.auth=False


def login():
    st.title("🛡️ EduPredict SPP — Principal Portal")
    st.caption("Live academic monitoring • Shared Supabase database")
    with st.form("principal_login"):
        u=st.text_input("Username")
        p=st.text_input("Password", type="password")
        ok=st.form_submit_button("🔐 Secure Login", type="primary", use_container_width=True)
    if ok:
        if u.strip()==PRINCIPAL_USERNAME and p==PRINCIPAL_PASSWORD:
            st.session_state.auth=True
            st.rerun()
        else:
            st.error("Invalid username or password.")


def frame_students(rows):
    cols=["University ID","Student Name","Department","Semester","Studied College","Registered By","Active","Registered At"]
    data=[]
    for r in rows:
        data.append([r.get("university_id",""),r.get("student_name",""),r.get("department",""),r.get("semester",""),r.get("studied_college",""),r.get("registered_by",""),r.get("active",True),r.get("registered_at","")])
    return pd.DataFrame(data,columns=cols)


def frame_tutors(rows):
    cols=["Tutor ID","Tutor Name","Department","Semester","Credit Score /10","Active","Registered At"]
    return pd.DataFrame([[r.get("tutor_id",""),r.get("tutor_name",""),r.get("department",""),r.get("semester",""),r.get("credit_score",0),r.get("active",True),r.get("registered_at","")] for r in rows],columns=cols)


def frame_marks(rows):
    data=[]
    for r in rows:
        subjects=r.get("subjects",[])
        if isinstance(subjects,str):
            try: import json; subjects=json.loads(subjects)
            except Exception: subjects=[]
        data.append({"University ID":r.get("university_id",""),"Department":r.get("department",""),"Semester":r.get("semester",""),"Tutor":r.get("tutor_name",""),"Subjects":len(subjects),"Submitted At":r.get("submitted_at","")})
    return pd.DataFrame(data)


def dashboard():
    st.title("🛡️ Principal Academic Monitoring")
    st.caption(f"Shared live database • {datetime.now().strftime('%d %b %Y, %I:%M:%S %p')}")
    if st.button("🚪 Logout"):
        st.session_state.auth=False; st.rerun()

    ok,msg=test_connection()
    if not ok:
        st.error(msg)
        st.info("Check that this Principal Streamlit app has the same SUPABASE_URL and SUPABASE_KEY secrets as the Student/Tutor app.")
        return
    st.success("🟢 Live connection: Student/Tutor and Principal are using the same Supabase database.")

    try:
        students=get_students(); tutors=get_tutors(); marks=get_marks(); smart=get_smart_cards(); audit=get_audit_logs()
    except Exception as exc:
        st.error(f"Could not load shared data: {exc}")
        return

    a,b,c,d,e=st.columns(5)
    a.metric("👨‍🎓 Students",len(students)); b.metric("👨‍🏫 Tutors",len(tutors)); c.metric("📝 Mark Records",len(marks)); d.metric("🪪 Smart Cards",len(smart)); e.metric("📡 Audit Events",len(audit))

    if st.button("🔄 Refresh Live Data", type="primary"):
        st.rerun()

    tab1,tab2,tab3,tab4,tab5=st.tabs(["🏫 Students","👨‍🏫 Tutors","📊 Marks","🪪 Smart Cards","🛰️ Activity"])
    with tab1:
        if not students: st.info("No students registered yet.")
        else:
            dept=st.selectbox("Department",["All"]+DEPARTMENTS,key="principal_dept")
            sem=st.selectbox("Semester",["All"]+SEMESTERS,key="principal_sem")
            filtered=students
            if dept!="All": filtered=[r for r in filtered if r.get("department")==dept]
            if sem!="All": filtered=[r for r in filtered if str(r.get("semester","")).upper()==sem]
            st.dataframe(frame_students(filtered),use_container_width=True,hide_index=True)
            st.download_button("📥 Download Students CSV",frame_students(filtered).to_csv(index=False).encode(),"students.csv","text/csv",use_container_width=True)
    with tab2:
        if not tutors: st.info("No tutor activity has been synchronized yet.")
        else:
            st.dataframe(frame_tutors(tutors),use_container_width=True,hide_index=True)
    with tab3:
        if not marks: st.info("No marks submitted yet.")
        else:
            st.dataframe(frame_marks(marks),use_container_width=True,hide_index=True)
    with tab4:
        if not smart: st.info("No Smart Cards registered yet.")
        else:
            rows=[]
            for r in smart:
                rows.append({"Registration ID":r.get("registration_id",""),"Name":r.get("name",""),"DOB":r.get("dob",""),"Blood Group":r.get("blood_group",""),"Address":r.get("address",""),"PIN Code":r.get("pin_code",""),"College":r.get("studied_college",""),"Department":r.get("department",""),"Semester":r.get("semester",""),"CGPA":r.get("cgpa",""),"University":r.get("university_name",""),"University ID":r.get("university_id",""),"Submitted":r.get("submitted_at","")})
            sdf=pd.DataFrame(rows)
            st.dataframe(sdf,use_container_width=True,hide_index=True)
            st.download_button("📥 Download Smart Card Details CSV",sdf.to_csv(index=False).encode(),"smart_card_registrations.csv","text/csv",use_container_width=True)
    with tab5:
        if not audit: st.info("No activity yet.")
        else:
            ad=pd.DataFrame([{"Timestamp":r.get("timestamp",""),"Role":r.get("role",""),"Username":r.get("username",""),"Action":r.get("action",""),"University ID":r.get("university_id",""),"Department":r.get("department",""),"Semester":r.get("semester",""),"Details":r.get("details","")} for r in audit])
            st.dataframe(ad,use_container_width=True,hide_index=True)

if not st.session_state.auth: login()
else: dashboard()
