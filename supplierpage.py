import streamlit as st
import mysql.connector
from database import create_connection
import pandas as pd
import random
import uuid

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

    # Supplier Company page: Add Product and Authorize Orders functionality
    st.subheader("Select Roles")
    role = st.selectbox("Role", ["Add Products", "Authorize Orders","Check transactions","Delete Product","Update Product"], key="supplier_role_selectbox")
    
    # Implement "Add Products" functionality
    if role == "Add Products":
        with st.form("Add_Products"):
            product_id = st.text_input("Product ID (Alphanumeric)", key="add_product_id")
            product_name = st.text_input("Product Name", key="add_product_name")
            product_price = st.number_input("Product Price", min_value=0.01, format="%.2f", key="add_product_price")
            
            if st.form_submit_button("Add Product"):
                # Validate product_id is alphanumeric
                if not product_id.isalnum():
                    st.error("Product ID must be alphanumeric.")
                else:
                    # Call function to add the product
                    add_product(product_id, product_name, product_price)

    elif role == "Authorize Orders":
        conn = create_connection()
        cursor = conn.cursor()
        st.write("Authorize Orders Page")

        # Show only pending orders for the logged-in supplier company
        cursor.execute("""
            SELECT * FROM Order_info 
            WHERE Status = 'Pending' AND Supplier_Company_Id = %s
        """, (st.session_state.company_id,))

        data = cursor.fetchall()
        columns = cursor.column_names
        df = pd.DataFrame(data, columns=columns)
        st.subheader("Pending Orders List")
        st.dataframe(df)

        st.write("Authorize an order")
        
        # Order ID input
        order_id = st.text_input("ID of the Order", key="authorize_order_id")
        add_status = st.selectbox("Add status", ["Accept", "Reject"], key="authorize_order_status")

        if add_status == "Accept":
            delivery_company = st.selectbox("Select Delivery Company", ["DHL Group", "FedEx Corp"], key="authorize_delivery_company")
            submit_button = st.button("Deliver Order")
        else:  # Reject
            submit_button = st.button("Reject Order")

        if submit_button:
            if add_status == "Accept":
                # Check if the selected delivery company exists
                cursor.execute("SELECT Shipment_Company_id FROM Shipment_Company WHERE Shipment_Company_name = %s", (delivery_company,))
                shipment_company_id_result = cursor.fetchone()
                shipment_company_id = shipment_company_id_result[0] if shipment_company_id_result else None

                if not shipment_company_id:
                    st.error(f"Delivery company {delivery_company} does not exist.")
                else:
                    # Fetch order details
                    cursor.execute("""
                        SELECT Product_id, Quantity, Cost, Construction_Company_Id
                        FROM Order_info 
                        WHERE Order_id = %s AND Status = 'Pending' AND Supplier_Company_Id = %s
                    """, (order_id, st.session_state.company_id))
                    order_details = cursor.fetchone()

                    if order_details:
                        product_id, quantity, total_cost, construction_company_id = order_details
                        
                        # Fetch the product name
                        cursor.execute("SELECT Product_name FROM Product_info WHERE Product_id = %s", (product_id,))
                        product_name = cursor.fetchone()[0]
                        
                        # Fetch the construction company name
                        cursor.execute("SELECT Construction_Company_name FROM Construction_Company WHERE Construction_Company_id = %s", (construction_company_id,))
                        company_name = cursor.fetchone()[0]
                        
                        # Check cash balance
                        cursor.execute("SELECT Cash_Balance FROM Construction_Company WHERE Construction_Company_id = %s", (construction_company_id,))
                        cash_balance = cursor.fetchone()[0]

                        if cash_balance >= total_cost:
                            # Deduct the cost from Construction_Company's balance
                            cursor.execute("""
                                UPDATE Construction_Company 
                                SET Cash_Balance = Cash_Balance - %s
                                WHERE Construction_Company_id = %s
                            """, (total_cost, construction_company_id))
                            
                            # Check if the product exists in the inventory of the construction company
                            cursor.execute("""
                                SELECT Quantity FROM Company_Inventory 
                                WHERE Construction_Company_name = %s AND Product_name = %s
                            """, (company_name, product_name))
                            existing_quantity = cursor.fetchone()
                            
                            if existing_quantity:
                                # Update the quantity if the product already exists
                                cursor.execute("""
                                    UPDATE Company_Inventory 
                                    SET Quantity = Quantity + %s 
                                    WHERE Construction_Company_name = %s AND Product_name = %s
                                """, (quantity, company_name, product_name))
                            else:
                                # Insert a new record into Company_Inventory
                                cursor.execute("""
                                    INSERT INTO Company_Inventory (Construction_Company_name, Product_name, Quantity) 
                                    VALUES (%s, %s, %s)
                                """, (company_name, product_name, quantity))
                            
                            # Update the status of the order to Accepted and set Shipment_Company_Id
                            cursor.execute("""
                                UPDATE Order_info 
                                SET Status = 'Accepted', Shipment_Company_Id = %s 
                                WHERE Order_id = %s
                            """, (shipment_company_id, order_id))
                            
                            conn.commit()
                            st.success(f"Order {order_id} has been delivered successfully!")
                        else:
                            st.error(f"Construction company {company_name} has insufficient balance.")
                    else:
                        st.error("Invalid Order ID or the order is not pending.")
            else:  # Reject
                # Update the status of the order to Rejected
                cursor.execute("""
                    UPDATE Order_info 
                    SET Status = 'Rejected' 
                    WHERE Order_id = %s AND Status = 'Pending'
                """, (order_id,))
                conn.commit()
                st.success(f"Order {order_id} has been rejected successfully!")
    
    elif role == "Delete Product":
        conn = create_connection()
        cursor = conn.cursor()

        # Fetch products belonging to the current supplier company
        cursor.execute("""
            SELECT Product_id, Product_name 
            FROM Product_info 
            WHERE Supplier_Company_id = %s
        """, (st.session_state.company_id,))

        products = cursor.fetchall()

        # If there are products, display them in a selectbox
        if products:
            product_ids = [product[0] for product in products]  # Extract product_ids
            selected_product_id = st.selectbox("Select Product ID to delete:", product_ids)

            if st.button("Delete Product"):
                try:
                    # Temporarily disable foreign key checks
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

                    # Proceed to delete the product
                    cursor.execute("DELETE FROM Product_info WHERE Product_id = %s", (selected_product_id,))
                    conn.commit()
                    st.success(f"Product {selected_product_id} deleted successfully!")
                    
                    # Re-enable foreign key checks
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
                except mysql.connector.Error as err:
                    st.error(f"Error: {err}")
        else:
            st.info("No products available for deletion.")

        cursor.close()
        conn.close()

    elif role == "Update Product":
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT Product_id, Product_name, Product_price 
            FROM Product_info 
            WHERE Supplier_Company_id = %s
        """, (st.session_state.company_id,))
        
        products = cursor.fetchall()
        df = pd.DataFrame(products, columns=["Product ID", "Product Name", "Product Price"])
        st.subheader("Current Products")
        st.dataframe(df)

        product_options = [product[0] for product in products]  # Extract product IDs for selectbox
        selected_product_id = st.selectbox("Select the Product ID to Update:", product_options, key="update_product_selectbox")

        cursor.execute("""
            SELECT Product_name, Product_price 
            FROM Product_info 
            WHERE Product_id = %s AND Supplier_Company_id = %s
        """, (selected_product_id, st.session_state.company_id))
        
        product_details = cursor.fetchone()

        if product_details:
            current_product_name, current_product_price = product_details
            
            new_product_id = st.text_input("New Product ID (Leave blank to keep current)", value=selected_product_id, key="new_product_id")

            new_product_price = st.number_input("New Product Price", value=float(current_product_price), min_value=0.01, format="%.2f", key="new_product_price")

            cursor.execute("""
                SELECT COUNT(*) 
                FROM Order_info 
                WHERE Product_id = %s AND Status = 'Pending'
            """, (selected_product_id,))
            pending_orders_count = cursor.fetchone()[0]

            if pending_orders_count > 0:
                st.warning("Cannot update this product as there are pending orders.")
            else:
                if st.button("Update Product"):
                    try:
                        if new_product_id:
                            cursor.execute("""
                                UPDATE Product_info 
                                SET Product_id = %s, Product_price = %s 
                                WHERE Product_id = %s AND Supplier_Company_id = %s
                            """, (new_product_id, new_product_price, selected_product_id, st.session_state.company_id))
                        else:
                            cursor.execute("""
                                UPDATE Product_info 
                                SET Product_price = %s 
                                WHERE Product_id = %s AND Supplier_Company_id = %s
                            """, (new_product_price, selected_product_id, st.session_state.company_id))
                        
                        conn.commit()
                        st.success("Product updated successfully!")
                    except mysql.connector.Error as err:
                        st.error(f"Error: {err}")
        else:
            st.error("Product ID not found or does not belong to your company.")
        
        cursor.close()
        conn.close()