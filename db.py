import json
import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def _data(result):
    return result.data or []

def register_student(data):
    row = {
        "university_id": str(data.get("university_id", "")).strip(),
        "student_name": str(data.get("student_name", "")).strip(),
        "department": str(data.get("department", "")).strip(),
        "semester": str(data.get("semester", "")).strip().upper(),
        "studied_college": str(data.get("studied_college", "")).strip(),
        "registered_by": str(data.get("registered_by", "")).strip(),
        "active": bool(data.get("active", True)),
    }
    return get_supabase().table("students").upsert(row, on_conflict="university_id").execute()

def get_students():
    return _data(get_supabase().table("students").select("*").order("registered_at", desc=True).execute())

def get_student(university_id):
    rows = _data(get_supabase().table("students").select("*").eq("university_id", str(university_id).strip()).limit(1).execute())
    return rows[0] if rows else None

def delete_student(university_id):
    return get_supabase().table("students").update({"active": False}).eq("university_id", str(university_id).strip()).execute()

def register_tutor(data):
    row = {
        "tutor_id": str(data.get("tutor_id", "")).strip(),
        "tutor_name": str(data.get("tutor_name", "")).strip(),
        "department": str(data.get("department", "")).strip(),
        "semester": str(data.get("semester", "")).strip().upper(),
        "credit_score": float(data.get("credit_score", 0) or 0),
        "active": bool(data.get("active", True)),
    }
    return get_supabase().table("tutors").upsert(row, on_conflict="tutor_id").execute()

def get_tutors():
    return _data(get_supabase().table("tutors").select("*").order("registered_at", desc=True).execute())

def save_student_marks(data):
    row = {
        "university_id": str(data["university_id"]).strip(),
        "department": str(data.get("department", "")).strip(),
        "semester": str(data.get("semester", "")).strip().upper(),
        "tutor_name": str(data.get("tutor_name", "")).strip(),
        "subjects": data.get("subjects", []),
    }
    return get_supabase().table("student_marks").insert(row).execute()

def get_student_marks(university_id):
    return _data(get_supabase().table("student_marks").select("*").eq("university_id", str(university_id).strip()).order("submitted_at", desc=True).execute())

def get_all_marks():
    return _data(get_supabase().table("student_marks").select("*").order("submitted_at", desc=True).execute())

def delete_mark_record(university_id, submitted_at):
    return get_supabase().table("student_marks").delete().eq("university_id", str(university_id).strip()).eq("submitted_at", submitted_at).execute()

def save_smart_card(data):
    row = {
        "registration_id": str(data.get("Registration_ID", "")).strip(),
        "university_id": str(data.get("University_ID", "")).strip() or None,
        "name": str(data.get("Student_Name", "")).strip(),
        "dob": data.get("DOB") or None,
        "blood_group": str(data.get("Blood_Group", "")),
        "address": str(data.get("Address", "")),
        "pin_code": str(data.get("PIN_Code", "")),
        "studied_college": str(data.get("Studied_College", "")),
        "department": str(data.get("Department", "")),
        "semester": str(data.get("Semester", "")),
        "cgpa": float(data["CGPA"]) if str(data.get("CGPA", "")).strip() else None,
        "university_name": str(data.get("University_Name", "")),
    }
    return get_supabase().table("smart_cards").upsert(row, on_conflict="registration_id").execute()

def get_smart_cards():
    return _data(get_supabase().table("smart_cards").select("*").order("submitted_at", desc=True).execute())

def save_student_file(data):
    return get_supabase().table("student_files").insert(data).execute()

def get_student_files(university_id):
    return _data(get_supabase().table("student_files").select("*").eq("university_id", str(university_id).strip()).order("uploaded_at", desc=True).execute())

def add_audit_log(username, role, action, university_id="", department="", semester="", details=""):
    row = {"username": str(username or ""), "role": str(role or ""), "action": str(action or ""), "university_id": str(university_id or ""), "department": str(department or ""), "semester": str(semester or ""), "details": str(details or "")}
    return get_supabase().table("audit_logs").insert(row).execute()

def get_audit_logs():
    return _data(get_supabase().table("audit_logs").select("*").order("timestamp", desc=True).execute())
