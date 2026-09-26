"""Principal Dashboard entry point.
Run with:
    streamlit run principal_dashboard.py
"""

# Importing app2 is intentional: app2 contains the complete Principal UI.
# main() is called explicitly so the dashboard cannot silently stay blank.
import app2

app2.main()
