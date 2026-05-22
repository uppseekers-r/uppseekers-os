import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor

st.set_page_config(page_title="Uppseekers OS - Student Journey Roadmap", layout="wide")

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Access Denied. Please authenticate via the System Gateway Home page.")
    st.stop()

user_info = st.session_state.user_info

def get_db_connection():
    conn_params = st.secrets["connections"]["postgresql"]
    return psycopg2.connect(
        host=conn_params["host"], port=conn_params["port"],
        database=conn_params["database"], user=conn_params["username"],
        password=conn_params["password"], cursor_factory=RealDictCursor
    )

st.title("🗺 Student Journey Lifecycle Roadmap")

# Role-based workspace determination
if user_info['role'] == 'Student':
    # Direct fetch for own profile records
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM student_profiles WHERE user_id = %s", (user_info['id'],))
        profile = cur.fetchone()
        cur.close()
        conn.close()
        
        if profile:
            st.success(f"Verified Profile Target Enrollment Intake Cohort Year: {profile['target_enrollment_year']}")
            grade = profile['current_grade_level']
            
            # Contextual roadmap building logic execution
            st.markdown(f"### Current Phase: **Grade {grade} Milestones**")
            
            if grade <= 10:
                st.info("📌 **Foundation Stage Focus Areas:** Maintain target high school GPA scores, isolate primary extracurricular interest pillars, and register for early academic skill development competitions.")
            elif grade == 11:
                st.warning("⚠️ **Acceleration Stage Focus Areas:** Lock down finalized SAT/ACT target test sittings, select your university list options, and begin early brainstorming for Common App personal statements.")
            else:
                st.error("🔥 **Execution Stage Focus Areas:** Finalize early action deadlines, submit certified transcripts, complete parent verification agreements, and finalize mock review panels.")
        else:
            st.error("No student tracking metadata linked to this login record. Reach out to system operations support.")
    except Exception as e:
        st.error(f"Database Read Failure: {e}")
else:
    st.subheader("Counselor / Operational Student Tracking Pipeline Workspace")
    st.write("Select a managed student profile to view their milestone tracking data:")
    # Dropdowns and operational search queries would go here for staff roles
