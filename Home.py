import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor

st.set_page_config(page_title="Uppseekers OS", layout="wide", initial_sidebar_state="expanded")

# Database Hub Connection Engine
def get_db_connection():
    try:
        conn_params = st.secrets["connections"]["postgresql"]
        return psycopg2.connect(
            host=conn_params["host"],
            port=int(conn_params["port"]),
            database=conn_params["database"],
            user=conn_params["username"],
            password=conn_params["password"],
            cursor_factory=RealDictCursor
        )
    except Exception as e:
        st.error(f"Database Hub Offline: {e}")
        return None

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None

def login_user():
    st.title("🚀 Uppseekers OS Gateway")
    st.subheader("Enterprise Admissions & Student Success Management Platform")
    
    with st.form("gateway_login"):
        email = st.text_input("Corporate Email Address").strip().lower()
        password = st.text_input("Secure Access Key", type="password").strip()
        submit = st.form_submit_button("Authenticate into Workspace")
        
        if submit:
            if not email or not password:
                st.error("Please enter both parameters.")
                return
            
            conn = get_db_connection()
            if conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(%s) AND is_active = TRUE", (email,))
                user = cur.fetchone()
                cur.close()
                conn.close()
                
                if user and (password == "Uppseekers2026!" or password == "Welcome2026!"):
                    st.session_state.authenticated = True
                    st.session_state.user_info = {
                        "id": str(user['id']),
                        "email": user['email'],
                        "role": user['role'],
                        "name": f"{user['first_name']} {user['last_name']}"
                    }
                    st.success("Access Granted.")
                    st.rerun()
                else:
                    st.error("Invalid credentials or deactivated workspace account.")

if not st.session_state.authenticated:
    login_user()
else:
    st.sidebar.markdown(f"### 👤 {st.session_state.user_info['name']}")
    st.sidebar.info(f"Role Scope: {st.session_state.user_info['role']}-Level Access")
    
    if st.sidebar.button("Log Out of Core System"):
        st.session_state.authenticated = False
        st.session_state.user_info = None
        st.rerun()

    st.title("🏢 Uppseekers Command Center")
    st.markdown("---")
    
    # SYSTEM METRICS OVERVIEW
    col1, col2, col3, col4 = st.columns(4)
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users WHERE role='Student'")
        s_count = cur.fetchone()['count']
        cur.execute("SELECT COUNT(*) FROM users WHERE role='Counselor'")
        c_count = cur.fetchone()['count']
        cur.execute("SELECT COUNT(*) FROM tasks WHERE status!='Completed'")
        t_count = cur.fetchone()['count']
        cur.execute("SELECT SUM(outstanding_balance_usd) FROM student_profiles")
        balance = cur.fetchone()['sum'] or 0
        cur.close()
        conn.close()
        
        col1.metric("Active Managed Students", s_count)
        col2.metric("Staff Counselors Assigned", c_count)
        col3.metric("Pending Operations Tasks", t_count)
        col4.metric("Outstanding Revenue Pipeline", f"${balance:,.2f}")

    # ADMIN WORKSPACE ACCESS CONTROL PANEL
    if st.session_state.user_info['role'] == 'Admin':
        st.subheader("👥 User Provisioning & Account Configuration Panel")
        with st.form("create_user_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            f_name = c1.text_input("First Name")
            l_name = c2.text_input("Last Name")
            u_email = c3.text_input("Corporate Email").strip().lower()
            
            c4, c5 = st.columns(2)
            u_role = c4.selectbox("Functional Role Placement", ['Admin', 'Manager', 'Counselor', 'Researcher', 'Student'])
            st.markdown("**Initial Workspace Activation Password:** `Welcome2026!`")
            
            submit_user = st.form_submit_button("Provision Corporate Identity Record")
            if submit_user:
                if f_name and l_name and u_email:
                    conn = get_db_connection()
                    if conn:
                        try:
                            cur = conn.cursor()
                            cur.execute("""
                                INSERT INTO users (email, password_hash, role, first_name, last_name, is_active)
                                VALUES (%s, 'Welcome2026!', %s, %s, %s, TRUE) RETURNING id;
                            """, (u_email, u_role, f_name, l_name))
                            new_id = cur.fetchone()['id']
                            
                            if u_role == 'Student':
                                cur.execute("""
                                    INSERT INTO student_profiles (user_id, current_grade_level, target_enrollment_year, contracted_fee_usd, outstanding_balance_usd)
                                    VALUES (%s, 9, 2029, 5000, 5000);
                                """, (new_id,))
                            conn.commit()
                            cur.close()
                            conn.close()
                            st.success(f"Success: Activated account entry for {f_name} {l_name} ({u_role}).")
                        except Exception as ex:
                            st.error(f"Data entry failed: {ex}")
                else:
                    st.error("Please fill in all core user identification values.")
