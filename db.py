"""Shared Supabase database helpers for EduPredict SPP.

Both Streamlit apps import this module. Credentials are read only from
Streamlit Secrets; nothing is hard-coded here.
"""
import json
from functools import lru_cache
import streamlit as st
from supabase import create_client


def _secrets_ready():
    return bool(st.secrets.get("SUPABASE_URL", "").strip()) and bool(st.secrets.get("SUPABASE_KEY", "").strip())


@lru_cache(maxsize=1)
def get_supabase():
    url = st.secrets.get("SUPABASE_URL", "").strip()
    key = st.secrets.get("SUPABASE_KEY", "").strip()
    if not url or not key:
        raise RuntimeError(
            "Supabase is not configured for this Streamlit app. "
            "Open App Settings → Secrets and add SUPABASE_URL and SUPABASE_KEY."
        )
    return create_client(url, key)


def db_status():
    if not _secrets_ready():
        return False, "Missing SUPABASE_URL or SUPABASE_KEY in Streamlit Secrets."
    try:
        get_supabase().table("students").select("university_id").limit(1).execute()
        return True, "Connected"
    except Exception as exc:
        return False, str(exc)


def _data(result):
    return getattr(result, "data", None) or []


# ---------- Students ----------
def register_student(data):
    return get_supabase().table("students").upsert(data, on_conflict="university_id").execute()


def get_students():
    return _data(get_supabase().table("students").select("*").order("registered_at", desc=True).execute())


def get_student(university_id):
    rows = _data(get_supabase().table("students").select("*").eq("university_id", str(university_id).strip()).limit(1).execute())
    return rows[0] if rows else None


def delete_student(university_id):
    return get_supabase().table("students").delete().eq("university_id", str(university_id).strip()).execute()


# ---------- Tutors ----------
def register_tutor(data):
    return get_supabase().table("tutors").upsert(data, on_conflict="tutor_id").execute()


def get_tutors():
    return _data(get_supabase().table("tutors").select("*").order("registered_at", desc=True).execute())


# ---------- Marks ----------
def save_student_marks(data):
    return get_supabase().table("student_marks").insert(data).execute()


def get_student_marks(university_id):
    return _data(get_supabase().table("student_marks").select("*").eq("university_id", str(university_id).strip()).order("submitted_at", desc=True).execute())


def get_all_marks():
    return _data(get_supabase().table("student_marks").select("*").order("submitted_at", desc=True).execute())


def delete_mark_submission(university_id, department, semester, submitted_at=None):
    q = get_supabase().table("student_marks").delete().eq("university_id", str(university_id).strip()).eq("department", str(department).strip()).eq("semester", str(semester).strip())
    if submitted_at:
        q = q.eq("submitted_at", submitted_at)
    return q.execute()


# ---------- Smart cards ----------
def save_smart_card(data):
    return get_supabase().table("smart_cards").upsert(data, on_conflict="registration_id").execute()


def get_smart_cards():
    return _data(get_supabase().table("smart_cards").select("*").order("submitted_at", desc=True).execute())


def get_smart_card(university_id):
    rows = _data(get_supabase().table("smart_cards").select("*").eq("university_id", str(university_id).strip()).limit(1).execute())
    return rows[0] if rows else None


# ---------- Files ----------
def save_student_file(data):
    return get_supabase().table("student_files").insert(data).execute()


def get_student_files(university_id):
    return _data(get_supabase().table("student_files").select("*").eq("university_id", str(university_id).strip()).order("uploaded_at", desc=True).execute())


# ---------- Audit ----------
def add_audit_log(username, role, action, university_id="", department="", semester="", details=""):
    return get_supabase().table("audit_logs").insert({
        "username": str(username or ""),
        "role": str(role or ""),
        "action": str(action or ""),
        "university_id": str(university_id or ""),
        "department": str(department or ""),
        "semester": str(semester or ""),
        "details": str(details or ""),
    }).execute()


def get_audit_logs():
    return _data(get_supabase().table("audit_logs").select("*").order("timestamp", desc=True).execute())
