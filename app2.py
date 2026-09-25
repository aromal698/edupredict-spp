import streamlit as st
import pandas as pd
import numpy as np
import os
import io
import json
from datetime import datetime

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether
)
from reportlab.graphics.shapes import Drawing, Circle


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Student Performance Prediction",
    page_icon="🎓",
    layout="wide"
)


# ============================================================
# FILES
# ============================================================

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

REPORT_FILE = os.path.join(
    DATA_DIR,
    "student_reports.csv"
)


# ============================================================
# B.TECH BRANCH OPTIONS
# ============================================================

BRANCHES = [
    "Artificial Intelligence and Data Science",
    "Artificial Intelligence and Machine Learning",
    "Computer Science and Engineering",
    "Computer Science and Engineering (AI)",
    "Computer Science and Engineering (Data Science)",
    "Computer Science and Engineering (Cyber Security)",
    "Information Technology",
    "Cyber Security",
    "Data Science",
    "Computer Engineering",
    "Software Engineering",
    "Electronics and Communication Engineering",
    "Electrical and Electronics Engineering",
    "Electronics and Instrumentation Engineering",
    "Electronics Engineering",
    "Instrumentation Engineering",
    "Biomedical Engineering",
    "Mechanical Engineering",
    "Automobile Engineering",
    "Aeronautical Engineering",
    "Civil Engineering",
    "Chemical Engineering",
    "Food Technology",
    "Biotechnology",
    "Industrial Engineering",
    "Production Engineering",
    "Mechatronics Engineering",
    "Robotics and Automation",
    "Environmental Engineering",
    "Marine Engineering",
    "Metallurgical Engineering",
    "Mining Engineering",
    "Textile Engineering",
    "Agricultural Engineering"
]


# ============================================================
# SUBJECT OPTIONS
# ============================================================

SUBJECTS = {

    "S1": [
        "Mathematics I",
        "Physics",
        "Chemistry",
        "Engineering Graphics",
        "Programming in C",
        "Engineering Mechanics",
        "Basic Electrical Engineering",
        "Basic Civil Engineering",
        "Life Skills",
        "Workshop Practice",
        "Design and Engineering",
        "Engineering Drawing"
    ],

    "S2": [
        "Mathematics II",
        "Engineering Physics",
        "Engineering Chemistry",
        "Python Programming",
        "Engineering Mechanics",
        "Basic Electronics",
        "Professional Communication",
        "Environmental Science",
        "Electrical Engineering",
        "Design and Engineering",
        "Programming Lab",
        "Constitution of India"
    ],

    "S3": [
        "Mathematics III",
        "Data Structures",
        "Database Management Systems",
        "Artificial Intelligence",
        "Machine Learning",
        "Computer Organization",
        "Object Oriented Programming",
        "Digital Electronics",
        "Probability and Statistics",
        "Operating Systems",
        "Data Structures Lab",
        "Microprocessors"
    ],

    "S4": [
        "Mathematics IV",
        "Operating Systems",
        "Computer Networks",
        "Design and Analysis of Algorithms",
        "Artificial Intelligence",
        "Machine Learning",
        "Software Engineering",
        "Microprocessors",
        "Web Programming",
        "Theory of Computation",
        "Database Lab",
        "Computer Networks Lab"
    ],

    "S5": [
        "Compiler Design",
        "Computer Networks",
        "Distributed Computing",
        "Data Mining",
        "Deep Learning",
        "Cloud Computing",
        "Cyber Security",
        "Software Testing",
        "Computer Graphics",
        "Data Analytics",
        "Elective I",
        "Mini Project"
    ],

    "S6": [
        "Big Data Analytics",
        "Natural Language Processing",
        "Computer Vision",
        "Internet of Things",
        "Cloud Computing",
        "Information Security",
        "Data Science",
        "Mobile Computing",
        "Data Mining Lab",
        "Elective II",
        "Project Phase I",
        "Seminar"
    ],

    "S7": [
        "Advanced Machine Learning",
        "Deep Learning",
        "Blockchain",
        "Artificial Intelligence Applications",
        "Data Analytics",
        "Elective III",
        "Elective IV",
        "Seminar",
        "Project Phase II",
        "Professional Elective",
        "Major Project",
        "Industrial Training"
    ],

    "S8": [
        "Project",
        "Project Viva",
        "Comprehensive Viva",
        "Elective V",
        "Elective VI",
        "Industrial Training",
        "Advanced Artificial Intelligence",
        "Advanced Data Science",
        "Professional Elective",
        "Open Elective",
        "Technical Seminar",
        "Major Project Viva"
    ]
}


# ============================================================
# TEACHER ACCOUNTS
# ============================================================
# Demo passwords. Change these for actual deployment.
# ============================================================

TEACHERS = {

    "teacher_aids": {
        "password": "ktutech",
        "semester": "ALL",
        "branch": "Artificial Intelligence and Data Science"
    },

    "teacher_aiml": {
        "password": "ktutech",
        "semester": "ALL",
        "branch": "Artificial Intelligence and Machine Learning"
    },

    "teacher_cse": {
        "password": "ktutech",
        "semester": "ALL",
        "branch": "Computer Science and Engineering"
    },

    "teacher_cseai": {
        "password": "ktutech",
        "semester": "ALL",
        "branch": "Computer Science and Engineering (AI)"
    },

    "teacher_ds": {
        "password": "ktutech",
        "semester": "ALL",
        "branch": "Computer Science and Engineering (Data Science)"
    },

    "teacher_cyber": {
        "password": "ktutech",
        "semester": "ALL",
        "branch": "Cyber Security"
    },

    "teacher_it": {
        "password": "ktutech",
        "semester": "ALL",
        "branch": "Information Technology"
    },

    "teacher_ece": {
        "password": "ktutech",
        "semester": "ALL",
        "branch": "Electronics and Communication Engineering"
    },

    "teacher_eee": {
        "password": "ktutech",
        "semester": "ALL",
        "branch": "Electrical and Electronics Engineering"
    },

    "teacher_eie": {
        "password": "ktutech",
        "semester": "ALL",
        "branch": "Electronics and Instrumentation Engineering"
    },

    "teacher_me": {
        "password": "ktutech",
        "semester": "ALL",
        "branch": "Mechanical Engineering"
    },

    "teacher_ce": {
        "password": "ktutech",
        "semester": "ALL",
        "branch": "Civil Engineering"
    },

    "teacher_auto": {
        "password": "ktutech",
        "semester": "ALL",
        "branch": "Automobile Engineering"
    },

    "teacher_aero": {
        "password": "ktutech",
        "semester": "ALL",
        "branch": "Aeronautical Engineering"
    },

    "teacher_bio": {
        "password": "ktutech",
        "semester": "ALL",
        "branch": "Biotechnology"
    },

    "teacher_biomed": {
        "password": "ktutech",
        "semester": "ALL",
        "branch": "Biomedical Engineering"
    },

    "teacher_robotics": {
        "password": "ktutech",
        "semester": "ALL",
        "branch": "Robotics and Automation"
    },

    "teacher_mechatronics": {
        "password": "ktutech",
        "semester": "ALL",
        "branch": "Mechatronics Engineering"
    },

    "teacher_chemical": {
        "password": "ktutech",
        "semester": "ALL",
        "branch": "Chemical Engineering"
    },

    "teacher_food": {
        "password": "ktutech",
        "semester": "ALL",
        "branch": "Food Technology"
    }
}


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None

if "username" not in st.session_state:
    st.session_state.username = None

if "teacher_branch" not in st.session_state:
    st.session_state.teacher_branch = None

if "teacher_semester" not in st.session_state:
    st.session_state.teacher_semester = "ALL"

if "student_id" not in st.session_state:
    st.session_state.student_id = None

if "student_calculated" not in st.session_state:
    st.session_state.student_calculated = False


# ============================================================
# PERFORMANCE COLOURS
# ============================================================

PERFORMANCE_COLORS = {
    "Low Performance": "#F4CCCC",
    "Average Performance": "#FCE5CD",
    "Above Average": "#FFF2CC",
    "Good Performance": "#D9EAD3"
}

PERFORMANCE_TEXT_COLORS = {
    "Low Performance": "#CC0000",
    "Average Performance": "#E69138",
    "Above Average": "#C9A227",
    "Good Performance": "#38761D"
}


# ============================================================
# COLOURED CIRCLE FOR PDF
# ============================================================

def performance_circle(level):

    hex_colour = PERFORMANCE_TEXT_COLORS.get(
        level,
        "#777777"
    )

    drawing = Drawing(
        16,
        16
    )

    drawing.add(
        Circle(
            8,
            8,
            5,
            fillColor=colors.HexColor(hex_colour),
            strokeColor=colors.HexColor(hex_colour)
        )
    )

    return drawing


# ============================================================
# ATTENDANCE CONVERSION
# ============================================================

def attendance_mark(attendance):

    if attendance >= 90:
        return 5

    elif attendance >= 80:
        return 4

    elif attendance >= 70:
        return 3

    elif attendance >= 60:
        return 2

    elif attendance >= 10:
        return 1

    else:
        return 0


def attendance_range(attendance):

    if attendance >= 90:
        return "90–100% → 5 marks"

    elif attendance >= 80:
        return "80–89% → 4 marks"

    elif attendance >= 70:
        return "70–79% → 3 marks"

    elif attendance >= 60:
        return "60–69% → 2 marks"

    elif attendance >= 10:
        return "10–59% → 1 mark"

    else:
        return "Below 10% → 0 marks"


# ============================================================
# PERFORMANCE CALCULATION
# ============================================================

def calculate_performance(
    attendance,
    study_hours,
    internal,
    assignment,
    previous
):

    # Attendance converted to 5 marks
    attendance_score = (
        attendance_mark(attendance) / 5
    ) * 100

    # Study hours maximum 6
    study_score = min(
        (study_hours / 6) * 100,
        100
    )

    # Internal /40
    internal_score = (
        internal / 40
    ) * 100

    # Assignment /15
    assignment_score = (
        assignment / 15
    ) * 100

    # Previous /60
    previous_score = (
        previous / 60
    ) * 100

    overall = np.mean([
        attendance_score,
        study_score,
        internal_score,
        assignment_score,
        previous_score
    ])

    # Project-defined performance categories
    if overall < 50:

        level = "Low Performance"

    elif overall < 65:

        level = "Average Performance"

    elif overall < 80:

        level = "Above Average"

    else:

        level = "Good Performance"

    return (
        level,
        overall
    )


# ============================================================
# RECOMMENDATIONS / COMPLEMENT
# ============================================================

def get_feedback(
    attendance,
    study_hours,
    internal,
    assignment,
    previous,
    level
):

    methods = []

    # Low performance
    if level == "Low Performance":

        if attendance < 75:
            methods.append(
                "Improve attendance by attending classes regularly."
            )

        if study_hours < 2:
            methods.append(
                "Increase daily study time gradually."
            )

        if internal < 20:
            methods.append(
                "Prepare more consistently for internal examinations."
            )

        if assignment < 8:
            methods.append(
                "Complete assignments on time."
            )

        if previous < 30:
            methods.append(
                "Revise previous topics and strengthen fundamentals."
            )

        if not methods:
            methods.append(
                "Follow a regular study timetable and revise weak topics."
            )

    # Average
    elif level == "Average Performance":

        methods.append(
            "Maintain regular revision and improve consistency."
        )

        if attendance < 80:
            methods.append(
                "Try to improve attendance."
            )

        if internal < 25:
            methods.append(
                "Give additional attention to internal examinations."
            )

    # Above average
    elif level == "Above Average":

        methods.append(
            "Good progress. Small improvements in marks and internal assessment can improve the overall result."
        )

        if internal < 32:
            methods.append(
                "Improve internal marks through regular revision."
            )

        if assignment < 12:
            methods.append(
                "Try to improve assignment scores."
            )

    # Good
    else:

        methods.append(
            "Excellent performance! Keep up the good work."
        )

        methods.append(
            "Maintain your current study habits and consistency."
        )

    return methods


# ============================================================
# DATASET
# ============================================================

def load_dataset():

    files = [
        "data/student_performance.csv",
        "student_performance.csv"
    ]

    for file in files:

        if os.path.exists(file):

            try:

                df = pd.read_csv(file)

                required = [
                    "Attendance",
                    "Study_Hours",
                    "Internal_Mark",
                    "Assignment",
                    "Previous_Mark",
                    "Performance"
                ]

                if all(
                    column in df.columns
                    for column in required
                ):

                    return df

            except Exception:
                pass

    return None


# ============================================================
# FALLBACK TRAINING DATA
# ============================================================

def create_training_data():

    rng = np.random.default_rng(42)

    n = 300

    attendance = rng.uniform(
        40,
        100,
        n
    )

    study = rng.uniform(
        0,
        6,
        n
    )

    internal = rng.uniform(
        8,
        40,
        n
    )

    assignment = rng.uniform(
        3,
        15,
        n
    )

    previous = rng.uniform(
        15,
        60,
        n
    )

    score = (

        attendance * 0.25

        + (study / 6 * 100) * 0.15

        + (internal / 40 * 100) * 0.25

        + (assignment / 15 * 100) * 0.15

        + (previous / 60 * 100) * 0.20
    )

    performance = []

    for value in score:

        if value < 50:
            performance.append("Low")

        elif value < 70:
            performance.append("Medium")

        else:
            performance.append("High")

    return pd.DataFrame({
        "Attendance": attendance,
        "Study_Hours": study,
        "Internal_Mark": internal,
        "Assignment": assignment,
        "Previous_Mark": previous,
        "Performance": performance
    })


# ============================================================
# PREPARE MODEL DATA
# ============================================================

def prepare_dataset(df):

    data = df.copy()

    data["Attendance_Model"] = pd.to_numeric(
        data["Attendance"],
        errors="coerce"
    ).fillna(0)

    study = pd.to_numeric(
        data["Study_Hours"],
        errors="coerce"
    ).fillna(0)

    data["Study_Model"] = (
        study / 6
    ) * 100

    internal = pd.to_numeric(
        data["Internal_Mark"],
        errors="coerce"
    ).fillna(0)

    data["Internal_Model"] = (
        internal / 40
    ) * 100

    assignment = pd.to_numeric(
        data["Assignment"],
        errors="coerce"
    ).fillna(0)

    data["Assignment_Model"] = (
        assignment / 15
    ) * 100

    previous = pd.to_numeric(
        data["Previous_Mark"],
        errors="coerce"
    ).fillna(0)

    data["Previous_Model"] = (
        previous / 60
    ) * 100

    return data


# ============================================================
# TRAIN K-MEANS + RANDOM FOREST
# ============================================================

@st.cache_resource
def train_models():

    df = load_dataset()

    if df is None:
        df = create_training_data()

    df = prepare_dataset(df)

    features = [
        "Attendance_Model",
        "Study_Model",
        "Internal_Model",
        "Assignment_Model",
        "Previous_Model"
    ]

    X = df[features].fillna(0)

    y = df["Performance"].astype(str)

    # Scaling
    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)

    # --------------------------------------------------------
    # K-MEANS CLUSTERING
    # --------------------------------------------------------

    kmeans = KMeans(
        n_clusters=3,
        random_state=42,
        n_init=10
    )

    df["Cluster"] = kmeans.fit_predict(
        X_scaled
    )

    # --------------------------------------------------------
    # RANDOM FOREST
    # --------------------------------------------------------

    random_forest = RandomForestClassifier(
        n_estimators=150,
        random_state=42,
        class_weight="balanced"
    )

    random_forest.fit(
        X_scaled,
        y
    )

    return (
        random_forest,
        kmeans,
        scaler,
        df
    )


# ============================================================
# PREDICTION
# ============================================================

def predict_student(
    attendance,
    study_hours,
    internal,
    assignment,
    previous
):

    (
        random_forest,
        kmeans,
        scaler,
        dataset
    ) = train_models()

    student = np.array([[
        attendance,
        (study_hours / 6) * 100,
        (internal / 40) * 100,
        (assignment / 15) * 100,
        (previous / 60) * 100
    ]])

    student_scaled = scaler.transform(
        student
    )

    # K-MEANS
    cluster = int(
        kmeans.predict(
            student_scaled
        )[0]
    )

    # RANDOM FOREST
    prediction = random_forest.predict(
        student_scaled
    )[0]

    probabilities = random_forest.predict_proba(
        student_scaled
    )[0]

    confidence = float(
        np.max(probabilities) * 100
    )

    return (
        prediction,
        confidence,
        cluster
    )


# ============================================================
# REPORT STORAGE
# ============================================================

REPORT_COLUMNS = [
    "Student_Name",
    "University_ID",
    "Semester",
    "Branch",
    "Subjects_JSON",
    "Created_Time"
]


def load_reports():

    if not os.path.exists(REPORT_FILE):

        return pd.DataFrame(
            columns=REPORT_COLUMNS
        )

    try:

        df = pd.read_csv(
            REPORT_FILE
        )

        for column in REPORT_COLUMNS:

            if column not in df.columns:

                df[column] = ""

        return df

    except Exception:

        return pd.DataFrame(
            columns=REPORT_COLUMNS
        )


def save_reports(df):

    df.to_csv(
        REPORT_FILE,
        index=False
    )


# ============================================================
# PDF STYLES
# ============================================================

def create_pdf_styles():

    styles = getSampleStyleSheet()

    title = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=18,
        spaceAfter=10
    )

    heading = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=13,
        spaceBefore=12,
        spaceAfter=8
    )

    subheading = ParagraphStyle(
        "CustomSubHeading",
        parent=styles["Heading3"],
        fontSize=10,
        spaceBefore=8,
        spaceAfter=5
    )

    normal = ParagraphStyle(
        "CustomNormal",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=11
    )

    small = ParagraphStyle(
        "CustomSmall",
        parent=styles["Normal"],
        fontSize=7.5,
        leading=10
    )

    return (
        title,
        heading,
        subheading,
        normal,
        small
    )


# ============================================================
# COLOURED STUDENT PDF
# ============================================================

def generate_student_pdf(student):

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=28,
        leftMargin=28,
        topMargin=28,
        bottomMargin=28
    )

    (
        title_style,
        heading_style,
        subheading_style,
        normal_style,
        small_style
    ) = create_pdf_styles()

    story = []

    # ========================================================
    # 1. TITLE
    # ========================================================

    story.append(
        Paragraph(
            "STUDENT PERFORMANCE PROGRESS REPORT",
            title_style
        )
    )

    story.append(
        Paragraph(
            "AI-Based Student Performance Prediction System",
            normal_style
        )
    )

    story.append(
        Spacer(1, 12)
    )

    # ========================================================
    # 2. STUDENT DETAILS
    # ========================================================

    story.append(
        Paragraph(
            "1. Student Details",
            heading_style
        )
    )

    student_details = [

        [
            "Student Name",
            str(student["Student_Name"])
        ],

        [
            "University ID",
            str(student["University_ID"])
        ],

        [
            "Semester",
            str(student["Semester"])
        ],

        [
            "Branch",
            str(student["Branch"])
        ],

        [
            "Report Generated",
            str(student["Created_Time"])
        ]
    ]

    student_table = Table(
        student_details,
        colWidths=[125, 385]
    )

    student_table.setStyle(
        TableStyle([

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.HexColor("#E8EEF7")
            ),

            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                9
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            )
        ])
    )

    story.append(
        student_table
    )

    story.append(
        Spacer(1, 15)
    )

    subjects = json.loads(
        student["Subjects_JSON"]
    )

    # ========================================================
    # 3. OVERALL INFORMATION
    # ========================================================

    story.append(
        Paragraph(
            "2. Overall Information and Marks",
            heading_style
        )
    )

    total_internal = sum(
        float(x["Internal"])
        for x in subjects
    )

    total_assignment = sum(
        float(x["Assignment"])
        for x in subjects
    )

    total_previous = sum(
        float(x["Previous"])
        for x in subjects
    )

    total_attendance_mark = sum(
        int(x["Attendance_Mark"])
        for x in subjects
    )

    total_possible_internal = (
        len(subjects) * 40
    )

    total_possible_assignment = (
        len(subjects) * 15
    )

    total_possible_previous = (
        len(subjects) * 60
    )

    average_overall = np.mean([
        x["Overall"]
        for x in subjects
    ])

    overall_data = [

        [
            "Number of Subjects",
            str(len(subjects))
        ],

        [
            "Total Internal",
            f"{total_internal:.0f} / "
            f"{total_possible_internal}"
        ],

        [
            "Total Assignment",
            f"{total_assignment:.0f} / "
            f"{total_possible_assignment}"
        ],

        [
            "Total Previous Mark",
            f"{total_previous:.0f} / "
            f"{total_possible_previous}"
        ],

        [
            "Attendance Converted Total",
            f"{total_attendance_mark} / "
            f"{len(subjects) * 5}"
        ],

        [
            "Overall Performance Score",
            f"{average_overall:.2f}%"
        ]
    ]

    overall_table = Table(
        overall_data,
        colWidths=[230, 280]
    )

    overall_table.setStyle(
        TableStyle([

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.HexColor("#EAF4EA")
            ),

            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8.5
            )
        ])
    )

    story.append(
        overall_table
    )

    story.append(
        Spacer(1, 15)
    )

    # ========================================================
    # 4. SUBJECT-WISE PERFORMANCE
    # ========================================================

    story.append(
        Paragraph(
            "3. Subject-wise Performance",
            heading_style
        )
    )

    subject_table_data = [

        [
            "Subject",
            "Indicator",
            "Attendance",
            "Study",
            "Internal",
            "Assignment",
            "Previous",
            "Score"
        ]
    ]

    subject_table_objects = []

    for subject in subjects:

        circle = performance_circle(
            subject["Level"]
        )

        subject_table_data.append([

            subject["Subject"],

            circle,

            f'{subject["Attendance"]:.0f}%',

            f'{subject["Study_Hours"]:.1f}/6',

            f'{subject["Internal"]:.0f}/40',

            f'{subject["Assignment"]:.0f}/15',

            f'{subject["Previous"]:.0f}/60',

            f'{subject["Overall"]:.1f}%'
        ])

        subject_table_objects.append(
            subject
        )

    subject_table = Table(
        subject_table_data,
        repeatRows=1,
        colWidths=[
            105,
            30,
            50,
            42,
            55,
            58,
            55,
            55
        ]
    )

    table_commands = [

        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.4,
            colors.grey
        ),

        (
            "BACKGROUND",
            (0, 0),
            (-1, 0),
            colors.HexColor("#D9EAF7")
        ),

        (
            "FONTNAME",
            (0, 0),
            (-1, 0),
            "Helvetica-Bold"
        ),

        (
            "FONTSIZE",
            (0, 0),
            (-1, -1),
            6.8
        ),

        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "MIDDLE"
        )
    ]

    for row_index, subject in enumerate(
        subject_table_objects,
        start=1
    ):

        table_commands.append(
            (
                "BACKGROUND",
                (0, row_index),
                (-1, row_index),
                colors.HexColor(
                    PERFORMANCE_COLORS[
                        subject["Level"]
                    ]
                )
            )
        )

    subject_table.setStyle(
        TableStyle(table_commands)
    )

    story.append(
        subject_table
    )

    story.append(
        Spacer(1, 15)
    )

    # ========================================================
    # 5. ASSESSMENT INFORMATION & CONVERSION
    # ========================================================

    story.append(
        Paragraph(
            "4. Assessment Information and Conversion",
            heading_style
        )
    )

    story.append(
        Paragraph(
            "Assessment limits used in this project:",
            normal_style
        )
    )

    assessment_info = [

        ["Assessment", "Maximum"],

        ["Attendance", "100%"],

        ["Study Hours", "6 hours/day"],

        ["Internal Mark", "40"],

        ["Assignment Score", "15"],

        ["Previous Mark", "60"]
    ]

    assessment_table = Table(
        assessment_info,
        colWidths=[250, 260]
    )

    assessment_table.setStyle(
        TableStyle([

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.grey
            ),

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#D9EAF7")
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
            )
        ])
    )

    story.append(
        assessment_table
    )

    story.append(
        Spacer(1, 8)
    )

    story.append(
        Paragraph(
            "Attendance Conversion",
            subheading_style
        )
    )

    conversion_table = Table(

        [
            ["Attendance", "Converted Mark"],

            ["90–100%", "5"],

            ["80–89%", "4"],

            ["70–79%", "3"],

            ["60–69%", "2"],

            ["10–59%", "1"],

            ["Below 10%", "0"]
        ],

        colWidths=[250, 260]
    )

    conversion_table.setStyle(
        TableStyle([

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.grey
            ),

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#D9EAF7")
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
            )
        ])
    )

    story.append(
        conversion_table
    )

    story.append(
        Spacer(1, 15)
    )

    # ========================================================
    # 6. EACH SUBJECT SEPARATELY
    # ========================================================

    story.append(
        Paragraph(
            "5. Detailed Subject-wise Assessment",
            heading_style
        )
    )

    for index, subject in enumerate(
        subjects,
        start=1
    ):

        level = subject["Level"]

        background = colors.HexColor(
            PERFORMANCE_COLORS[level]
        )

        subject_header = Table(

            [[

                f"{index}. {subject['Subject']}",

                performance_circle(level),

                level

            ]],

            colWidths=[330, 35, 145]
        )

        subject_header.setStyle(
            TableStyle([

                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    background
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, -1),
                    "Helvetica-Bold"
                ),

                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    9
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                )
            ])
        )

        story.append(
            subject_header
        )

        story.append(
            Spacer(1, 4)
        )

        details = [

            [
                "Attendance",
                f'{subject["Attendance"]:.0f}%'
            ],

            [
                "Attendance Conversion",
                f'{subject["Attendance_Mark"]}/5'
            ],

            [
                "Study Hours",
                f'{subject["Study_Hours"]:.1f}/6 hours'
            ],

            [
                "Internal Mark",
                f'{subject["Internal"]:.0f}/40'
            ],

            [
                "Assignment",
                f'{subject["Assignment"]:.0f}/15'
            ],

            [
                "Previous Mark",
                f'{subject["Previous"]:.0f}/60'
            ],

            [
                "Overall Subject Score",
                f'{subject["Overall"]:.2f}%'
            ]
        ]

        details_table = Table(
            details,
            colWidths=[220, 290]
        )

        details_table.setStyle(
            TableStyle([

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.3,
                    colors.grey
                ),

                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#F4F4F4")
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold"
                ),

                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8
                )
            ])
        )

        story.append(
            details_table
        )

        story.append(
            Spacer(1, 5)
        )

        # ----------------------------------------------------
        # K-MEANS
        # ----------------------------------------------------

        if "Cluster" in subject:

            story.append(
                Paragraph(
                    f'<b>K-Means Cluster:</b> '
                    f'{subject["Cluster"]}',
                    normal_style
                )
            )

        # ----------------------------------------------------
        # RANDOM FOREST
        # ----------------------------------------------------

        if "ML_Prediction" in subject:

            story.append(
                Paragraph(
                    f'<b>Random Forest Prediction:</b> '
                    f'{subject["ML_Prediction"]}',
                    normal_style
                )
            )

            story.append(
                Paragraph(
                    f'<b>Prediction Confidence:</b> '
                    f'{subject["Confidence"]:.2f}%',
                    normal_style
                )
            )

        story.append(
            Spacer(1, 4)
        )

        # ----------------------------------------------------
        # FEEDBACK
        # ----------------------------------------------------

        story.append(
            Paragraph(
                "<b>Feedback / Improvement Method:</b>",
                normal_style
            )
        )

        for method in subject[
            "Recommendations"
        ]:

            story.append(
                Paragraph(
                    "• " + method,
                    small_style
                )
            )

        story.append(
            Spacer(1, 10)
        )

    # ========================================================
    # 7. PERFORMANCE LEGEND
    # ========================================================

    story.append(
        Paragraph(
            "6. Performance Indicator",
            heading_style
        )
    )

    legend_rows = [

        [
            performance_circle(
                "Low Performance"
            ),
            "Low Performance",
            "Needs improvement"
        ],

        [
            performance_circle(
                "Average Performance"
            ),
            "Average Performance",
            "Regular improvement required"
        ],

        [
            performance_circle(
                "Above Average"
            ),
            "Above Average",
            "Good progress; incremental improvement"
        ],

        [
            performance_circle(
                "Good Performance"
            ),
            "Good Performance",
            "Excellent; maintain consistency"
        ]
    ]

    legend_table = Table(
        legend_rows,
        colWidths=[35, 170, 305]
    )

    legend_table.setStyle(
        TableStyle([

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.3,
                colors.grey
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            )
        ])
    )

    story.append(
        legend_table
    )

    story.append(
        Spacer(1, 15)
    )

    # ========================================================
    # 8. NOTE
    # ========================================================

    story.append(
        Paragraph(
            "Note: The performance categories in this project "
            "are project-defined indicators. K-Means cluster "
            "numbers are group identifiers and do not themselves "
            "represent a performance grade. Machine learning "
            "results are intended to support academic monitoring "
            "and should not replace teacher evaluation.",
            small_style
        )
    )

    document.build(
        story
    )

    buffer.seek(0)

    return buffer.getvalue()


# ============================================================
# REGISTRATION / AUDIT STORAGE
# ============================================================

REGISTRATION_FILE = os.path.join(DATA_DIR, "student_registrations.csv")
AUDIT_FILE = os.path.join(DATA_DIR, "audit_log.csv")

REGISTRATION_COLUMNS = [
    "Username", "University_ID", "Student_Name", "Department",
    "Semester", "Registered_By", "Registered_Time"
]
AUDIT_COLUMNS = ["Time", "Role", "User", "Action", "University_ID", "Details"]


def load_registrations():
    if os.path.exists(REGISTRATION_FILE):
        try:
            df = pd.read_csv(REGISTRATION_FILE).fillna("")
            for c in REGISTRATION_COLUMNS:
                if c not in df.columns:
                    df[c] = ""
            return df[REGISTRATION_COLUMNS]
        except Exception:
            pass
    return pd.DataFrame(columns=REGISTRATION_COLUMNS)


def save_registrations(df):
    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(REGISTRATION_FILE, index=False)


def log_action(role, user, action, university_id="", details=""):
    row = pd.DataFrame([{
        "Time": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "Role": role,
        "User": user,
        "Action": action,
        "University_ID": university_id,
        "Details": details,
    }])
    if os.path.exists(AUDIT_FILE):
        try:
            old = pd.read_csv(AUDIT_FILE).fillna("")
        except Exception:
            old = pd.DataFrame(columns=AUDIT_COLUMNS)
        row = pd.concat([old, row], ignore_index=True)
    row.to_csv(AUDIT_FILE, index=False)


def tutor_can_access(department, semester):
    assigned_department = st.session_state.get("teacher_branch")
    assigned_semester = st.session_state.get("teacher_semester", "ALL")
    return (
        str(department) == str(assigned_department)
        and (assigned_semester == "ALL" or str(semester) == str(assigned_semester))
    )


def intro_style():
    st.markdown("""
    <style>
    .hero3d{padding:32px 18px 26px;border-radius:28px;text-align:center;
      background:radial-gradient(circle at 50% 25%,rgba(87,180,255,.28),transparent 32%),
      linear-gradient(135deg,#07152f,#101b3d 55%,#07101f);color:white;
      box-shadow:0 18px 60px rgba(0,0,0,.28);overflow:hidden;position:relative}
    .orb{font-size:72px;animation:float 2.8s ease-in-out infinite;display:inline-block;
      filter:drop-shadow(0 0 20px #6cf)}
    .cube{font-size:48px;display:inline-block;animation:spin 5s linear infinite;margin:8px 22px}
    .ring{font-size:38px;display:inline-block;animation:spin 7s linear infinite}
    .hero-title{font-size:clamp(30px,6vw,64px);font-weight:900;letter-spacing:2px;
      text-shadow:0 0 18px rgba(110,210,255,.65)}
    .hero-sub{font-size:18px;opacity:.86;letter-spacing:1px}
    .chip{display:inline-block;padding:7px 13px;margin:5px;border:1px solid rgba(255,255,255,.18);
      border-radius:999px;background:rgba(255,255,255,.08)}
    @keyframes spin{to{transform:rotateY(360deg) rotateZ(360deg)}}
    @keyframes float{50%{transform:translateY(-12px) rotate(3deg)}}
    </style>
    <div class="hero3d">
      <div><span class="orb">🎓</span><span class="cube">🧊</span><span class="ring">⭕</span></div>
      <div class="hero-title">EDUPREDICT SPP</div>
      <div class="hero-sub">AI • K-MEANS • SMART ACADEMIC MONITORING • KTU B.TECH</div>
      <div style="margin-top:12px">
        <span class="chip">🤖 ANN</span><span class="chip">📊 Analytics</span>
        <span class="chip">🧑‍🏫 Tutor</span><span class="chip">🎓 Student</span>
        <span class="chip">🏫 Principal</span>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# HOME
# ============================================================

def home_page():
    intro_style()
    st.markdown("## 🚀 Smart Academic Portal")
    st.caption("One connected workflow: Registration → Marks → Student Analysis → Principal Monitoring")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 🎓 Student")
        st.caption("View your tutor-registered profile and calculate marks after marks are submitted.")
        if st.button("🎓 Enter Student Portal", width="stretch"):
            st.session_state.page = "student_login"; st.rerun()
    with c2:
        st.markdown("### 🧑‍🏫 Tutor")
        st.caption("Register students and enter marks only for your assigned department/semester.")
        if st.button("🧑‍🏫 Tutor Login", width="stretch"):
            st.session_state.page = "teacher_login"; st.rerun()
    with c3:
        st.markdown("### 🏫 Principal")
        st.caption("Monitor registrations, mark-entry activity, tutors and students.")
        if st.button("🏫 Principal Login", width="stretch"):
            st.session_state.page = "principal_login"; st.rerun()


# ============================================================
# STUDENT LOGIN — UNIVERSITY ID ONLY
# ============================================================

def student_login():
    intro_style()
    st.title("🎓 Student Portal Login")
    st.info("🔐 Student login uses your **University ID only**. Username and password are not required.")
    st.markdown("**Example University ID:** `SNM25CE001`  •  **Example registered name:** `Aromal kv`")
    university_id = st.text_input("🪪 University ID", placeholder="e.g. SNM25CE001").strip()
    if st.button("🚀 Open My Student Portal", type="primary", width="stretch"):
        regs = load_registrations()
        match = regs[regs["University_ID"].astype(str).str.upper() == university_id.upper()]
        if match.empty:
            st.error("❌ University ID is not registered by a tutor yet.")
        else:
            student = match.iloc[-1].to_dict()
            st.session_state.logged_in = True
            st.session_state.role = "student"
            st.session_state.username = student["Username"]
            st.session_state.student_id = student["University_ID"]
            st.session_state.page = "student_dashboard"
            log_action("Student", student["Username"], "Student Login", student["University_ID"], "University ID login")
            st.success("🎉 Welcome! Your tutor-registered profile is ready.")
            st.rerun()
    if st.button("⬅ Back", width="stretch"):
        st.session_state.page = "home"; st.rerun()


# ============================================================
# TUTOR LOGIN
# ============================================================

def teacher_login():
    intro_style()
    st.title("🧑‍🏫 Tutor Login")
    username = st.text_input("👤 Tutor Username")
    password = st.text_input("🔑 Password", type="password")
    st.caption("Tutor access is restricted by the tutor's assigned department and semester.")
    if st.button("🔐 Login to Tutor Control Center", type="primary", width="stretch"):
        if username in TEACHERS and TEACHERS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.role = "teacher"
            st.session_state.username = username
            st.session_state.teacher_branch = TEACHERS[username]["branch"]
            st.session_state.teacher_semester = TEACHERS[username].get("semester", "ALL")
            st.session_state.page = "teacher_dashboard"
            log_action("Tutor", username, "Tutor Login", "", f"Department={st.session_state.teacher_branch}; Semester={st.session_state.teacher_semester}")
            st.rerun()
        else:
            st.error("❌ Invalid tutor username or password.")
    if st.button("⬅ Back", width="stretch"):
        st.session_state.page = "home"; st.rerun()


# ============================================================
# STUDENT DASHBOARD
# ============================================================

def student_dashboard():
    st.title("🎓 My Student Portal")
    if st.button("🚪 Logout"):
        log_action("Student", st.session_state.get("username", ""), "Student Logout", st.session_state.get("student_id", ""))
        st.session_state.logged_in=False; st.session_state.role=None; st.session_state.page="home"; st.rerun()

    uid = str(st.session_state.get("student_id", ""))
    regs = load_registrations()
    reg_rows = regs[regs["University_ID"].astype(str).str.upper() == uid.upper()]
    if reg_rows.empty:
        st.error("Registration not found."); return
    reg = reg_rows.iloc[-1]

    st.markdown("### 🪪 Tutor-Registered Student Profile")
    p1,p2,p3,p4 = st.columns(4)
    p1.metric("👤 Name", str(reg["Student_Name"]))
    p2.metric("🪪 University ID", str(reg["University_ID"]))
    p3.metric("🏛️ Department", str(reg["Department"]))
    p4.metric("📚 Semester", str(reg["Semester"]))
    st.caption(f"🧑‍🏫 Registered by: {reg['Registered_By']}  •  🕒 {reg['Registered_Time']}")

    reports = load_reports()
    student_reports = reports[
        (reports["University_ID"].astype(str).str.upper() == uid.upper()) &
        (reports["Branch"].astype(str) == str(reg["Department"])) &
        (reports["Semester"].astype(str) == str(reg["Semester"]))
    ]

    st.divider()
    st.markdown("### 📊 Marks & Performance")
    if student_reports.empty:
        st.warning("⏳ Your tutor has registered your profile, but marks have not been entered yet.")
        st.button("🔒 Calculate My Mark — Waiting for Tutor Marks", disabled=True, width="stretch")
        st.info("💡 Once your tutor submits marks, the Calculate My Mark button will become available here.")
        return

    report = student_reports.iloc[-1].to_dict()
    subjects = json.loads(report["Subjects_JSON"])
    st.success("✅ Tutor marks are available. You can now calculate and view your performance.")

    if "student_calculated" not in st.session_state:
        st.session_state.student_calculated = False

    if st.button("🧮✨ Calculate My Mark", type="primary", width="stretch"):
        st.session_state.student_calculated = True
        log_action("Student", st.session_state.get("username", ""), "Calculated Marks", uid, f"Department={reg['Department']}; Semester={reg['Semester']}")
        st.balloons()

    if not st.session_state.student_calculated:
        st.info("👆 Click **Calculate My Mark** to reveal your marks and AI-supported performance analysis.")
        return

    # Student can enter study hours only; tutor-entered marks remain read-only.
    st.markdown("### ⏱️ Daily Study Hours")
    study_hours = {}
    for i, subject in enumerate(subjects):
        key = f"study_{uid}_{i}"
        study_hours[subject["Subject"]] = st.number_input(
            f"📘 {subject['Subject']} — hours/day", 0.0, 12.0, float(subject.get("Study_Hours", 0)), 0.5, key=key
        )

    rows=[]
    for subject in subjects:
        sh = study_hours[subject["Subject"]]
        attendance = float(subject.get("Attendance", 0)); internal=float(subject.get("Internal",0)); assignment=float(subject.get("Assignment",0)); previous=float(subject.get("Previous",0))
        level, overall = calculate_performance(attendance, sh, internal, assignment, previous)
        pred, conf, cluster = predict_student(attendance, sh, internal, assignment, previous)
        rows.append({"Subject":subject["Subject"],"Attendance %":attendance,"Attendance /5":attendance_mark(attendance),"Internal /40":internal,"Assignment /15":assignment,"Previous /60":previous,"Study Hours":sh,"Score %":overall,"Level":level,"AI Prediction":pred,"Confidence %":conf,"K-Means":cluster})

    result_df=pd.DataFrame(rows)
    st.dataframe(result_df, width="stretch")
    overall_score=float(result_df["Score %"].mean()) if not result_df.empty else 0
    st.metric("🏆 Overall Performance", f"{overall_score:.2f}%")
    for _, r in result_df.iterrows():
        icon={"Low Performance":"🔴","Average Performance":"🟠","Above Average":"🟡","Good Performance":"🟢"}.get(r["Level"],"🔵")
        st.markdown(f"### {icon} {r['Subject']} — {r['Level']}")
        if r["Level"] == "Good Performance": st.success("🌟 Excellent work! Keep your consistency and continue practicing.")
        elif r["Level"] == "Above Average": st.warning("🟡 You are doing well. Focus more on internals, revision and regular practice.")
        elif r["Level"] == "Average Performance": st.info("🟠 Try a fixed daily study routine, more problem practice and weekly revision.")
        else: st.error("🔴 Needs Improvement — increase practice time, clarify doubts early and revise fundamentals.")

    pdf = generate_student_pdf(report)
    st.download_button("📥 Download Progress Report PDF", pdf, f"{uid}_Progress_Report.pdf", "application/pdf", width="stretch")


# ============================================================
# TUTOR DASHBOARD — REGISTRATION + MARK ENTRY
# ============================================================

def teacher_dashboard():
    department = st.session_state.get("teacher_branch")
    assigned_semester = st.session_state.get("teacher_semester", "ALL")
    username = st.session_state.get("username", "")
    st.title("🧑‍🏫 Tutor Control Center")
    if assigned_semester == "ALL":
        st.session_state.teacher_semester = st.selectbox(
            "📚 Active Semester Scope", list(SUBJECTS.keys()), key="active_tutor_semester"
        )
        assigned_semester = st.session_state.teacher_semester
    st.success(f"👨‍🏫 Tutor: {username}  |  🏛️ Department: {department}  |  📚 Active semester scope: {assigned_semester}")
    st.caption("🔐 Marks and registrations are restricted to the tutor's department + active semester scope.")
    if st.button("🚪 Logout Tutor"):
        log_action("Tutor", username, "Tutor Logout", "", f"Department={department}; Semester={assigned_semester}")
        st.session_state.logged_in=False; st.session_state.role=None; st.session_state.username=None; st.session_state.page="home"; st.rerun()

    tab1, tab2, tab3 = st.tabs(["🧑‍🎓 Student Registration", "📝 Student Mark Entry", "📋 Registered Students"])

    with tab1:
        st.subheader("🪪 Register a Student")
        st.info("Register first. Only registered students can receive marks or open the student portal.")
        c1,c2=st.columns(2)
        with c1:
            reg_username=st.text_input("👤 Student Username", placeholder="e.g. Aromal kv")
            reg_uid=st.text_input("🪪 University ID", placeholder="e.g. SNM25CE001")
            reg_name=st.text_input("🧑 Student Name", placeholder="e.g. Aromal K. V.")
        with c2:
            reg_dept=st.selectbox("🏛️ Student Department", BRANCHES, index=BRANCHES.index(department) if department in BRANCHES else 0)
            sem_options=[assigned_semester] if assigned_semester != "ALL" else list(SUBJECTS.keys())
            reg_sem=st.selectbox("📚 Student Semester", sem_options)
        if st.button("✅ Submit Student Registration", type="primary", width="stretch"):
            if not reg_username.strip() or not reg_uid.strip() or not reg_name.strip():
                st.error("Please fill username, University ID and name.")
            elif reg_dept != department or (assigned_semester != "ALL" and reg_sem != assigned_semester):
                st.error("🚫 You can register only students in your assigned department/semester.")
            else:
                df=load_registrations()
                if not df.empty and (df["University_ID"].astype(str).str.upper() == reg_uid.strip().upper()).any():
                    st.error("⚠️ This University ID is already registered.")
                else:
                    row={"Username":reg_username.strip(),"University_ID":reg_uid.strip().upper(),"Student_Name":reg_name.strip(),"Department":reg_dept,"Semester":reg_sem,"Registered_By":username,"Registered_Time":datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
                    save_registrations(pd.concat([df,pd.DataFrame([row])],ignore_index=True))
                    log_action("Tutor", username, "Student Registration", row["University_ID"], f"Name={row['Student_Name']}; Department={reg_dept}; Semester={reg_sem}")
                    st.success("🎉 Student registered successfully!")
                    st.balloons()

    with tab2:
        st.subheader("📝 Marks Entry")
        st.caption("🔒 Department + semester restriction is enforced. Marks can be entered only for registered students assigned to this tutor scope.")
        regs=load_registrations()
        allowed=regs[(regs["Department"].astype(str)==str(department)) & ((assigned_semester=="ALL") | (regs["Semester"].astype(str)==str(assigned_semester)))]
        if allowed.empty:
            st.warning("📭 No registered students are available for your assigned department/semester.")
        else:
            selected_uid=st.selectbox("🪪 Select Registered University ID", allowed["University_ID"].astype(str).tolist())
            selected=allowed[allowed["University_ID"].astype(str)==str(selected_uid)].iloc[0]
            st.markdown(f"### 👤 {selected['Student_Name']}  •  {selected['University_ID']}")
            st.write(f"🏛️ **{selected['Department']}**  |  📚 **{selected['Semester']}**")
            subjects=SUBJECTS[selected["Semester"]][:6]
            subject_results=[]
            for i, subject in enumerate(subjects):
                st.markdown(f"#### 📘 {i+1}. {subject}")
                a,b,c,d=st.columns(4)
                with a: att=st.number_input("Attendance %",0.0,100.0,75.0,1.0,key=f"att_{selected_uid}_{i}")
                with b: internal=st.number_input("Internal /40",0.0,40.0,20.0,1.0,key=f"int_{selected_uid}_{i}")
                with c: assignment=st.number_input("Assignment /15",0.0,15.0,8.0,1.0,key=f"asg_{selected_uid}_{i}")
                with d: previous=st.number_input("Previous /60",0.0,60.0,30.0,1.0,key=f"prev_{selected_uid}_{i}")
                subject_results.append({"Subject":subject,"Attendance":att,"Study_Hours":0.0,"Internal":internal,"Assignment":assignment,"Previous":previous,"Attendance_Mark":attendance_mark(att),"Level":"","Overall":0.0,"Recommendations":[]})
            if st.button("💾✨ Submit Student Marks", type="primary", width="stretch"):
                # Re-check registration and tutor scope before saving.
                latest_reg=load_registrations()
                check=latest_reg[(latest_reg["University_ID"].astype(str).str.upper()==str(selected_uid).upper())]
                if check.empty or not tutor_can_access(check.iloc[-1]["Department"],check.iloc[-1]["Semester"]):
                    st.error("🚫 Permission denied: this student is outside your assigned department/semester.")
                else:
                    for x in subject_results:
                        x["Level"],x["Overall"]=calculate_performance(x["Attendance"],0,x["Internal"],x["Assignment"],x["Previous"])
                        x["ML_Prediction"],x["Confidence"],x["Cluster"]=predict_student(x["Attendance"],0,x["Internal"],x["Assignment"],x["Previous"])
                    reports=load_reports()
                    reports=reports[reports["University_ID"].astype(str).str.upper()!=str(selected_uid).upper()].copy()
                    new={"Student_Name":selected["Student_Name"],"University_ID":selected_uid,"Semester":selected["Semester"],"Branch":selected["Department"],"Subjects_JSON":json.dumps(subject_results),"Created_Time":datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
                    save_reports(pd.concat([reports,pd.DataFrame([new])],ignore_index=True))
                    log_action("Tutor",username,"Marks Submitted",selected_uid,f"Department={selected['Department']}; Semester={selected['Semester']}; Subjects=6")
                    st.success("🎉 Marks submitted successfully. Student can now calculate and view marks.")
                    st.toast("📚 Marks saved",icon="✅")

    with tab3:
        st.subheader("📋 Registered Students")
        regs=load_registrations()
        mine=regs[(regs["Department"].astype(str)==str(department)) & ((assigned_semester=="ALL") | (regs["Semester"].astype(str)==str(assigned_semester)))]
        if mine.empty: st.info("No students registered in your scope.")
        else: st.dataframe(mine, width="stretch")


# ============================================================
# PRINCIPAL LOGIN / MONITORING (also deployable as a separate app)
# ============================================================

def principal_login():
    intro_style()
    st.title("🏫 Principal Login")
    st.info("This monitoring portal is read-only for student/tutor academic records. It records tutor and student actions through the audit log.")
    username=st.text_input("🏫 Principal Username")
    password=st.text_input("🔑 Principal Password", type="password")
    if st.button("🔐 Enter Principal Monitoring", type="primary", width="stretch"):
        if username == "principal" and password == "principal@2007":
            st.session_state.logged_in=True; st.session_state.role="principal"; st.session_state.username=username; st.session_state.page="principal_dashboard"; log_action("Principal",username,"Principal Login"); st.rerun()
        else: st.error("❌ Invalid principal login.")
    if st.button("⬅ Back", width="stretch"): st.session_state.page="home"; st.rerun()


def principal_dashboard():
    st.title("🏫 Principal Monitoring Dashboard")
    st.success("👑 Principal access: monitoring and oversight mode")
    if st.button("🚪 Logout Principal"):
        log_action("Principal",st.session_state.get("username",""),"Principal Logout"); st.session_state.logged_in=False; st.session_state.role=None; st.session_state.page="home"; st.rerun()
    regs=load_registrations(); reports=load_reports()
    audit=pd.read_csv(AUDIT_FILE).fillna("") if os.path.exists(AUDIT_FILE) else pd.DataFrame(columns=AUDIT_COLUMNS)
    a,b,c,d=st.columns(4)
    a.metric("🧑‍🎓 Registered Students",len(regs)); b.metric("📝 Marked Students",len(reports)); c.metric("🧑‍🏫 Active Tutor Accounts",len(TEACHERS)); d.metric("🕵️ Logged Actions",len(audit))
    st.markdown("### 📊 Department Overview")
    if regs.empty: st.info("No registrations yet.")
    else:
        summary=regs.groupby(["Department","Semester"]).size().reset_index(name="Students")
        st.dataframe(summary,width="stretch")
    st.markdown("### 🧑‍🎓 Student Registrations")
    st.dataframe(regs,width="stretch")
    st.markdown("### 📝 Tutor Mark Submission Records")
    if reports.empty: st.info("No marks submitted yet.")
    else: st.dataframe(reports[["Student_Name","University_ID","Branch","Semester","Created_Time"]],width="stretch")
    st.markdown("### 🕵️ Tutor & Student Action Monitor")
    st.dataframe(audit.sort_values("Time",ascending=False),width="stretch")
    st.download_button("📥 Download Audit Log",audit.to_csv(index=False).encode(),"principal_audit_log.csv","text/csv",width="stretch")


# ============================================================
# MAIN ROUTER
# ============================================================

if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "student_login":
    student_login()
elif st.session_state.page == "teacher_login":
    teacher_login()
elif st.session_state.page == "principal_login":
    principal_login()
elif st.session_state.page == "student_dashboard" and st.session_state.logged_in and st.session_state.role == "student":
    student_dashboard()
elif st.session_state.page == "teacher_dashboard" and st.session_state.logged_in and st.session_state.role == "teacher":
    teacher_dashboard()
elif st.session_state.page == "principal_dashboard" and st.session_state.logged_in and st.session_state.role == "principal":
    principal_dashboard()
else:
    st.session_state.page = "home"
    st.rerun()
