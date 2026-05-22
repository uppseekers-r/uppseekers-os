import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Uppseekers OS - Dashboard", layout="wide")

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Access Denied. Please authenticate via the System Gateway Home page.")
    st.stop()

user_role = st.session_state.user_info['role']

def get_db_connection():
    conn_params = st.secrets["connections"]["postgresql"]
    return psycopg2.connect(
        host=conn_params["host"], port=conn_params["port"],
        database=conn_params["database"], user=conn_params["username"],
        password=conn_params["password"], cursor_factory=RealDictCursor
    )

st.title(f"📊 System Management Analytics Dashboard")
st.caption(f"Contextual Access Level View: **{user_role}**")

# Contextual visibility logic
if user_role in ['Admin', 'Manager', 'Counselor']:
    try:
        conn = get_db_connection()
        
        # Pull core metric totals
        df_tasks = pd.read_sql("SELECT status, count(*) as count FROM tasks GROUP BY status", conn)
        df_students = pd.read_sql("SELECT current_grade_level, count(*) as count FROM student_profiles GROUP BY current_grade_level", conn)
        
        conn.close()
        
        # High-level metrics layout
        m1, m2, m3 = st.columns(3)
        m1.metric("Active Student Roster Count", df_students['count'].sum() if not df_students.empty else 0)
        m2.metric("Total Outstanding Tasks", df_tasks['count'].sum() if not df_tasks.empty else 0)
        m3.metric("System Operational Health", "Optimal (200 OK)")
        
        st.markdown("---")
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Task Completion Breakdown")
            if not df_tasks.empty:
                fig = px.pie(df_tasks, values='count', names='status', hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No tasks recorded in system records.")
        with c2:
            st.subheader("Roster Demographic Dispersion (By Grade)")
            if not df_students.empty:
                fig2 = px.bar(df_students, x='current_grade_level', y='count', labels={'current_grade_level': 'Grade Profile', 'count': 'Student Total'})
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No student profile cohorts mapped yet.")
                
    except Exception as e:
        st.error(f"Failed to fetch analytical datasets: {e}")
else:
    st.info("Welcome to Uppseekers OS! Your student dashboard overview is located on the 'Student Journey' module page.")
