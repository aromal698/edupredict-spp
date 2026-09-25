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


def extract_completed(audit):
    return [r for r in audit if str(r.get("role", "")).strip().lower() == "tutor"
            and str(r.get("action", "")).strip() == "Tutor Work Completed"]


def extract_pending(audit):
    return [r for r in audit if str(r.get("role", "")).strip().lower() == "tutor"
            and str(r.get("action", "")).strip() == "Tutor Work Saved - Pending Completion"]


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

    mark_count = {}
    mark_credits = {}
    for m in marks:
        tutor = str(m.get("tutor_name", "")).strip() or "Unknown"
        mark_count[tutor] = mark_count.get(tutor, 0) + 1
        credit = credit_from_subjects(parse_subjects(m.get("subjects", [])))
        mark_credits.setdefault(tutor, []).append(credit)

    names = set()
    for t in tutors:
        name = str(t.get("tutor_name", "")).strip()
        if name:
            names.add(name)
    names.update(str(r.get("username", "")).strip() for r in audit if r.get("username"))
    names.update(mark_count.keys())

    out = []
    for name in sorted(n for n in names if n):
        done = [r for r in completed if str(r.get("username", "")).strip() == name]
        pend = [r for r in pending if str(r.get("username", "")).strip() == name]
        profile = next((t for t in tutors if str(t.get("tutor_name", "")).strip() == name), {})
        credits = mark_credits.get(name, [])
        departments = [str(r.get("department", "")).strip() for r in done + pend if r.get("department")]
        department = str(profile.get("department", "")).strip() or (departments[-1] if departments else "")
        out.append({
            "Tutor Name": name,
            "Department": department,
            "Tutor Credit /10": round(float(profile.get("credit_score", 0) or 0), 2),
            "Mark Submissions": mark_count.get(name, 0),
            "Completed Work": len(done),
            "Pending Work": len(pend),
            "Students Completed": len({str(r.get("university_id", "")) for r in done if r.get("university_id")}),
            "Avg Student Credit /10": round(sum(credits) / len(credits), 2) if credits else 0.0,
            "Last Activity": max([str(r.get("timestamp", "")) for r in done + pend] or ["—"]),
        })
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
    st.title("🛡️ Principal Academic Monitoring")
    st.caption("Shared Supabase database • " + datetime.now().strftime("%d %b %Y, %I:%M:%S %p"))

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

    tab1, tab2, tab3, tab4 = st.tabs([
        "👨‍🏫 Live Tutor Activity", "💰 Tutor Salary Analysis", "🪪 Smart Cards", "🏫 Students"
    ])

    with tab1:
        st.subheader("🔴 Live Tutor Activity")
        if tutor_actions:
            activity = pd.DataFrame([{
                "Time": r.get("timestamp", ""),
                "Tutor Name": r.get("username", ""),
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
            salary["Salary (₹)"] = salary["Completed Work"] * float(rate)
            salary = salary[["Tutor Name", "Department", "Completed Work", "Pending Work", "Students Completed", "Avg Student Credit /10", "Salary (₹)"]]
            st.dataframe(salary, use_container_width=True, hide_index=True)
            total = float(salary["Salary (₹)"].sum())
            x,y,z = st.columns(3)
            x.metric("✅ Completed Work", int(salary["Completed Work"].sum()))
            y.metric("⏳ Pending Work", int(salary["Pending Work"].sum()))
            z.metric("💰 Total Tutor Salary", f"₹{total:,.2f}")
            st.caption("Salary is a project calculation: Completed Work × Salary per completed student work.")

        st.subheader("✅ Completed Work Details")
        if completed:
            details = pd.DataFrame([{
                "Completed At": r.get("timestamp", ""),
                "Tutor": r.get("username", ""),
                "Student": r.get("university_id", ""),
                "Department": r.get("department", ""),
                "Semester": r.get("semester", ""),
                "Details": r.get("details", ""),
            } for r in completed])
            st.dataframe(details, use_container_width=True, hide_index=True)
        else:
            st.info("No Tutor work has been marked Completed yet.")

    with tab3:
        st.subheader("🪪 Smart Card Monitoring")
        if smart:
            sdf = pd.DataFrame([{
                "Registration ID": r.get("registration_id", ""), "Name": r.get("name", ""),
                "University ID": r.get("university_id", ""), "DOB": r.get("dob", ""),
                "Blood Group": r.get("blood_group", ""), "Address": r.get("address", ""),
                "PIN Code": r.get("pin_code", ""), "Studied College": r.get("studied_college", ""),
                "Department": r.get("department", ""), "Semester": r.get("semester", ""),
                "CGPA": r.get("cgpa", ""), "University": r.get("university_name", ""),
                "Submitted": r.get("submitted_at", ""),
            } for r in smart])
            st.dataframe(sdf, use_container_width=True, hide_index=True)
        else:
            st.info("No Smart Cards registered yet.")

    with tab4:
        st.subheader("🏫 Student Monitoring")
        if students:
            sdf = pd.DataFrame([{
                "University ID": r.get("university_id", ""), "Student Name": r.get("student_name", ""),
                "Department": r.get("department", ""), "Semester": r.get("semester", ""),
                "Studied College": r.get("studied_college", ""), "Registered By": r.get("registered_by", ""),
                "Active": r.get("active", True), "Registered At": r.get("registered_at", ""),
            } for r in students])
            st.dataframe(sdf, use_container_width=True, hide_index=True)
        else:
            st.info("No students registered yet.")


if "principal_auth" not in st.session_state:
    st.session_state.principal_auth = False

if not st.session_state.principal_auth:
    login()
else:
    dashboard()
