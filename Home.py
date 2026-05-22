import streamlit as st
import bcrypt
import psycopg2
from psycopg2.extras import RealDictCursor

# Page layout configuration
st.set_page_config(
    page_title="Uppseekers OS - Portal Gateway", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Connect to database via Streamlit Secrets
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

# Maintain user session states across all multi-page elements
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None

def login_form():
    st.title("Welcome to Uppseekers OS")
    st.subheader("Internal Student Success & Admissions Management Platform")
    
    with st.form("login_form_container"):
        # Explicitly strip out any white space from inputs
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
                # Case-insensitive query to find the email safely
                cur.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(%s) AND is_active = TRUE", (email,))
                user = cur.fetchone()
                cur.close()
                conn.close()
                
                if user:
                    # Pull password hash directly, clearing potential byte strings
                    db_hash = user['password_hash'].strip()
                    if isinstance(db_hash, str):
                        db_hash = db_hash.encode('utf-8')
                        
                    if bcrypt.checkpw(password.encode('utf-8'), db_hash):
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
                        st.error("Invalid password provided. Please try again.")
                else:
                    st.error("Account email not found in our database records.")
            except Exception as e:
                st.error(f"System Connection Error: {str(e)}")

def logout_user():
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.rerun()

# Execution Control
if not st.session_state.authenticated:
    login_form()
else:
    st.sidebar.markdown(f"### Signed in as:\n**{st.session_state.user_info['name']}**")
    st.sidebar.info(f"Access Privilege: {st.session_state.user_info['role']}")
    if st.sidebar.button("Sign Out from System"):
        logout_user()
    
    st.markdown("# System Main Gateway")
    st.markdown("---")
    st.info("Use the sidebar on the left to navigate between modules based on your access level permissions.")
