EduPredict SPP data folder

CSV files:
- student_registrations.csv: student Smart Card/profile registrations
- student_reports.csv: tutor-entered academic records
- audit_log.csv: login/action history
- tutor_profiles.csv: tutor department and credit-score details
- smart_card_registrations.csv: Smart Card registration records

student_records/
- Keep individual student files/PDFs/photos here if the app uses local file storage.

IMPORTANT:
For two separate Streamlit Cloud apps, this local data folder is NOT a shared live database.
Use Supabase/PostgreSQL/Firebase for real Student -> Tutor -> Principal live synchronization.
