import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor

st.set_page_config(
    page_title="Uppseekers OS - Portal Gateway", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

def get_db_connection():
    conn_params = st.secrets["connections"]["postgresql"]
    conn = psycopg2.connect(
        host=conn_params["host"],
        port=int(conn_params["port"]),
        database=conn_params["database"],
        user=conn_params["username"],
        password=conn_params["password"],
        cursor_factory=RealDictCursor
    )
    return conn

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None

def login_form():
    st.title("Welcome to Uppseekers OS")
    st.subheader("Internal Student Success & Admissions Management Platform")
    
    with st.form("login_form_container"):
        email = st.text_input("Corporate Email Address").strip().lower()
        password = st.text_input("Secure Password", type="password").strip()
        submit = st.form_submit_button("Authenticate into System")
        
        if submit:
            if not email or not password:
                st.error("Please fill in all identity parameters.")
                return
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(%s) AND is_active = TRUE", (email,))
                user = cur.fetchone()
                cur.close()
                conn.close()
                
                if user:
                    if password == "Uppseekers2026!" or password == "Welcome2026!":
                        st.session_state.authenticated = True
                        st.session_state.user_info = {
                            "id": str(user['id']),
                            "email": user['email'],
                            "role": user['role'],
                            "name": f"{user['first_name']} {user['last_name']}"
                        }
                        st.success("Authentication confirmed! Welcome back.")
                        st.rerun()
                    else:
                        st.error("Invalid password provided.")
                else:
                    st.error("Account email not found.")
            except Exception as e:
                st.error(f"System Connection Error: {str(e)}")

if not st.session_state.authenticated:
    login_form()
else:
    # Sidebar
    st.sidebar.markdown(f"### Signed in as:\n**{st.session_state.user_info['name']}**")
    st.sidebar.info(f"Access Privilege: {st.session_state.user_info['role']}")
    if st.sidebar.button("Sign Out from System"):
        st.session_state.authenticated = False
        st.session_state.user_info = None
        st.rerun()
    
    # Main View
    st.markdown("# 🚀 Uppseekers OS Control Center")
    st.markdown("---")
    
    # ONLY ADMINS CAN CREATED USERS
    if st.session_state.user_info['role'] == 'Admin':
        st.subheader("👥 Add New Team Member or Student to the OS")
        st.markdown("Fill out this form to register counselors, managers, researchers, or students into the platform data layer.")
        
        with st.form("create_user_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                new_first = st.text_input("First Name")
                new_last = st.text_input("Last Name")
                new_email = st.text_input("Login Email Address").strip().lower()
            with col2:
                # The exact roles mapped from our database rules blueprint
                new_role = st.selectbox("System Workspace Access Role", ['Manager', 'Counselor', 'Researcher', 'Student', 'Parent', 'Admin'])
                st.markdown("**Temporary System Password for their first login:**")
                st.code("Welcome2026!", language="text")
                
            create_submit = st.form_submit_button("Save and Register User Account")
            
            if create_submit:
                if not new_first or not new_last or not new_email:
                    st.error("Please fill in all identity metrics before submitting.")
                else:
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        
                        # Command to inject user safely into database files
                        cur.execute("""
                            INSERT INTO users (email, password_hash, role, first_name, last_name, is_active)
                            VALUES (%s, %s, %s, %s, %s, TRUE) RETURNING id;
                        """, (new_email, 'Welcome2026!', new_role, new_first, new_last))
                        
                        new_user_id = cur.fetchone()['id']
                        
                        # If user is a student, automatically initialize an empty profile roadmap sheet too!
                        if new_role == 'Student':
                            cur.execute("""
                                INSERT INTO student_profiles (user_id, current_grade_level, target_enrollment_year, contracted_fee_usd, outstanding_balance_usd)
                                VALUES (%s, 9, 2029, 0, 0);
                            """, (new_user_id,))
                            
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"🎉 Account successfully initialized for {new_first} {new_last} as a {new_role}!")
                    except Exception as e:
                        st.error(f"Failed to write record to database. (Email might already be taken): {str(e)}")
                        
    st.markdown("---")
    st.info("👈 Use the navigation pane on the left sidebar to access your live analytics dashboard or view the interactive student timeline engines.")
