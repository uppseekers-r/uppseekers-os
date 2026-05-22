import streamlit as st
import psycopg2

st.set_page_config(page_title="Student Hub & Trackers", layout="wide")

def get_db_connection():
    conn_params = st.secrets["connections"]["postgresql"]
    return psycopg2.connect(
        host=conn_params["host"], port=int(conn_params["port"]),
        database=conn_params["database"], user=conn_params["username"],
        password=conn_params["password"], cursor_factory=psycopg2.extras.RealDictCursor
    )

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("🔒 Session terminated. Please authenticate via the Main Portal.")
    st.stop()

st.title("🎯 Admissions Roadmap & Pipeline Task Boards")
st.markdown("---")

conn = get_db_connection()
cur = conn.cursor()

# LOAD ALL STUDENTS FROM DATABASE FOR ASSIGNMENT SELECTBOXES
cur.execute("SELECT id, first_name || ' ' || last_name AS name FROM users WHERE role='Student'")
all_students = cur.fetchall()

if not all_students:
    st.info("No active student records found in your database pipeline layer. Provision profiles on the Home screen.")
    st.stop()

selected_student_id = st.selectbox("🔦 Focus Target Student Workspace", options=[s['id'] for s in all_students], format_func=lambda x: next(s['name'] for s in all_students if s['id']==x))

# ROADMAP ENGINE INTERFACE
st.subheader("🗺️ Student Longitudinal Admission Journey Progress Tracker")
grades_tabs = st.tabs(["Grade 8-9 Profile Framework", "Grade 10 Strategy & Testing", "Grade 11 Intensive Build", "Grade 12 Applications & Selection"])

with grades_tabs[0]:
    st.markdown("### 🔍 Early Profile Discovery Framework")
    st.checkbox("Identify Academic Core Focus Areas and Target Country Regions", value=True)
    st.checkbox("Initialize Extracurricular Interests Log and NGO Projects Plan", value=False)
    
with grades_tabs[1]:
    st.markdown("### 📈 Standardized Testing & Extracurricular Deep-Dive")
    st.checkbox("Standardized Exam Diagnostic Planning (SAT/ACT Timelines)", value=False)
    st.checkbox("Secure Core Leadership Roles in Competitions & Research Modules", value=False)

with grades_tabs[2]:
    st.markdown("### 🔥 High-Stakes Profile Construction Phase")
    st.checkbox("Summer School Placements and Advanced University Research Internships", value=False)
    st.checkbox("Draft Master University College Shortlists (Reach, Target, Safety Split)", value=False)

with grades_tabs[3]:
    st.markdown("### 🎓 Core Submission Campaign Engine")
    st.checkbox("Finalize Common App Personal Statement and Country Essays", value=False)
    st.checkbox("Submit Early Action / Early Decision Applications", value=False)

st.markdown("---")
st.subheader("📋 Active Milestone Task Allocation Management")

# TASK FORM INJECTION
with st.form("add_task_form", clear_on_submit=True):
    t_title = st.text_input("Task Assignment Header")
    t_desc = st.text_area("Detailed Directives and Deliverable Requirements")
    col_t1, col_t2 = st.columns(2)
    t_status = col_t1.selectbox("Current Task Stage", ['Pending', 'In Progress', 'Under Review', 'Completed'])
    t_due = col_t2.date_input("Deadline Execution Date")
    
    submit_task = st.form_submit_button("Deploy Actionable Task Directive")
    if submit_task:
        if t_title:
            try:
                cur.execute("""
                    INSERT INTO tasks (student_id, title, description, status, due_date)
                    VALUES (%s, %s, %s, %s, %s);
                """, (selected_student_id, t_title, t_desc, t_status, t_due))
                conn.commit()
                st.success("Task assigned and written live to database schema.")
            except Exception as e:
                st.error(f"Task deployment failed: {e}")

# RENDER LIVE TASKS FOR SELECTED STUDENT
st.markdown("#### Currently Running Pipelines Operations:")
cur.execute("SELECT * FROM tasks WHERE student_id = %s ORDER BY due_date ASC", (selected_student_id,))
student_tasks = cur.fetchall()

if student_tasks:
    for tk in student_tasks:
        with st.expander(f"📌 [{tk['status']}] - {tk['title']} (Due: {tk['due_date']})"):
            st.write(tk['description'])
else:
    st.caption("No pending tasks tracked for this specific student profile account yet.")

cur.close()
conn.close()
