import uuid
import streamlit as st
from database import create_connection
import pandas as pd
import random

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
    choice = st.selectbox("Select Action", ["Add money/balance", "Place Orders", "Check Inventory","Delete from inventory","Check transactions"], key="construction_company_actions")  # Added unique key
    if choice == "Add money/balance":
        conn = create_connection()
        cursor = conn.cursor()
        with st.form('Construction company page'):
            money = st.number_input("money", min_value=1, key="construction_add_money")
            if st.form_submit_button("Add money/balance"):
                cursor.execute("""
                UPDATE Construction_Company SET Cash_Balance = Cash_Balance + %s WHERE Construction_Company_id = %s
                """, (money, st.session_state.company_id))
                conn.commit()
                st.success("Money added successfully!")
    elif choice=="Place Orders":
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM Product_info
        """)
        data = cursor.fetchall()
        columns = cursor.column_names
        df = pd.DataFrame(data, columns=columns)
        st.subheader("Product list")
        st.dataframe(df)
        st.write("Place an order")
        with st.form("Place orders"):
            product_id = st.selectbox("Id of the Product", key="order_product_id",options=df["Product_id"])
            Quantity = st.number_input("Quantity", min_value=1, key="order_quantity")
            if st.form_submit_button("Place Orders"):
                cursor.execute("""
                SELECT Supplier_Company_id FROM Product_info WHERE Product_id = %s
                """, (product_id,))
                placeholder = cursor.fetchone()
                supply_company_id = placeholder[0] if placeholder else "none"
                cursor.execute("""
                    SELECT (Product_price * %s) AS total_price FROM Product_info WHERE Product_id = %s AND Supplier_Company_id = %s
                """, (Quantity, product_id, supply_company_id))
                price = cursor.fetchone()
                t_price = price[0] if price is not None else 0
                cursor.execute("""
                    SELECT Cash_Balance FROM Construction_Company WHERE Construction_Company_id = %s
                """, (st.session_state.company_id,))
                minprice = cursor.fetchone()
                if minprice[0] > t_price:
                    orderId = "OR" + str(uuid.uuid4().hex[:4])
                    cursor.execute("""
                        INSERT INTO Order_info(Order_id, Product_id, Construction_Company_Id, Supplier_Company_Id, Quantity, Cost) 
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (orderId, product_id, st.session_state.company_id, supply_company_id, Quantity, t_price))
                    conn.commit()
                    st.success("Order made successfully")
                else:
                    st.error("Insufficient balance")
    elif choice=="Check Inventory":
        conn = create_connection()
        cursor = conn.cursor()
        
        # Fetch inventory for the construction company
        cursor.execute("""
            SELECT Product_name, Quantity 
            FROM Company_Inventory 
            WHERE Construction_Company_name = %s
        """, (company_name,))
        
        data = cursor.fetchall()
        columns = ["Product Name", "Quantity"]  # Define the columns for the DataFrame
        df = pd.DataFrame(data, columns=columns)
        
        cursor.close()
        conn.close()

        # Check if there are any products in inventory
        if not df.empty:
            st.subheader("Inventory")
            st.dataframe(df)
        else:
            st.warning("No products in inventory for this company.")
    
    elif choice=="Delete from inventory":
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
        select * from Company_Inventory where Construction_Company_Name=(SELECT Construction_Company_name 
        FROM Construction_Company 
        WHERE Construction_Company_id = %s)
        """,(st.session_state.company_id,))
        
        result=cursor.fetchall()
        columns = cursor.column_names
        df = pd.DataFrame(result, columns=columns)
        st.dataframe(df)
        with st.form("remove from inventory"):
            inventory_id=st.selectbox("select product to remove/delete",options=df["Inventory_id"])
            quantity=st.number_input("how many to remove?",min_value=1)
            if st.form_submit_button("submit"):
                update_query = """
                UPDATE Company_Inventory AS outer_ci
                JOIN (
                SELECT Inventory_id, Quantity - %s AS new_quantity
                FROM Company_Inventory
                WHERE Inventory_id = %s
                ) AS subquery
                ON outer_ci.inventory_id = subquery.inventory_id
                SET outer_ci.quantity = subquery.new_quantity
                WHERE outer_ci.inventory_id = %s;
                """
                cursor.execute(update_query, (quantity, inventory_id, inventory_id))
                cursor.execute("""delete from Company_Inventory where Inventory_id=%s and Quantity<=0""",(inventory_id,))
                conn.commit()
                st.success("inventory updated")
        
    elif choice=="Check transactions":
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
        select * from Order_info where Construction_Company_Id=%s
        """,(st.session_state.company_id,))
        result=cursor.fetchall()
        columns = cursor.column_names
        df = pd.DataFrame(result, columns=columns)
        st.write("Orders from this company")
        st.dataframe(df)
        
    cursor.close()
    conn.close()