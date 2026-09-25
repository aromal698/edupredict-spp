import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def get_supabase() -> Client:
    """
    Create one shared Supabase connection for the Streamlit app.
    Credentials are read from Streamlit Secrets.
    """
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]

    return create_client(url, key)


# ---------------------------------------------------------
# STUDENTS
# ---------------------------------------------------------

def register_student(data):
    db = get_supabase()

    return db.table("students").upsert(
        data,
        on_conflict="university_id"
    ).execute()


def get_students():
    db = get_supabase()

    return db.table("students") \
        .select("*") \
        .order("registered_at", desc=True) \
        .execute().data


def get_student(university_id):
    db = get_supabase()

    result = db.table("students") \
        .select("*") \
        .eq("university_id", university_id) \
        .limit(1) \
        .execute()

    return result.data[0] if result.data else None


def delete_student(university_id):
    db = get_supabase()

    return db.table("students") \
        .delete() \
        .eq("university_id", university_id) \
        .execute()


# ---------------------------------------------------------
# TUTORS
# ---------------------------------------------------------

def register_tutor(data):
    db = get_supabase()

    return db.table("tutors").upsert(
        data,
        on_conflict="tutor_id"
    ).execute()


def get_tutors():
    db = get_supabase()

    return db.table("tutors") \
        .select("*") \
        .order("registered_at", desc=True) \
        .execute().data


# ---------------------------------------------------------
# MARKS
# ---------------------------------------------------------

def save_student_marks(data):
    db = get_supabase()

    return db.table("student_marks") \
        .insert(data) \
        .execute()


def get_student_marks(university_id):
    db = get_supabase()

    return db.table("student_marks") \
        .select("*") \
        .eq("university_id", university_id) \
        .order("submitted_at", desc=True) \
        .execute().data


def get_all_marks():
    db = get_supabase()

    return db.table("student_marks") \
        .select("*") \
        .order("submitted_at", desc=True) \
        .execute().data


# ---------------------------------------------------------
# SMART CARDS
# ---------------------------------------------------------

def save_smart_card(data):
    db = get_supabase()

    return db.table("smart_cards").upsert(
        data,
        on_conflict="registration_id"
    ).execute()


def get_smart_cards():
    db = get_supabase()

    return db.table("smart_cards") \
        .select("*") \
        .order("submitted_at", desc=True) \
        .execute().data


def get_smart_card(university_id):
    db = get_supabase()

    result = db.table("smart_cards") \
        .select("*") \
        .eq("university_id", university_id) \
        .limit(1) \
        .execute()

    return result.data[0] if result.data else None


# ---------------------------------------------------------
# STUDENT FILES
# ---------------------------------------------------------

def save_student_file(data):
    db = get_supabase()

    return db.table("student_files") \
        .insert(data) \
        .execute()


def get_student_files(university_id):
    db = get_supabase()

    return db.table("student_files") \
        .select("*") \
        .eq("university_id", university_id) \
        .order("uploaded_at", desc=True) \
        .execute().data


# ---------------------------------------------------------
# AUDIT LOG
# ---------------------------------------------------------

def add_audit_log(
    username,
    role,
    action,
    university_id="",
    department="",
    semester="",
    details=""
):
    db = get_supabase()

    data = {
        "username": username,
        "role": role,
        "action": action,
        "university_id": university_id,
        "department": department,
        "semester": semester,
        "details": details,
    }

    return db.table("audit_logs").insert(data).execute()


def get_audit_logs():
    db = get_supabase()

    return db.table("audit_logs") \
        .select("*") \
        .order("timestamp", desc=True) \
        .execute().data
