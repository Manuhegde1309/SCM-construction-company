import streamlit as st
import mysql.connector
from database import create_connection

def add_product(product_id, product_name, product_price):
    # Ensure product_name is in uppercase
    product_name = product_name.upper()

    conn = create_connection()
    cursor = conn.cursor()

    # Get Supplier_Company_id from session state
    supplier_company_id = st.session_state.company_id

    try:
        # Insert product into Product_info table
        cursor.execute("""
            INSERT INTO Product_info (Product_id, Product_name, Product_price, Supplier_Company_id)
            VALUES (%s, %s, %s, %s)
        """, (product_id, product_name, product_price, supplier_company_id))
        
        conn.commit()
        st.success("Product added successfully!")
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

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

    # Supplier Company page: Add Product functionality
    st.subheader("Select Roles")
    role = st.selectbox("Role", ["Add Products", "Authorize Orders"])
    
    # Implement "Add Products" form
    if role == "Add Products":
        with st.form("Add_Products"):
            product_id = st.text_input("Product ID (Alphanumeric)")
            product_name = st.text_input("Product Name")
            product_price = st.number_input("Product Price", min_value=0.01)
            
            submit_button = st.form_submit_button(label="Add Product")
            
            if submit_button:
                add_product(product_id, product_name, product_price)
    # Implement "Authorize Orders" functionality
    elif role == "Authorize Orders":
        st.write("Authorize Orders Page")
