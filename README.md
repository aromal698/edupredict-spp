# 🎓 EduPredict SPP

Student Performance Prediction and Academic Monitoring System for KTU B.Tech project work.

## Files
- `app2.py` — Main Student + Tutor application
- `principal_dashboard.py` — Separate Principal monitoring application
- `requirements.txt` — Python dependencies
- `data/` — Runtime data directory

## Run locally
```bash
pip install -r requirements.txt
streamlit run app2.py
```

Principal portal:
```bash
streamlit run principal_dashboard.py
```

## Important
The applications currently use the local `data/` directory. For two separately deployed Streamlit Cloud apps to share live data, use a shared database/storage service such as Supabase/PostgreSQL rather than relying on separate local filesystems.

Do not commit real student personal data, marks, passwords, or secrets to a public GitHub repository.
