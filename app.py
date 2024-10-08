# implemented login and sign up features

import os
import streamlit as st
import mysql.connector
import argon2
from argon2 import PasswordHasher
from dotenv import load_dotenv

load_dotenv()

# Initialize the Argon2 password hasher
ph = PasswordHasher()

# Database connection function
def create_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv('db_password'),
        database="dbms_project_testing"
    )
    return connection

# Create required tables
def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    # Create Admin Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Admin (
            Admin_id VARCHAR(50) PRIMARY KEY,
            Firstname VARCHAR(50) NOT NULL,
            Middlename VARCHAR(50),
            Lastname VARCHAR(50) NOT NULL,
            Password VARCHAR(255) NOT NULL
        )
    """)

    # Create Construction_Company Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Construction_Company (
            Construction_Company_id VARCHAR(50) PRIMARY KEY,
            Construction_Company_name VARCHAR(100) NOT NULL UNIQUE,
            Cash_Balance DECIMAL(20, 2) DEFAULT 10000000,
            Admin_id VARCHAR(50),
            FOREIGN KEY (Admin_id) REFERENCES Admin(Admin_id)
        )
    """)

    # Create Supplier_Company Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Supplier_Company (
            Supplier_Company_id VARCHAR(50) PRIMARY KEY,
            Supplier_Company_name VARCHAR(100) NOT NULL UNIQUE,
            Password VARCHAR(255) NOT NULL
        )
    """)

    # Create Shipment_Company Table
    cursor.execute("""  
        CREATE TABLE IF NOT EXISTS Shipment_Company (
            Shipment_Company_id VARCHAR(50) PRIMARY KEY,
            Supplier_Company_name VARCHAR(100) NOT NULL UNIQUE
        )
    """)

    # Insert 2 shipment companies by default
    shipment_companies = [
        ("DHL", "DHL Group"),
        ("FDX", "FedEx Corp")   
    ]

    for shipment_id, company_name in shipment_companies:
        cursor.execute("""
            INSERT INTO Shipment_Company (Shipment_Company_id, Supplier_Company_name)
            SELECT %s, %s
            WHERE NOT EXISTS (SELECT 1 FROM Shipment_Company WHERE Shipment_Company_id = %s)
        """, (shipment_id, company_name, shipment_id) )

    cursor.execute("""  
        CREATE TABLE IF NOT EXISTS Product_info (
            Product_id VARCHAR(50) PRIMARY KEY,
            Product_name VARCHAR(100) NOT NULL UNIQUE
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()

# Password hashing and verification functions
def hash_password(password):
    return ph.hash(password)

def check_password(password, hashed):
    try:
        return ph.verify(hashed, password)
    except argon2.exceptions.VerifyMismatchError:
        return False

# Company name existence check functions
def company_exists(company_name, company_type):
    conn = create_connection()
    cursor = conn.cursor()

    table_name = "Construction_Company" if company_type == "Construction" else "Supplier_Company"
    column_name = "Construction_Company_name" if company_type == "Construction" else "Supplier_Company_name"
    cursor.execute(f"SELECT 1 FROM {table_name} WHERE LOWER({column_name}) = LOWER(%s)", (company_name,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result is not None

# Signup functions
def signup_admin(firstname, middlename, lastname, password, company_name, admin_id, company_id):
    if company_exists(company_name, "Construction"):
        st.error("Construction company with this name already exists.")
        return False

    conn = create_connection()
    cursor = conn.cursor()

    hashed_password = hash_password(password)

    try:
        cursor.execute("INSERT INTO Admin (Admin_id, Firstname, Middlename, Lastname, Password) VALUES (%s, %s, %s, %s, %s)", 
                       (admin_id, firstname, middlename, lastname, hashed_password))

        cursor.execute("INSERT INTO Construction_Company (Construction_Company_id, Construction_Company_name, Admin_id) VALUES (%s, %s, %s)", 
                       (company_id, company_name, admin_id))
        
        conn.commit()
        st.success("Admin and Construction Company signed up successfully!")
        return True
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def signup_supplier(company_name, company_id, password):
    if company_exists(company_name, "Supplier"):
        st.error("Supplier company with this name already exists.")
        return False

    conn = create_connection()
    cursor = conn.cursor()

    hashed_password = hash_password(password)

    try:
        cursor.execute("INSERT INTO Supplier_Company (Supplier_Company_id, Supplier_Company_name, Password) VALUES (%s, %s, %s)", 
                       (company_id, company_name, hashed_password))
        
        conn.commit()
        st.success("Supplier Company signed up successfully!")
        return True
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

# Modified login function
def login_user(company_id, password, role, admin_id=None):
    conn = create_connection()
    cursor = conn.cursor()

    if role == "Construction Company":
        cursor.execute("""
            SELECT A.Password FROM Admin A 
            JOIN Construction_Company C ON A.Admin_id = C.Admin_id
            WHERE C.Construction_Company_id = %s AND A.Admin_id = %s
        """, (company_id, admin_id))
    else:
        cursor.execute("SELECT Password FROM Supplier_Company WHERE Supplier_Company_id = %s", (company_id,))
    
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result and check_password(password, result[0]):
        return True
    return False

# Page functions
def login_signup_page():
    st.title("Login / Signup")
    
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
                    if admin_id.isalnum() and company_id.isalnum():
                        if signup_admin(firstname, middlename, lastname, password, company_name, admin_id, company_id):
                            st.session_state.logged_in = True
                            st.session_state.user_role = "Construction Company"
                            st.session_state.company_id = company_id
                            st.rerun()
                    else:
                        st.error("Admin ID and Company ID must be alphanumeric")
        else:
            with st.form("signup_supplier"):
                company_name = st.text_input("Supplier Company Name")
                company_id = st.text_input("Supplier Company ID (Alphanumeric)")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Sign Up"):
                    if company_id.isalnum():
                        if signup_supplier(company_name, company_id, password):
                            st.session_state.logged_in = True
                            st.session_state.user_role = "Supplier Company"
                            st.session_state.company_id = company_id
                            st.rerun()
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
                            st.rerun()
                        else:
                            st.error("Invalid credentials")
                    else:
                        st.error("Supplier ID must be alphanumeric")

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

def supplier_company_page():
    conn = create_connection()
    cursor = conn.cursor()

    # Fetch the supplier company name using the company_id stored in session state
    cursor.execute("""
        SELECT Supplier_Company_name 
        FROM Supplier_Company 
        WHERE Supplier_Company_id = %s
    """, (st.session_state.company_id,))

    result = cursor.fetchone()
    company_name = result[0] if result else "Unknown Supplier Company"

    cursor.close()
    conn.close()

    # Display the company name and other details
    st.title(f"Welcome, {company_name}")
    st.write(f"This is the dashboard for Supply company {company_name} (ID: {st.session_state.company_id}).")

    # Supplier Company page must be implemented here
    st.subheader("Select Roles")
    role = st.selectbox("Role", ["Add Products", "Authorize Orders"])
    


def main():
    create_tables()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

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
            st.rerun()

if __name__ == "__main__":
    main()