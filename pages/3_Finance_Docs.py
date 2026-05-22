import streamlit as st
import psycopg2

st.set_page_config(page_title="Financials & Documents", layout="wide")

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

st.title("💰 Financial Ledgers & Application Document Vaults")
st.markdown("---")

conn = get_db_connection()
cur = conn.cursor()

# LOAD ACTIVE PROFILES MATRIX FOR FINANCIAL ANALYSIS
cur.execute("""
    SELECT u.id, u.first_name || ' ' || u.last_name AS name, p.contracted_fee_usd, p.outstanding_balance_usd 
    FROM student_profiles p JOIN users u ON p.user_id = u.id
""")
financial_records = cur.fetchall()

if not financial_records:
    st.info("No active student transaction logs currently tracked.")
    st.stop()

col_f1, col_f2 = st.columns([1, 2])

with col_f1:
    st.subheader("💵 Fee Management Engine")
    selected_fin_id = st.selectbox("Select Account Ledger", options=[f['id'] for f in financial_records], format_func=lambda x: next(f['name'] for f in financial_records if f['id']==x))
    
    current_record = next(f for f in financial_records if f['id'] == selected_fin_id)
    st.metric("Total Corporate Contracted Fee Value", f"${current_record['contracted_fee_usd']:,.2f}")
    st.metric("Outstanding Accounts Receivable Balance Due", f"${current_record['outstanding_balance_usd']:,.2f}", delta="- Remaining Invoice")
    
    with st.form("payment_update_ledger"):
        payment_received = st.number_input("Process Payment Installment ($)", min_value=0, step=100)
        process_payment = st.form_submit_button("Post Transaction Settlement")
        
        if process_payment and payment_received > 0:
            new_balance = max(0, float(current_record['outstanding_balance_usd']) - float(payment_received))
            try:
                cur.execute("""
                    UPDATE student_profiles SET outstanding_balance_usd = %s WHERE user_id = %s;
                """, (new_balance, selected_fin_id))
                conn.commit()
                st.success(f"Payment posted successfully! New Outstanding Balance: ${new_balance:,.2f}")
                st.rerun()
            except Exception as e:
                st.error(f"Ledger reconciliation failed: {e}")

with col_f2:
    st.subheader("📁 Central Secure Admissions Asset Repository")
    st.markdown("Upload transcripts, standard scoresheets, or portfolio essays directly to the secure tracking layer.")
    
    uploaded_file = st.file_uploader("Upload Core Admission Asset (PDF, DOCX, PNG)", type=['pdf', 'docx', 'png', 'jpg'])
    doc_tag = st.selectbox("Document Classification Tag Category", ["Transcript Transcript", "Letter of Recommendation (LOR)", "Statement of Purpose (SOP)", "Resume / Activity CV", "Passport Identity"])
    
    upload_submit = st.button("Commit Asset File to Vault")
    if upload_submit:
        if uploaded_file is not None:
            try:
                cur.execute("""
                    INSERT INTO documents (student_id, file_name, storage_url, is_latest)
                    VALUES (%s, %s, %s, TRUE);
                """, (selected_fin_id, uploaded_file.name, f"vault://{doc_tag.lower().replace(' ', '_')}/{uploaded_file.name}"))
                conn.commit()
                st.success(f"🎉 Secure asset metadata record for '{uploaded_file.name}' compiled inside structural layer successfully!")
            except Exception as e:
                st.error(f"Asset vault registration failed: {e}")
                
    st.markdown("#### Document Logs & Asset Verification Checklist:")
    cur.execute("SELECT * FROM documents WHERE student_id = %s", (selected_fin_id,))
    vault_docs = cur.fetchall()
    
    if vault_docs:
        for doc in vault_docs:
            st.text(f"📄 {doc['file_name']} | Path: {doc['storage_url']}")
    else:
        st.caption("No structural application documents uploaded to this client profile yet.")

cur.close()
conn.close()
