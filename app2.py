import json
from datetime import datetime
import pandas as pd
import streamlit as st

try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except Exception:
    SUPABASE_AVAILABLE = False

st.set_page_config(page_title="EduPredict SPP • Principal", page_icon="🛡️", layout="wide")

PRINCIPAL_USERNAME = "Principal"
PRINCIPAL_PASSWORD = "2026"

def inject_principal_css():
    st.markdown("""
    <style>
    .stApp { min-height:100vh; color:#eef6ff; background:#020817; overflow-x:hidden; }
    .stApp::before {
      content:""; position:fixed; inset:-20%; z-index:-5; pointer-events:none;
      background:
        radial-gradient(circle at 12% 18%, rgba(14,165,233,.30), transparent 22%),
        radial-gradient(circle at 88% 22%, rgba(37,99,235,.28), transparent 24%),
        radial-gradient(circle at 55% 92%, rgba(59,130,246,.22), transparent 27%),
        linear-gradient(125deg,#020817,#06285d 50%,#020817);
      animation: pbg 15s ease-in-out infinite alternate;
    }
    .principal-wallpaper { position:fixed; inset:0; z-index:-3; pointer-events:none; overflow:hidden; perspective:1100px; }
    .p-orb { position:absolute; border-radius:50%; transform-style:preserve-3d; filter:blur(.4px); mix-blend-mode:screen; }
    .p-a { width:270px;height:270px;left:5%;top:14%; background:radial-gradient(circle at 28% 25%,#fff,#38bdf8 10%,#2563eb 38%,transparent 72%); box-shadow:0 0 100px rgba(14,165,233,.28); animation: pa 12s ease-in-out infinite; }
    .p-b { width:330px;height:330px;right:2%;top:8%; background:radial-gradient(circle at 30% 25%,#fff,#60a5fa 9%,#1d4ed8 38%,transparent 72%); box-shadow:0 0 110px rgba(37,99,235,.28); animation: pb 16s ease-in-out infinite; }
    .p-c { width:190px;height:190px;right:27%;bottom:2%; background:radial-gradient(circle at 30% 25%,#fff,#7dd3fc 9%,#0284c7 38%,transparent 72%); animation: pc 10s ease-in-out infinite; }
    .p-ring { position:absolute; border:1px solid rgba(125,211,252,.22); border-radius:50%; transform-style:preserve-3d; }
    .p-ring.one { width:520px;height:520px;left:-180px;bottom:-250px; transform:rotateX(68deg); animation: ring 20s linear infinite; }
    .p-ring.two { width:600px;height:600px;right:-240px;top:25%; transform:rotateY(70deg); animation:ring2 25s linear infinite; }
    .p-cube { position:absolute; width:90px;height:90px;right:23%;top:39%; transform-style:preserve-3d; animation:cube 14s linear infinite; opacity:.32; }
    .p-cube i { position:absolute; inset:0; border:1px solid rgba(125,211,252,.6); background:rgba(59,130,246,.05); }
    .p-cube i:nth-child(1){transform:translateZ(45px)} .p-cube i:nth-child(2){transform:rotateY(180deg) translateZ(45px)} .p-cube i:nth-child(3){transform:rotateY(90deg) translateZ(45px)} .p-cube i:nth-child(4){transform:rotateY(-90deg) translateZ(45px)} .p-cube i:nth-child(5){transform:rotateX(90deg) translateZ(45px)} .p-cube i:nth-child(6){transform:rotateX(-90deg) translateZ(45px)}
    @keyframes pbg{from{transform:scale(1)}to{transform:scale(1.07) rotate(.5deg)}}
    @keyframes pa{0%,100%{transform:translate3d(0,0,0)}50%{transform:translate3d(100px,40px,150px)}}
    @keyframes pb{0%,100%{transform:translate3d(0,0,0)}50%{transform:translate3d(-80px,80px,-80px)}}
    @keyframes pc{0%,100%{transform:translate3d(0,0,0)}50%{transform:translate3d(-120px,-40px,120px) scale(1.12)}}
    @keyframes ring{to{transform:rotateX(68deg) rotateZ(360deg)}} @keyframes ring2{to{transform:rotateY(70deg) rotateZ(-360deg)}}
    @keyframes cube{to{transform:rotateX(360deg) rotateY(360deg) rotateZ(180deg)}}
    .block-container{position:relative;z-index:2;max-width:1250px;padding-top:2rem;}
    .glass-panel{padding:22px;border-radius:22px;border:1px solid rgba(147,197,253,.16);background:rgba(3,15,38,.70);backdrop-filter:blur(16px);box-shadow:0 24px 70px rgba(0,0,0,.30);}
    .smart-preview{max-width:520px;margin:auto;padding:22px;border-radius:22px;background:linear-gradient(135deg,#06142e,#0b4aa2,#123f8f);border:1px solid rgba(191,219,254,.25);box-shadow:0 22px 70px rgba(0,0,0,.35);font-weight:700;}
    @media (prefers-reduced-motion:reduce){.stApp::before,.principal-wallpaper *{animation:none!important}}
    </style>
    <div class="principal-wallpaper" aria-hidden="true"><div class="p-orb p-a"></div><div class="p-orb p-b"></div><div class="p-orb p-c"></div><div class="p-ring one"></div><div class="p-ring two"></div><div class="p-cube"><i></i><i></i><i></i><i></i><i></i><i></i></div></div>
    """, unsafe_allow_html=True)



def secret_value(*names):
    for name in names:
        try:
            value = st.secrets.get(name, "")
        except Exception:
            value = ""
        if value:
            return str(value).strip()
    return ""


def get_supabase():
    if not SUPABASE_AVAILABLE:
        raise RuntimeError("Python package 'supabase' is not installed. Add supabase to requirements.txt.")
    url = secret_value("SUPABASE_URL", "SUPABASE_PROJECT_URL").rstrip("/")
    key = secret_value("SUPABASE_KEY", "SUPABASE_SECRET_KEY", "SUPABASE_SERVICE_ROLE_KEY")
    if url.endswith("/rest/v1"):
        url = url[:-8]
    if not url or not key:
        raise RuntimeError("Supabase Secrets are missing. Add SUPABASE_URL and SUPABASE_KEY in Streamlit Cloud.")
    return create_client(url, key)


def rows(response):
    return list(getattr(response, "data", None) or [])


def get_all(table, order_col=None):
    q = get_supabase().table(table).select("*")
    if order_col:
        q = q.order(order_col, desc=True)
    return rows(q.execute())


def parse_subjects(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            obj = json.loads(value)
            return obj if isinstance(obj, list) else []
        except Exception:
            return []
    return []


def _latest_work_state(audit):
    """Return the latest tutor completion state per tutor + student + scope."""
    events=[r for r in audit if str(r.get("role","")).strip().lower()=="tutor" and str(r.get("action","")).strip() in {"Tutor Work Completed","Tutor Work Saved - Pending Completion"}]
    latest={}
    for r in events:
        key=(str(r.get("username","")).strip().lower(),str(r.get("university_id","")).strip().lower(),str(r.get("department","")).strip().lower(),str(r.get("semester","")).strip().upper())
        stamp=str(r.get("timestamp", ""))
        if key not in latest or stamp >= str(latest[key].get("timestamp", "")):
            latest[key]=r
    return list(latest.values())

def extract_completed(audit):
    return [r for r in _latest_work_state(audit) if str(r.get("action","")).strip()=="Tutor Work Completed"]

def extract_pending(audit):
    return [r for r in _latest_work_state(audit) if str(r.get("action","")).strip()=="Tutor Work Saved - Pending Completion"]

def tutor_name_from_event(row):
    details = str(row.get("details", ""))
    m = __import__("re").search(r"Tutor=([^;]+)", details)
    if m:
        return m.group(1).strip()
    return str(row.get("username", "")).strip()

def salary_breakdown(completed):
    """One salary unit per completed student upload, scoped by tutor+department+semester."""
    groups = {}
    for r in completed:
        tutor = tutor_name_from_event(r) or str(r.get("username", "")).strip() or "Unknown"
        dept = str(r.get("department", "")).strip() or "Unknown"
        sem = str(r.get("semester", "")).strip().upper() or "Unknown"
        key = (tutor, dept, sem)
        groups[key] = groups.get(key, 0) + 1
    return groups


def credit_from_subjects(subjects):
    vals = []
    for x in subjects:
        try:
            if x.get("Tutor_Credit_10") is not None:
                vals.append(float(x.get("Tutor_Credit_10")))
                continue
            att = float(x.get("Attendance_Mark", 0)) / 5 * 100
            internal = float(x.get("Internal", 0)) / 40 * 100
            assignment = float(x.get("Assignment", 0)) / 15 * 100
            previous = float(x.get("Previous", 0)) / 60 * 100
            vals.append((att + internal + assignment + previous) / 40)
        except Exception:
            pass
    return round(sum(vals) / len(vals), 2) if vals else 0.0


def build_tutor_summary(tutors, marks, audit):
    completed = extract_completed(audit)
    pending = extract_pending(audit)
    groups = {}
    for r in completed + pending:
        tutor = tutor_name_from_event(r) or str(r.get("username", "")).strip() or "Unknown"
        dept = str(r.get("department", "")).strip() or "Unknown"
        sem = str(r.get("semester", "")).strip().upper() or "Unknown"
        key=(tutor,dept,sem)
        g=groups.setdefault(key,{"Completed Uploads":0,"Pending Uploads":0,"Last Activity":"—"})
        if str(r.get("action", "")).strip()=="Tutor Work Completed": g["Completed Uploads"] += 1
        else: g["Pending Uploads"] += 1
        g["Last Activity"] = max(g["Last Activity"],str(r.get("timestamp", "")))
    out=[]
    for (tutor,dept,sem),g in sorted(groups.items()):
        out.append({"Tutor Name":tutor,"Department":dept,"Semester":sem,**g})
    return pd.DataFrame(out)


def login():
    st.title("🛡️ EduPredict SPP — Principal Portal")
    st.caption("Live Tutor monitoring • Completed work • Salary analysis • Student monitoring")
    with st.form("principal_login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        ok = st.form_submit_button("🔐 Secure Login", type="primary", use_container_width=True)
    if ok:
        if u.strip() == PRINCIPAL_USERNAME and p == PRINCIPAL_PASSWORD:
            st.session_state.principal_auth = True
            st.rerun()
        else:
            st.error("Invalid username or password.")


def dashboard():
    inject_principal_css()
    try:
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=15000, key="principal_live_refresh")
    except Exception:
        pass
    st.title("🛡️ Principal Academic Monitoring")
    st.caption("LIVE shared Supabase • Tutor actions + completed work + salary + Smart Cards • " + datetime.now().strftime("%d %b %Y, %I:%M:%S %p"))

    c1, c2 = st.columns([1, 5])
    if c1.button("🚪 Logout"):
        st.session_state.principal_auth = False
        st.rerun()
    if c2.button("🔄 Refresh Live Data", type="primary"):
        st.rerun()

    try:
        sb = get_supabase()
        sb.table("students").select("university_id").limit(1).execute()
        students = get_all("students", "registered_at")
        tutors = get_all("tutors", "registered_at")
        marks = get_all("student_marks", "submitted_at")
        smart = get_all("smart_cards", "submitted_at")
        audit = get_all("audit_logs", "timestamp")
    except Exception as exc:
        st.error(f"❌ Could not connect/load Supabase data: {exc}")
        st.info("Both Streamlit apps must use the same SUPABASE_URL and SUPABASE_KEY secrets and the same six Supabase tables.")
        return

    completed = extract_completed(audit)
    pending = extract_pending(audit)
    tutor_actions = [r for r in audit if str(r.get("role", "")).strip().lower() == "tutor"]

    a,b,c,d,e = st.columns(5)
    a.metric("👨‍🎓 Students", len(students))
    b.metric("👨‍🏫 Tutors", len(tutors))
    c.metric("📝 Mark Records", len(marks))
    d.metric("✅ Completed Tutor Work", len(completed))
    e.metric("🪪 Smart Cards", len(smart))

    st.success("🟢 LIVE: Tutor completion records are read from the same Supabase database used by the Student/Tutor app.")

    tab1, tab2, tab3 = st.tabs([
        "👨‍🏫 Live Tutor Activity", "💰 Tutor Salary Analysis", "🪪 Smart Cards"
    ])

    with tab1:
        st.subheader("🔴 Live Tutor Activity")
        if tutor_actions:
            activity = pd.DataFrame([{
                "Time": r.get("timestamp", ""),
                "Tutor Name": tutor_name_from_event(r),
                "Action": r.get("action", ""),
                "University ID": r.get("university_id", ""),
                "Department": r.get("department", ""),
                "Semester": r.get("semester", ""),
                "Details": r.get("details", ""),
            } for r in tutor_actions])
            st.dataframe(activity, use_container_width=True, hide_index=True)
            st.download_button("📥 Download Tutor Activity CSV", activity.to_csv(index=False).encode(), "tutor_activity.csv", "text/csv")
        else:
            st.info("No Tutor activity recorded yet.")

        st.subheader("📊 Tutor Work Summary")
        summary = build_tutor_summary(tutors, marks, audit)
        if summary.empty:
            st.info("No tutor work available yet.")
        else:
            st.dataframe(summary, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("💰 Tutor Salary Analysis")
        st.info("Only work explicitly marked **Completed** by the Tutor is counted. Pending work is not included in salary.")
        rate = st.number_input("Salary per completed student work (₹)", min_value=0.0, value=100.0, step=10.0, key="principal_salary_rate")
        summary = build_tutor_summary(tutors, marks, audit)
        if summary.empty:
            st.info("No tutor work available for salary calculation.")
        else:
            salary = summary.copy()
            salary["Salary (₹)"] = salary["Completed Uploads"] * float(rate)
            salary = salary[["Tutor Name","Department","Semester","Completed Uploads","Pending Uploads","Salary (₹)"]]
            st.dataframe(salary, use_container_width=True, hide_index=True)
            total = float(salary["Salary (₹)"].sum())
            x,y,z = st.columns(3)
            x.metric("✅ Completed Uploads", int(salary["Completed Uploads"].sum()))
            y.metric("⏳ Pending Uploads", int(salary["Pending Uploads"].sum()))
            z.metric("💰 Total Tutor Salary", f"₹{total:,.2f}")
            st.caption("Salary rule: each completed student mark upload = 1 salary unit. The unit is counted only for the tutor's assigned department + selected semester. Pending uploads receive no salary.")

        st.subheader("✅ Completed Work Details")
        if completed:
            details = pd.DataFrame([{
                "Completed At": r.get("timestamp", ""),
                "Tutor": tutor_name_from_event(r),
                "Student": r.get("university_id", ""),
                "Department": r.get("department", ""),
                "Semester": r.get("semester", ""),
                "Details": r.get("details", ""),
            } for r in completed])
            st.dataframe(details, use_container_width=True, hide_index=True)
        else:
            st.info("No Tutor work has been marked Completed yet.")

    with tab3:
        st.subheader("🪪 Smart Card + Full Student Monitoring")
        st.caption("Principal can see the complete Smart Card details, student profile, tutor directory, and live tutor work from the shared database.")
        if smart:
            latest_card = smart[0]
            st.markdown(f"""<div class='smart-preview' style='background:linear-gradient(135deg,#062a6b,#0b63ce,#12a4d8,#083b8f);font-size:1.05rem;line-height:1.7;position:relative;overflow:hidden'>
            <div style='font-size:.92rem;letter-spacing:.16em;color:#e0f2fe;font-weight:800'>EDUPREDICT SPP • STUDENT IDENTITY CARD</div>
            <div style='font-size:2.25rem;font-weight:900;color:white;margin-top:8px'>{latest_card.get('name','')}</div>
            <div style='font-family:monospace;font-size:1.35rem;color:white;font-weight:800'>{latest_card.get('registration_id','')}</div>
            <div style='display:grid;grid-template-columns:1fr 1fr;gap:8px 20px;margin-top:18px'>
            <div><b>DOB</b><br>{latest_card.get('dob','')}</div><div><b>Blood Group</b><br>{latest_card.get('blood_group','')}</div>
            <div><b>University ID</b><br>{latest_card.get('university_id','')}</div><div><b>PIN Code</b><br>{latest_card.get('pin_code','')}</div>
            <div><b>Department</b><br>{latest_card.get('department','')}</div><div><b>Semester</b><br>{latest_card.get('semester','')}</div>
            <div><b>CGPA</b><br>{latest_card.get('cgpa','') or '—'}</div><div><b>University</b><br>{latest_card.get('university_name','')}</div>
            <div style='grid-column:1/-1'><b>Studied College</b><br>{latest_card.get('studied_college','')}</div>
            <div style='grid-column:1/-1'><b>Address</b><br>{latest_card.get('address','')}</div>
            </div></div>""", unsafe_allow_html=True)
            sdf = pd.DataFrame([{
                "Registration ID": r.get("registration_id", ""), "Name": r.get("name", ""), "University ID": r.get("university_id", ""),
                "DOB": r.get("dob", ""), "Blood Group": r.get("blood_group", ""), "Address": r.get("address", ""),
                "PIN Code": r.get("pin_code", ""), "Studied College": r.get("studied_college", ""), "Department": r.get("department", ""),
                "Semester": r.get("semester", ""), "CGPA": r.get("cgpa", ""), "University": r.get("university_name", ""), "Submitted": r.get("submitted_at", ""),
            } for r in smart])
            st.dataframe(sdf, use_container_width=True, hide_index=True)
            st.download_button("📥 Download All Smart Card Records", sdf.to_csv(index=False).encode(), "all_smart_cards.csv", "text/csv")
        else:
            st.info("No Smart Cards registered yet.")

        st.subheader("👨‍🎓 Complete Student Profiles")
        if students:
            student_df=pd.DataFrame([{
                "University ID":r.get("university_id",""), "Student Name":r.get("student_name",""),
                "Department":r.get("department",""), "Semester":r.get("semester",""),
                "Studied College":r.get("studied_college","") or "", "Registered By":r.get("registered_by",""),
                "Registered At":r.get("registered_at","")
            } for r in students])
            st.dataframe(student_df,use_container_width=True,hide_index=True)
        else:
            st.info("No student profiles available.")

        st.subheader("👨‍🏫 Tutor Directory")
        if tutors:
            tutor_df=pd.DataFrame([{
                "Tutor Username":r.get("tutor_id",""), "Tutor Name":r.get("tutor_name",""),
                "Department":r.get("department",""), "Semester":r.get("semester","") or "All",
                "Active":r.get("active",True),
                "Registered At":r.get("registered_at","")
            } for r in tutors])
            st.dataframe(tutor_df,use_container_width=True,hide_index=True)
        else:
            st.info("No tutor profiles available yet.")


if "principal_auth" not in st.session_state:
    st.session_state.principal_auth = False

if not st.session_state.principal_auth:
    login()
else:
    dashboard()
