import json
from datetime import datetime
import pandas as pd
import streamlit as st

from db import (
    test_connection,
    get_students,
    get_tutors,
    get_marks,
    get_smart_cards,
    get_audit_logs,
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
SEMESTERS = [f"S{i}" for i in range(1, 9)]

if "auth" not in st.session_state:
    st.session_state.auth = False


def login():
    st.title("🛡️ EduPredict SPP — Principal Portal")
    st.caption("Live tutor monitoring • Student performance analysis • Smart Card monitoring")
    with st.form("principal_login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        ok = st.form_submit_button("🔐 Secure Login", type="primary", use_container_width=True)
    if ok:
        if u.strip() == PRINCIPAL_USERNAME and p == PRINCIPAL_PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Invalid username or password.")


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


def student_credit(subjects):
    vals = []
    for x in subjects:
        try:
            v = x.get("Tutor_Credit_10")
            if v is not None:
                vals.append(float(v))
        except Exception:
            pass
    if vals:
        return round(sum(vals) / len(vals), 2)
    # Fallback for older records created before Tutor_Credit_10 existed.
    vals = []
    for x in subjects:
        try:
            att = float(x.get("Attendance_Mark", 0)) / 5 * 100
            internal = float(x.get("Internal", 0)) / 40 * 100
            assignment = float(x.get("Assignment", 0)) / 15 * 100
            previous = float(x.get("Previous", 0)) / 60 * 100
            vals.append((att + internal + assignment + previous) / 4 / 10)
        except Exception:
            continue
    return round(sum(vals) / len(vals), 2) if vals else 0.0


def frame_students(rows):
    return pd.DataFrame([
        {
            "University ID": r.get("university_id", ""),
            "Student Name": r.get("student_name", ""),
            "Department": r.get("department", ""),
            "Semester": r.get("semester", ""),
            "Studied College": r.get("studied_college", ""),
            "Registered By": r.get("registered_by", ""),
            "Active": r.get("active", True),
            "Registered At": r.get("registered_at", ""),
        } for r in rows
    ])


def frame_smart_cards(rows):
    return pd.DataFrame([
        {
            "Registration ID": r.get("registration_id", ""),
            "Name": r.get("name", ""),
            "University ID": r.get("university_id", ""),
            "DOB": r.get("dob", ""),
            "Blood Group": r.get("blood_group", ""),
            "Address": r.get("address", ""),
            "PIN Code": r.get("pin_code", ""),
            "Studied College": r.get("studied_college", ""),
            "Department": r.get("department", ""),
            "Semester": r.get("semester", ""),
            "CGPA": r.get("cgpa", ""),
            "University": r.get("university_name", ""),
            "Submitted": r.get("submitted_at", ""),
        } for r in rows
    ])


def build_tutor_activity(tutors, marks, audit):
    # A completed tutor work item is represented by the explicit audit action
    # generated when the tutor checks "Completed" during mark submission.
    completed = [r for r in audit if r.get("role") == "Tutor" and r.get("action") == "Tutor Work Completed"]
    pending = [r for r in audit if r.get("role") == "Tutor" and r.get("action") == "Tutor Work Saved - Pending Completion"]

    marks_by_tutor = {}
    credit_by_tutor = {}
    for row in marks:
        subjects = parse_subjects(row.get("subjects", []))
        tutor = str(row.get("tutor_name", "")).strip() or "Unknown"
        marks_by_tutor[tutor] = marks_by_tutor.get(tutor, 0) + 1
        credit_by_tutor.setdefault(tutor, []).append(student_credit(subjects))

    rows = []
    tutor_names = {str(r.get("tutor_name", "")).strip() for r in tutors if r.get("tutor_name")}
    tutor_names.update(marks_by_tutor.keys())
    tutor_names.update(str(r.get("username", "")).strip() for r in completed if r.get("username"))
    tutor_names.update(str(r.get("username", "")).strip() for r in pending if r.get("username"))

    for name in sorted(n for n in tutor_names if n):
        done = [r for r in completed if str(r.get("username", "")).strip() == name]
        pend = [r for r in pending if str(r.get("username", "")).strip() == name]
        credits = credit_by_tutor.get(name, [])
        profile = next((r for r in tutors if str(r.get("tutor_name", "")).strip() == name), {})
        rows.append({
            "Tutor Name": name,
            "Department": profile.get("department", done[-1].get("department", "") if done else ""),
            "Tutor Credit /10": round(float(profile.get("credit_score", 0) or 0), 2),
            "Mark Submissions": marks_by_tutor.get(name, 0),
            "Completed Work": len(done),
            "Pending Work": len(pend),
            "Students Completed": len({str(r.get("university_id", "")) for r in done if r.get("university_id")}),
            "Avg Student Credit /10": round(sum(credits) / len(credits), 2) if credits else 0.0,
            "Last Activity": max([str(r.get("timestamp", "")) for r in done + pend] or ["—"]),
        })
    return pd.DataFrame(rows)


def dashboard():
    st.title("🛡️ Principal Academic Monitoring")
    st.caption(f"Shared Supabase database • {datetime.now().strftime('%d %b %Y, %I:%M:%S %p')}")

    c1, c2 = st.columns([1, 5])
    if c1.button("🚪 Logout"):
        st.session_state.auth = False
        st.rerun()
    if c2.button("🔄 Refresh Live Data", type="primary"):
        st.rerun()

    ok, msg = test_connection()
    if not ok:
        st.error(msg)
        st.info("Use the same SUPABASE_URL and SUPABASE_KEY in both Streamlit apps.")
        return

    try:
        students = get_students()
        tutors = get_tutors()
        marks = get_marks()
        smart = get_smart_cards()
        audit = get_audit_logs()
    except Exception as exc:
        st.error(f"Could not load live data: {exc}")
        return

    completed = [r for r in audit if r.get("role") == "Tutor" and r.get("action") == "Tutor Work Completed"]
    tutor_actions = [r for r in audit if r.get("role") == "Tutor"]

    a, b, c, d, e = st.columns(5)
    a.metric("👨‍🎓 Students", len(students))
    b.metric("👨‍🏫 Tutors", len(tutors))
    c.metric("📝 Mark Records", len(marks))
    d.metric("✅ Completed Tutor Work", len(completed))
    e.metric("🪪 Smart Cards", len(smart))

    st.success("🟢 LIVE: Tutor actions, student marks and Smart Card records are read from the shared Supabase database.")

    tab1, tab2, tab3, tab4 = st.tabs([
        "👨‍🏫 Live Tutor Activity", "💰 Tutor Salary Analysis", "🪪 Smart Cards", "🏫 Students"
    ])

    with tab1:
        st.subheader("🔴 Live Tutor Action Monitor")
        st.caption("Only tutor actions are shown here. Refresh the page to fetch the newest events.")
        if not tutor_actions:
            st.info("No tutor activity yet.")
        else:
            activity = pd.DataFrame([
                {
                    "Time": r.get("timestamp", ""),
                    "Tutor Name": r.get("username", ""),
                    "Action": r.get("action", ""),
                    "University ID": r.get("university_id", ""),
                    "Department": r.get("department", ""),
                    "Semester": r.get("semester", ""),
                    "Details": r.get("details", ""),
                } for r in tutor_actions
            ])
            st.dataframe(activity, use_container_width=True, hide_index=True)
            st.download_button("📥 Download Tutor Activity CSV", activity.to_csv(index=False).encode(), "tutor_activity.csv", "text/csv")

        st.subheader("📊 Tutor Work Summary")
        summary = build_tutor_activity(tutors, marks, audit)
        if summary.empty:
            st.info("No tutor work to analyse yet.")
        else:
            st.dataframe(summary, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("💰 Tutor Salary Calculation")
        st.info("Salary is calculated from work explicitly marked **Completed** by the tutor. Set the project salary rate below according to your college/project rule.")
        rate = st.number_input("Salary per completed student work (₹)", min_value=0.0, value=100.0, step=10.0, key="salary_rate")
        summary = build_tutor_activity(tutors, marks, audit)
        if summary.empty:
            st.info("No tutor work available for salary calculation.")
        else:
            summary["Salary (₹)"] = summary["Completed Work"] * rate
            st.dataframe(summary[["Tutor Name", "Department", "Completed Work", "Pending Work", "Avg Student Credit /10", "Salary (₹)"]], use_container_width=True, hide_index=True)
            st.metric("Total Tutor Salary", f"₹{summary['Salary (₹)'].sum():,.2f}")
            st.caption("This is a project calculation, not an institutional payroll record. Change the rate to match your project's chosen rule.")

    with tab3:
        st.subheader("🪪 Smart Card Monitoring")
        if not smart:
            st.info("No Smart Cards registered yet.")
        else:
            sdf = frame_smart_cards(smart)
            st.dataframe(sdf, use_container_width=True, hide_index=True)
            st.download_button("📥 Download Smart Card Details CSV", sdf.to_csv(index=False).encode(), "smart_card_registrations.csv", "text/csv", use_container_width=True)
            st.success(f"Principal can monitor {len(smart)} Smart Card registration(s) from the shared database.")

    with tab4:
        st.subheader("🏫 Registered Students")
        if not students:
            st.info("No students registered yet.")
        else:
            dept = st.selectbox("Department", ["All"] + DEPARTMENTS, key="principal_dept")
            sem = st.selectbox("Semester", ["All"] + SEMESTERS, key="principal_sem")
            filtered = students
            if dept != "All":
                filtered = [r for r in filtered if r.get("department") == dept]
            if sem != "All":
                filtered = [r for r in filtered if str(r.get("semester", "")).upper() == sem]
            sdf = frame_students(filtered)
            st.dataframe(sdf, use_container_width=True, hide_index=True)


if not st.session_state.auth:
    login()
else:
    dashboard()
