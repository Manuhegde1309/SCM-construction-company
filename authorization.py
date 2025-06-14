import mysql.connector
import argon2
from argon2 import PasswordHasher
from database import create_connection
import streamlit as st
ph = PasswordHasher()

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

# Login functions
def login_user(company_id, password, role, admin_id=None):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        if role == "Construction Company":
            cursor.execute("SELECT Password FROM Admin WHERE Admin_id = %s", (admin_id,))
            result = cursor.fetchone()
            if result and check_password(password, result[0]):
                return True
        else:
            cursor.execute("SELECT Password FROM Supplier_Company WHERE Supplier_Company_id = %s", (company_id,))
            result = cursor.fetchone()
            if result and check_password(password, result[0]):
                return True
        return False
    finally:
        cursor.close()
        conn.close()
