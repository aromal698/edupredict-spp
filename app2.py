import json
import os
import re
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

def tutor_name_from_event(row, tutors=None):
    """Return ONLY the registered Tutor Name for Principal-facing records.
    Login IDs such as teacher_ce/teacher_aids are never shown.
    """
    username = str(row.get("username", "")).strip()
    details = str(row.get("details", ""))

    # First resolve the audit username against the Supabase tutors table.
    for t in (tutors or []):
        tid = str(t.get("tutor_id", "")).strip()
        name = str(t.get("tutor_name", "")).strip()
        if not name:
            continue
        if username and tid and username.lower() == tid.lower():
            return name
        if username and username.lower() == name.lower():
            return name

    # Older audit rows may have stored the tutor name in details.
    m = __import__("re").search(r"Tutor=([^;]+)", details)
    if m:
        candidate = m.group(1).strip()
        # Never return a teacher_* login ID from the details field.
        if candidate and not candidate.lower().startswith("teacher_"):
            return candidate
        for t in (tutors or []):
            if str(t.get("tutor_id", "")).strip().lower() == candidate.lower():
                return str(t.get("tutor_name", "")).strip() or "Registered Tutor"

    # If no real name can be resolved, use a safe display label instead of
    # exposing the authentication username.
    return "Registered Tutor"


def tutor_id_from_event(row):
    return str(row.get("username", "")).strip()

def salary_breakdown(completed):
    """One salary unit per completed student upload, scoped by tutor+department+semester."""
    groups = {}
    for r in completed:
        tutor = tutor_name_from_event(r, []) or "Registered Tutor"
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
        tutor = tutor_name_from_event(r, tutors) or str(r.get("username", "")).strip() or "Unknown"
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



def safe_folder_name(value, fallback="Unknown"):
    value = str(value or "").strip() or fallback
    return re.sub(r"[^A-Za-z0-9._ -]+", "_", value).strip()[:80] or fallback


def parse_event_dt(value):
    try:
        ts = pd.to_datetime(value, errors="coerce", utc=True)
        return ts
    except Exception:
        return pd.NaT


def month_label(value):
    ts = parse_event_dt(value)
    if pd.isna(ts):
        return "Unknown Month"
    return ts.strftime("%Y-%m")


def build_folder_records(students, tutors, marks, smart, audit, completed, rate):
    """Build department/semester virtual folders and monthly tutor salary folders."""
    folders = {}

    def ensure(dept, sem):
        dept = str(dept or "Unknown").strip() or "Unknown"
        sem = str(sem or "Unknown").strip().upper() or "Unknown"
        key = (dept, sem)
        folders.setdefault(key, {"students": [], "tutors": [], "marks": [], "smart": [], "audit": [], "analysis": {}})
        return folders[key]

    for r in students:
        ensure(r.get("department"), r.get("semester"))["students"].append(r)
    for r in tutors:
        ensure(r.get("department"), r.get("semester"))["tutors"].append(r)
    for r in marks:
        ensure(r.get("department"), r.get("semester"))["marks"].append(r)
    for r in smart:
        ensure(r.get("department"), r.get("semester"))["smart"].append(r)
    for r in audit:
        if str(r.get("role", "")).strip().lower() == "tutor":
            ensure(r.get("department"), r.get("semester"))["audit"].append(r)

    for (dept, sem), g in folders.items():
        done = [r for r in completed if str(r.get("department", "")).strip() == dept and str(r.get("semester", "")).strip().upper() == sem]
        pending_scope = [r for r in extract_pending(audit) if str(r.get("department", "")).strip() == dept and str(r.get("semester", "")).strip().upper() == sem]
        g["analysis"] = {
            "Students": len(g["students"]),
            "Tutors": len(g["tutors"]),
            "Mark Records": len(g["marks"]),
            "Smart Cards": len(g["smart"]),
            "Completed Uploads": len(done),
            "Pending Uploads": len(pending_scope),
            "Salary": len(done) * float(rate),
        }
    return folders


def write_runtime_folders(folders, completed, rate):
    """Create an organized runtime export tree. Supabase remains the permanent source of truth."""
    root = os.path.join(os.getcwd(), "principal_records")
    os.makedirs(root, exist_ok=True)
    for (dept, sem), g in folders.items():
        base = os.path.join(root, safe_folder_name(dept), f"Semester_{safe_folder_name(sem)}")
        for sub in ("Students", "Tutors", "Analysis"):
            os.makedirs(os.path.join(base, sub), exist_ok=True)
        for filename, data in (
            ("students_records.csv", g["students"]),
            ("tutors_records.csv", g["tutors"]),
            ("marks_records.csv", g["marks"]),
            ("smart_cards_records.csv", g["smart"]),
            ("tutor_activity.csv", g["audit"]),
        ):
            target = os.path.join(base, "Students" if filename.startswith(("students", "marks", "smart")) else "Tutors", filename)
            pd.DataFrame(data).to_csv(target, index=False)
        pd.DataFrame([g["analysis"]]).to_csv(os.path.join(base, "Analysis", "department_semester_analysis.csv"), index=False)

    # Tutor salary folders: Tutor Name / YYYY-MM
    salary_root = os.path.join(root, "Tutor Salary")
    os.makedirs(salary_root, exist_ok=True)
    by_month_tutor = {}
    for r in completed:
        tutor = tutor_name_from_event(r, tutors) or "Registered Tutor"
        month = month_label(r.get("timestamp"))
        key = (tutor, month)
        by_month_tutor.setdefault(key, []).append(r)
    for (tutor, month), records in by_month_tutor.items():
        d = os.path.join(salary_root, safe_folder_name(tutor), month)
        os.makedirs(d, exist_ok=True)
        rows_out = [{
            "Completed At": r.get("timestamp", ""), "Tutor": tutor,
            "University ID": r.get("university_id", ""), "Department": r.get("department", ""),
            "Semester": r.get("semester", ""), "Salary (₹)": float(rate),
        } for r in records]
        pd.DataFrame(rows_out).to_csv(os.path.join(d, "monthly_salary.csv"), index=False)

    return root


def folder_dataframe(data):
    return pd.DataFrame(data) if data else pd.DataFrame()

def write_daily_records(students, tutors, marks, smart, audit, completed, rate):
    """Create separate day-by-day CSV files from the current Supabase data.
    Each calendar day gets its own folder and files. These are regenerated from
    Supabase on every Principal refresh, so deleted students disappear from the
    current daily files too.
    """
    root = os.path.join(os.getcwd(), "principal_records", "Daily Records")
    os.makedirs(root, exist_ok=True)

    def day_of(value):
        ts = parse_event_dt(value)
        if pd.isna(ts):
            return "Unknown-Date"
        return ts.strftime("%Y-%m-%d")

    def write_rows(day, filename, rows):
        folder = os.path.join(root, safe_folder_name(day))
        os.makedirs(folder, exist_ok=True)
        pd.DataFrame(rows).to_csv(os.path.join(folder, filename), index=False)

    groups = {}
    for r in students:
        groups.setdefault(day_of(r.get("registered_at")), {"students": [], "tutors": [], "marks": [], "smart": [], "activity": [], "completed": []})["students"].append(r)
    for r in tutors:
        groups.setdefault(day_of(r.get("registered_at")), {"students": [], "tutors": [], "marks": [], "smart": [], "activity": [], "completed": []})["tutors"].append(r)
    for r in marks:
        groups.setdefault(day_of(r.get("submitted_at")), {"students": [], "tutors": [], "marks": [], "smart": [], "activity": [], "completed": []})["marks"].append(r)
    for r in smart:
        groups.setdefault(day_of(r.get("submitted_at")), {"students": [], "tutors": [], "marks": [], "smart": [], "activity": [], "completed": []})["smart"].append(r)
    for r in audit:
        groups.setdefault(day_of(r.get("timestamp")), {"students": [], "tutors": [], "marks": [], "smart": [], "activity": [], "completed": []})["activity"].append(r)
    for r in completed:
        groups.setdefault(day_of(r.get("timestamp")), {"students": [], "tutors": [], "marks": [], "smart": [], "activity": [], "completed": []})["completed"].append(r)

    for day, g in groups.items():
        write_rows(day, "students_records.csv", g["students"])
        write_rows(day, "tutors_records.csv", g["tutors"])
        write_rows(day, "marks_records.csv", g["marks"])
        write_rows(day, "smart_cards_records.csv", g["smart"])
        write_rows(day, "tutor_activity.csv", g["activity"])
        salary_rows = [{
            "Completed At": r.get("timestamp", ""), "Tutor": tutor_name_from_event(r, tutors),
            "University ID": r.get("university_id", ""), "Department": r.get("department", ""),
            "Semester": r.get("semester", ""), "Salary (₹)": float(rate),
        } for r in g["completed"]]
        write_rows(day, "completed_salary_records.csv", salary_rows)
    return root, sorted(groups.keys(), reverse=True)


def remove_runtime_student_records(uid):
    """Remove a student's UID from generated Principal CSV files on this runtime."""
    uid = str(uid or "").strip()
    if not uid:
        return 0
    root = os.path.join(os.getcwd(), "principal_records")
    removed = 0
    if not os.path.isdir(root):
        return removed
    for base, _, files in os.walk(root):
        for fn in files:
            if not fn.lower().endswith(".csv"):
                continue
            path = os.path.join(base, fn)
            try:
                df = pd.read_csv(path)
                before = len(df)
                for col in ["University ID", "university_id", "University_ID", "Student ID"]:
                    if col in df.columns:
                        df = df[df[col].astype(str).str.strip().ne(uid)]
                if len(df) != before:
                    df.to_csv(path, index=False)
                    removed += before - len(df)
            except Exception:
                pass
    return removed


def delete_student_everywhere(sb, student, audit_user="Principal"):
    """Delete one student and all related records from Supabase and known local files."""
    uid = str(student.get("university_id", "")).strip()
    if not uid:
        raise ValueError("Student University ID is missing.")
    dept = str(student.get("department", "") or "").strip()
    sem = str(student.get("semester", "") or "").strip().upper()

    file_rows = rows(sb.table("student_files").select("file_path,file_name").eq("university_id", uid).execute())
    # Remove the student's old Principal/Tutor activity records so the student
    # disappears from Principal activity, folders, daily files and salary views.
    try:
        sb.table("audit_logs").delete().eq("university_id", uid).execute()
    except Exception:
        pass
    sb.table("student_marks").delete().eq("university_id", uid).execute()
    sb.table("smart_cards").delete().eq("university_id", uid).execute()
    sb.table("student_files").delete().eq("university_id", uid).execute()
    sb.table("students").delete().eq("university_id", uid).execute()

    removed_files = 0
    for item in file_rows:
        path = str(item.get("file_path") or "").strip()
        if path and os.path.isfile(path):
            try:
                os.remove(path)
                removed_files += 1
            except OSError:
                pass

    remove_runtime_student_records(uid)

    sb.table("audit_logs").insert({
        "username": audit_user,
        "role": "Principal",
        "action": "Student Deleted",
        "university_id": uid,
        "department": dept,
        "semester": sem,
        "details": f"Deleted student {student.get('student_name', '')}; removed marks, Smart Card, student files and registration. Local files removed: {removed_files}."
    }).execute()
    return uid, removed_files


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


def tutor_accounts_for_principal(sb):
    try: return list(getattr(sb.table("tutor_accounts").select("*").order("tutor_name").execute(),"data",None) or [])
    except Exception: return []

def salary_transactions_for_principal(sb):
    try: return list(getattr(sb.table("tutor_salary_transactions").select("*").order("sent_at",desc=True).execute(),"data",None) or [])
    except Exception: return []

def credit_tutor_salary(sb,account,amount,salary_month,reference):
    email=str(account.get("email") or account.get("tutor_id") or "").strip().lower(); name=str(account.get("tutor_name") or "").strip(); amount=float(amount)
    if not email or not name: raise ValueError("Tutor account is incomplete.")
    if amount<=0: raise ValueError("Salary amount must be greater than ₹0.")
    new_balance=float(account.get("balance") or 0)+amount
    sb.table("tutor_accounts").update({"balance":new_balance}).eq("email",email).execute()
    sb.table("tutor_salary_transactions").insert({"tutor_id":email,"tutor_name":name,"amount":amount,"salary_month":str(salary_month),"sent_by":PRINCIPAL_USERNAME,"reference":str(reference or "").strip(),"status":"credited"}).execute()
    sb.table("audit_logs").insert({"username":PRINCIPAL_USERNAME,"role":"Principal","action":"Tutor Salary Credited","university_id":"","department":str(account.get("department") or ""),"semester":str(account.get("semester") or "").upper(),"details":f"Tutor={name}; Email={email}; Amount=₹{amount:.2f}; Month={salary_month}; Reference={reference}"}).execute()
    return new_balance


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
        tutor_accounts = tutor_accounts_for_principal(sb)
        salary_transactions = salary_transactions_for_principal(sb)
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

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "👁️ Monitoring", "💰 Salary", "📱 Normal App", "🪪 Smart Cards", "📁 Academic Folders", "📅 Daily Records", "🗑️ Delete Student"
    ])

    with tab1:
        st.subheader("🔴 Live Tutor Activity")
        if tutor_actions:
            activity = pd.DataFrame([{
                "Time": r.get("timestamp", ""),
                "Tutor Name": tutor_name_from_event(r, tutors),
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
        st.info("Salary is based on the number of students each tutor successfully completes/registers. Every completed student = one salary unit.")
        rate = st.number_input("Salary per completed/registered student (₹)", min_value=0.0, value=100.0, step=10.0, key="principal_salary_rate")

        # Count tutor work from Completed audit records, grouped by tutor.
        tutor_rows = []
        for tutor in tutors:
            tid = str(tutor.get("tutor_id", "")).strip()
            tname = str(tutor.get("tutor_name", "") or tid or "Unknown")
            dept = str(tutor.get("department", "") or "")
            sem = str(tutor.get("semester", "") or "").upper()
            own = [r for r in completed if str(r.get("username", "")).strip().lower() == tid.lower()]
            # Also match events where the tutor name itself was stored.
            own += [r for r in completed if tutor_name_from_event(r, tutors).strip().lower() == tname.lower() and r not in own]
            unique_students = {str(r.get("university_id", "")).strip() for r in own if str(r.get("university_id", "")).strip()}
            tutor_rows.append({
                "Tutor Name": tname, "Department": dept, "Semester": sem,
                "Students Completed": len(unique_students),
                "Completed Work": len(own),
                "Salary (₹)": len(unique_students) * float(rate),
            })

        salary_df = pd.DataFrame(tutor_rows)
        if salary_df.empty:
            st.info("No tutors registered yet.")
        else:
            salary_df = salary_df.sort_values("Tutor Name")
            st.subheader("👨‍🏫 Tutor-wise Salary Table")
            st.dataframe(salary_df, use_container_width=True, hide_index=True)
            st.download_button("📥 Download Tutor Salary Table", salary_df.to_csv(index=False).encode(), "tutor_salary_table.csv", "text/csv", use_container_width=True)
            x,y,z = st.columns(3)
            x.metric("👨‍🏫 Tutors", len(salary_df))
            y.metric("👥 Students Completed", int(salary_df["Students Completed"].sum()))
            z.metric("💰 Total Salary", f"₹{salary_df['Salary (₹)'].sum():,.2f}")

        st.subheader("💳 Send Salary to Tutor Account")
        if tutor_accounts:
            account_options={f"{a.get('tutor_name','')} — {a.get('department','')} — {a.get('semester','')}":a for a in tutor_accounts}
            label=st.selectbox("Select tutor account",list(account_options.keys()),key="principal_salary_account")
            account=account_options[label]
            c1,c2,c3=st.columns(3)
            amount=c1.number_input("Salary Amount (₹)",min_value=0.0,value=1000.0,step=100.0,key="principal_credit_amount")
            salary_month=c2.text_input("Salary Month",value=datetime.now().strftime("%Y-%m"),key="principal_salary_month")
            reference=c3.text_input("Reference / Note",placeholder="September salary",key="principal_salary_reference")
            st.caption(f"Tutor account: **{account.get('tutor_name','')}**  •  Current balance: **₹{float(account.get('balance') or 0):,.2f}**")
            if st.button("💸 Credit Salary to This Tutor Account",type="primary",use_container_width=True,key="credit_salary_button"):
                try:
                    new_balance=credit_tutor_salary(sb,account,amount,salary_month,reference)
                    st.success(f"✅ ₹{amount:,.2f} credited to {account.get('tutor_name','')} salary account. New balance: ₹{new_balance:,.2f}")
                    st.rerun()
                except Exception as exc: st.error(f"❌ Salary credit failed: {exc}")
            st.subheader("💰 Tutor Account Balances")
            balances=pd.DataFrame([{"Tutor Name":a.get("tutor_name",""),"Department":a.get("department",""),"Semester":str(a.get("semester","")).upper(),"Account Balance (₹)":float(a.get("balance") or 0),"Account Created":a.get("created_at","")} for a in tutor_accounts])
            st.dataframe(balances,use_container_width=True,hide_index=True)
            if salary_transactions:
                st.subheader("📜 Salary Credit History")
                txdf=pd.DataFrame([{"Date":x.get("sent_at",""),"Tutor Name":x.get("tutor_name",""),"Month":x.get("salary_month",""),"Amount (₹)":float(x.get("amount") or 0),"Reference":x.get("reference",""),"Status":x.get("status","")} for x in salary_transactions])
                st.dataframe(txdf,use_container_width=True,hide_index=True)
        else: st.info("No email-based tutor accounts have been created yet. Create one from the 👤 circle icon on the Tutor Login page.")

        st.subheader("📅 Monthly Salary — Every Tutor")
        if completed:
            monthly_rows = []
            for r in completed:
                uid = str(r.get("university_id", "")).strip()
                monthly_rows.append({
                    "Month": month_label(r.get("timestamp")),
                    "Tutor Name": tutor_name_from_event(r, tutors),
                    "Department": r.get("department", ""),
                    "Semester": str(r.get("semester", "")).upper(),
                    "Students Completed": 1 if uid else 0,
                    "Salary (₹)": float(rate) if uid else 0.0,
                })
            monthly = pd.DataFrame(monthly_rows).groupby(
                ["Month", "Tutor Name", "Department", "Semester"], as_index=False
            ).agg({"Students Completed":"sum", "Salary (₹)":"sum"}).sort_values(["Month", "Tutor Name"], ascending=[False, True])
            st.dataframe(monthly, use_container_width=True, hide_index=True)
            st.download_button("📥 Download Monthly Tutor Salary", monthly.to_csv(index=False).encode(), "monthly_tutor_salary.csv", "text/csv", use_container_width=True)
        else:
            st.info("No completed tutor work for monthly salary yet.")

        st.subheader("✅ Tutor Completed Work + Salary Details")
        if completed:
            details = pd.DataFrame([{
                "Completed At": r.get("timestamp", ""),
                "Tutor": tutor_name_from_event(r, tutors),
                "Student University ID": r.get("university_id", ""),
                "Department": r.get("department", ""),
                "Semester": r.get("semester", ""),
                "Salary (₹)": float(rate),
            } for r in completed])
            st.dataframe(details, use_container_width=True, hide_index=True)
        else:
            st.info("No Tutor work has been marked Completed yet.")

    with tab3:
        st.subheader("📱 Normal App — Principal View")
        st.caption("This is the simple day-to-day app view: Students, Tutors, Marks/Results and search. Monitoring stays in the first tab.")

        n1, n2, n3, n4 = st.tabs(["👨‍🎓 Students", "👨‍🏫 Tutors", "📝 Marks & Results", "🔎 Student Search"])

        with n1:
            st.subheader("👨‍🎓 Student Registration Records")
            if students:
                df = pd.DataFrame([{
                    "University ID": r.get("university_id", ""),
                    "Student Name": r.get("student_name", ""),
                    "Department": r.get("department", ""),
                    "Semester": r.get("semester", ""),
                    "Studied College": r.get("studied_college", ""),
                    "Registered By": r.get("registered_by", ""),
                    "Registered At": r.get("registered_at", "")
                } for r in students])
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.download_button("📥 Download Student Records", df.to_csv(index=False).encode(), "student_records.csv", "text/csv", use_container_width=True)
            else:
                st.info("No students registered yet.")

        with n2:
            st.subheader("👨‍🏫 Tutor Records")
            if tutors:
                df = pd.DataFrame([{
                    "Tutor Name": r.get("tutor_name", ""),
                    "Department": r.get("department", ""),
                    "Semester": r.get("semester", "") or "All",
                    "Credit Score": r.get("credit_score", 0),
                    "Active": r.get("active", True),
                    "Registered At": r.get("registered_at", "")
                } for r in tutors])
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.download_button("📥 Download Tutor Records", df.to_csv(index=False).encode(), "tutor_records.csv", "text/csv", use_container_width=True)
            else:
                st.info("No tutors registered yet.")

        with n3:
            st.subheader("📝 Student Marks / Results")
            if marks:
                rows = []
                for r in marks:
                    rows.append({
                        "Submitted At": r.get("submitted_at", ""),
                        "University ID": r.get("university_id", ""),
                        "Department": r.get("department", ""),
                        "Semester": r.get("semester", ""),
                        "Tutor": r.get("tutor_name", ""),
                        "Subjects / Marks": str(r.get("subjects", ""))
                    })
                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.download_button("📥 Download Marks Records", df.to_csv(index=False).encode(), "marks_records.csv", "text/csv", use_container_width=True)
            else:
                st.info("No marks have been entered yet.")

        with n4:
            st.subheader("🔎 Search Student Profile")
            if students:
                options = {f"{r.get('university_id','')} — {r.get('student_name','')}": r for r in students}
                selected = st.selectbox("Select Student", list(options.keys()), key="principal_normal_student_search")
                student = options[selected]
                c1, c2 = st.columns(2)
                c1.metric("University ID", str(student.get("university_id", "")))
                c2.metric("Department / Semester", f"{student.get('department','')} / {student.get('semester','')}")
                st.write(f"**Name:** {student.get('student_name','')}")
                st.write(f"**Studied College:** {student.get('studied_college','') or '—'}")
                st.write(f"**Registered By:** {student.get('registered_by','') or '—'}")
                st.write(f"**Registered At:** {student.get('registered_at','') or '—'}")

                student_marks = [m for m in marks if str(m.get('university_id','')).strip() == str(student.get('university_id','')).strip()]
                if student_marks:
                    st.subheader("📊 This Student's Mark Records")
                    st.dataframe(pd.DataFrame(student_marks), use_container_width=True, hide_index=True)
            else:
                st.info("No students available for search.")

    with tab4:
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


    with tab5:
        st.subheader("📁 Department → Semester → Students / Tutors / Analysis")
        st.caption("Folders are generated dynamically from the live Supabase records. Each department and semester gets separate Student, Tutor and Analysis sections.")
        rate_for_folders = float(rate) if "rate" in locals() else 100.0
        folders = build_folder_records(students, tutors, marks, smart, audit, completed, rate_for_folders)
        runtime_root = write_runtime_folders(folders, completed, rate_for_folders)

        if not folders:
            st.info("No department/semester records are available yet.")
        else:
            dept_names = sorted({d for d, _ in folders})
            selected_dept = st.selectbox("📂 Department Folder", dept_names, key="principal_folder_dept")
            sem_names = sorted({s for d, s in folders if d == selected_dept})
            selected_sem = st.selectbox("📁 Semester Folder", sem_names, key="principal_folder_sem")
            g = folders[(selected_dept, selected_sem)]

            st.markdown(f"### 📂 {selected_dept} / 📁 Semester {selected_sem}")
            f1, f2, f3, f4, f5 = st.tabs(["👨‍🎓 Students", "👨‍🏫 Tutors", "📝 Marks", "📊 Analysis", "🪪 Smart Cards"])
            with f1:
                df = folder_dataframe(g["students"])
                st.dataframe(df, use_container_width=True, hide_index=True) if not df.empty else st.info("No students in this folder.")
            with f2:
                df = folder_dataframe(g["tutors"])
                if not df.empty:
                    # Principal sees the tutor's real registered name, not login IDs such as teacher_ce.
                    preferred = [c for c in ["Tutor Name", "Department", "Semester", "Credit Score"] if c in df.columns]
                    if preferred:
                        df = df[preferred]
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("No tutors in this folder.")
            with f3:
                df = folder_dataframe(g["marks"])
                st.dataframe(df, use_container_width=True, hide_index=True) if not df.empty else st.info("No mark records in this folder.")
            with f4:
                st.dataframe(pd.DataFrame([g["analysis"]]), use_container_width=True, hide_index=True)
                st.caption("Analysis is scoped to this department + semester.")
            with f5:
                df = folder_dataframe(g["smart"])
                st.dataframe(df, use_container_width=True, hide_index=True) if not df.empty else st.info("No Smart Cards in this folder.")

            st.divider()
            st.subheader("💰 Tutor Salary Folders")
            salary_records = []
            for r in completed:
                salary_records.append({
                    "Tutor Name": tutor_name_from_event(r, tutors),
                    "Month": month_label(r.get("timestamp")),
                    "Department": r.get("department", ""),
                    "Semester": str(r.get("semester", "")).upper(),
                    "Completed Uploads": 1,
                    "Salary (₹)": rate_for_folders,
                })
            if salary_records:
                sdf = pd.DataFrame(salary_records).groupby(
                    ["Tutor Name", "Month", "Department", "Semester"], as_index=False
                ).agg({"Completed Uploads":"sum", "Salary (₹)":"sum"}).sort_values(
                    ["Tutor Name", "Month"], ascending=[True, False]
                )
                tutor_names = sorted(sdf["Tutor Name"].unique().tolist())
                selected_tutor = st.selectbox("👨‍🏫 Tutor Salary Folder", tutor_names, key="salary_folder_tutor")
                tutor_months = sdf[sdf["Tutor Name"] == selected_tutor]
                st.markdown(f"**📂 Tutor Salary / {selected_tutor}**")
                st.dataframe(tutor_months, use_container_width=True, hide_index=True)
                st.download_button("📥 Download Tutor Monthly Salary Folder Data", tutor_months.to_csv(index=False).encode(), f"{safe_folder_name(selected_tutor)}_monthly_salary.csv", "text/csv")
            else:
                st.info("No completed tutor salary records yet.")

            st.caption(f"Runtime folder tree created at: `{runtime_root}`. Supabase remains the permanent database; Streamlit Cloud runtime folders can reset on redeploy/restart.")


    with tab5:
        st.subheader("📅 Day-by-Day Recorded Files / Tables")
        st.caption("Every day is kept separately as YYYY-MM-DD. The tables below are regenerated from the live Supabase database, so a deleted student is removed from the displayed records.")
        rate_for_daily = float(rate) if "rate" in locals() else 100.0
        daily_root, available_days = write_daily_records(students, tutors, marks, smart, audit, completed, rate_for_daily)
        if not available_days:
            st.info("No dated records available yet.")
        else:
            selected_day = st.selectbox("📅 Select recording day", available_days, key="principal_daily_day")
            day_folder = os.path.join(daily_root, safe_folder_name(selected_day))
            st.markdown(f"### 📅 Records for {selected_day}")
            files_for_day = [
                ("students_records.csv", "👨‍🎓 Students"),
                ("tutors_records.csv", "👨‍🏫 Tutors"),
                ("marks_records.csv", "📝 Marks"),
                ("smart_cards_records.csv", "🪪 Smart Cards"),
                ("tutor_activity.csv", "🔴 Tutor Activity"),
                ("completed_salary_records.csv", "💰 Completed / Salary"),
            ]
            for filename, title in files_for_day:
                path = os.path.join(day_folder, filename)
                st.markdown(f"**{title}** — `{filename}`")
                if os.path.isfile(path):
                    try:
                        ddf = pd.read_csv(path)
                    except Exception:
                        ddf = pd.DataFrame()
                    if ddf.empty:
                        st.info("No records in this table for this day.")
                    else:
                        st.dataframe(ddf, use_container_width=True, hide_index=True)
                        st.download_button(f"📥 Download {filename}", ddf.to_csv(index=False).encode(), filename, "text/csv", key=f"daily_download_{selected_day}_{filename}")
                else:
                    st.info("No records in this table for this day.")

        st.caption(f"Daily files are generated under `{daily_root}` on the current Streamlit runtime. Supabase is the permanent source of truth.")


    with tab7:
        st.subheader("🗑️ Delete Student — One at a Time")
        st.warning("⚠️ Permanent deletion: this removes the selected student's registration, marks/results, Smart Card, uploaded student files, old tutor activity, daily Principal records and related Supabase records. A new deletion audit entry is kept.")
        if not students:
            st.info("No registered students are available to delete.")
        else:
            student_options = {
                f"{r.get('university_id','')} — {r.get('student_name','')} — {r.get('department','')} / {r.get('semester','')}": r
                for r in students
            }
            selected_label = st.selectbox("Select ONE student to delete", list(student_options.keys()), key="principal_delete_student_select")
            selected_student = student_options[selected_label]
            st.markdown("### Selected student")
            preview = pd.DataFrame([{
                "University ID": selected_student.get("university_id", ""),
                "Student Name": selected_student.get("student_name", ""),
                "Department": selected_student.get("department", ""),
                "Semester": selected_student.get("semester", ""),
                "Studied College": selected_student.get("studied_college", "") or "",
                "Registered By": selected_student.get("registered_by", "") or "",
            }])
            st.dataframe(preview, use_container_width=True, hide_index=True)
            confirm = st.checkbox("I understand this permanently deletes ALL details for this selected student.", key="principal_delete_student_confirm")
            if st.button("🗑️ DELETE SELECTED STUDENT", type="primary", use_container_width=True, disabled=not confirm):
                try:
                    uid, removed_files = delete_student_everywhere(sb, selected_student, audit_user=PRINCIPAL_USERNAME)
                    st.success(f"✅ Student {uid} deleted successfully. Local files removed: {removed_files}.")
                    st.session_state.pop("principal_delete_student_select", None)
                    st.session_state.pop("principal_delete_student_confirm", None)
                    st.rerun()
                except Exception as exc:
                    st.error(f"❌ Delete failed: {exc}")



if "principal_auth" not in st.session_state:
    st.session_state.principal_auth = False

if not st.session_state.principal_auth:
    login()
else:
    dashboard()

