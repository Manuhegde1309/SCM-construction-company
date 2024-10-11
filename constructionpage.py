import streamlit as st
from database import create_connection

def construction_company_page():
    conn = create_connection()
    cursor = conn.cursor()

    # Fetch the company name using the company_id stored in session state
    cursor.execute("""
        SELECT Construction_Company_name 
        FROM Construction_Company 
        WHERE Construction_Company_id = %s
    """, (st.session_state.company_id,))

    result = cursor.fetchone()
    company_name = result[0] if result else "Unknown Company"

    cursor.close()
    conn.close()

    # Display the company name and other details
    st.title(f"Welcome, {company_name}")
    st.write(f"This is the dashboard for Construction company {company_name} (ID: {st.session_state.company_id}).")    
    
    # Construction Company page must be implemented here
