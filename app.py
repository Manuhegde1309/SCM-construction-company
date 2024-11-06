from streamlit_autorefresh import st_autorefresh
import streamlit as st
from dotenv import load_dotenv
from database import create_tables
from authorization import login_user, signup_admin, signup_supplier
from constructionpage import construction_company_page
from supplierpage import supplier_company_page

# Load environment variables
load_dotenv()

def login_signup_page():
    sqluserchoice = st.text_input("Select SQL user to run (root/other user)")
    sqluserpassword = st.text_input("password")
    st.header("Login / Signup")
    choice = st.radio("Select Action", ["Login", "Signup"])

    if choice == "Signup":
        st.subheader("Create an Account")
        role = st.selectbox("Role", ["Construction Company", "Supplier Company"])

        if role == "Construction Company":
            with st.form("signup_construction"):
                company_name = st.text_input("Construction Company Name")
                company_id = st.text_input("Construction Company ID (Alphanumeric)")
                firstname = st.text_input("Admin First Name")
                middlename = st.text_input("Admin Middle Name (Optional)")
                lastname = st.text_input("Admin Last Name")
                admin_id = st.text_input("Admin ID (Alphanumeric)")
                password = st.text_input("Password", type="password")
                
                if st.form_submit_button("Sign Up"):
                    if not all([company_name, company_id, firstname, lastname, admin_id, password]):
                        st.error("Please fill out all the fields")
                    elif admin_id.isalnum() and company_id.isalnum():
                        if signup_admin(firstname, middlename, lastname, password, company_name, admin_id, company_id):
                            st.session_state.logged_in = True
                            st.session_state.user_role = "Construction Company"
                            st.session_state.company_id = company_id
                            st.session_state.sqluser = sqluserchoice
                            st.session_state.sqluserpassword = sqluserpassword
                            st.rerun()
                        else:
                            st.error("Signup failed")
                    else:
                        st.error("Admin ID and Company ID must be alphanumeric")
        else:
            with st.form("signup_supplier"):
                company_name = st.text_input("Supplier Company Name")
                company_id = st.text_input("Supplier Company ID (Alphanumeric)")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Sign Up"):
                    if not all([company_name, company_id, password]):
                        st.error("Please fill out all the fields")
                    elif company_id.isalnum():
                        if signup_supplier(company_name, company_id, password):
                            st.session_state.logged_in = True
                            st.session_state.user_role = "Supplier Company"
                            st.session_state.company_id = company_id
                            st.session_state.sqluser = sqluserchoice
                            st.session_state.sqluserpassword = sqluserpassword
                            st.rerun()
                        else:
                            st.error("Signup failed")
                    else:
                        st.error("Company ID must be alphanumeric")
            
    elif choice == "Login":
        st.subheader("Login to Your Account")
        role = st.selectbox("Role", ["Construction Company", "Supplier Company"])
        with st.form("login"):
            if role == "Construction Company":
                company_id = st.text_input("Construction Company ID (Alphanumeric)")
                admin_id = st.text_input("Admin ID (Alphanumeric)")
                password = st.text_input("Password", type="password")
                
                if st.form_submit_button("Login"):
                    if company_id.isalnum() and admin_id.isalnum():
                        if login_user(company_id, password, role, admin_id):
                            st.session_state.logged_in = True
                            st.session_state.user_role = role
                            st.session_state.company_id = company_id
                            st.session_state.sqluser = sqluserchoice
                            st.session_state.sqluserpassword = sqluserpassword
                            st.rerun()
                        else:
                            st.error("Invalid credentials")
                    else:
                        st.error("Company ID and Admin ID must be alphanumeric")
            else:
                company_id = st.text_input("Supplier Company ID (Alphanumeric)")
                password = st.text_input("Password", type="password")
                
                if st.form_submit_button("Login"):
                    if company_id.isalnum():
                        if login_user(company_id, password, role):
                            st.session_state.logged_in = True
                            st.session_state.user_role = role
                            st.session_state.company_id = company_id
                            st.session_state.sqluser = sqluserchoice
                            st.session_state.sqluserpassword = sqluserpassword
                            st.rerun()
                        else:
                            st.error("Invalid credentials")
                    else:
                        st.error("Supplier ID must be alphanumeric")
    
def main():
    count = st_autorefresh(interval=5000)
    
    # Initialize session state variables if they don't exist
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_role" not in st.session_state:
        st.session_state.user_role = None
    if "company_id" not in st.session_state:
        st.session_state.company_id = None
    if "sqluser" not in st.session_state:
        st.session_state.sqluser = None
    if "sqluserpassword" not in st.session_state:
        st.session_state.sqluserpassword = None

    if st.session_state.sqluser=="root":
        create_tables(st.session_state.sqluser,st.session_state.sqluserpassword)
        
    if not st.session_state.logged_in:
        login_signup_page()
    else:
        if st.session_state.user_role == "Construction Company":
            construction_company_page()
        elif st.session_state.user_role == "Supplier Company":
            supplier_company_page()
        
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.session_state.company_id = None
            st.session_state.sqluser = None
            st.session_state.sqluserpassword = None
            st.rerun()
if __name__ == "__main__":
    main()
