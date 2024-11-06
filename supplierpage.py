import streamlit as st
import mysql.connector
from database import create_connection
import pandas as pd


def get_order_info(company_id, company_type):
    conn = create_connection(st.session_state.sqluser,st.session_state.sqluserpassword)
    cursor=conn.cursor()
    if conn and cursor:
        try:
            cursor.callproc('get_order_info', [company_id, company_type])
            for result in cursor.stored_results():
                orders = result.fetchall()
                return orders
        except mysql.connector.Error as err:
            st.error(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()
    return []

def add_product(product_id, product_name, product_price):
    product_name = product_name.upper()

    conn = create_connection(st.session_state.sqluser,st.session_state.sqluserpassword)
    cursor = conn.cursor()

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
    conn = create_connection(st.session_state.sqluser,st.session_state.sqluserpassword)
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

    st.title(f"Welcome, {company_name}")
    st.write(f"This is the dashboard for Supply company {company_name} (ID: {st.session_state.company_id}).")

    role = st.selectbox("Select Action", ["Add Products", "Authorize Orders","Check transactions","Delete Product","Update Product","Products info"], key="supplier_role_selectbox")
    
    if role == "Add Products":
        st.header("Add Products Page")
        with st.form("Add_Products"):
            product_id = st.text_input("Product ID (Alphanumeric)", key="add_product_id")
            product_name = st.text_input("Product Name", key="add_product_name")
            product_price = st.number_input("Product Price",value=None, format="%.2f", key="add_product_price")
            
            if st.form_submit_button("Add Product"):
                if not product_id.isalnum():
                    st.error("Product ID must be alphanumeric.")
                elif product_price==None or product_price<=0:
                    st.error("Product price must be greater than 0")
                elif product_name=="":
                    st.error("Product name cannot be empty")
                else:
                    # Call function to add the product
                    add_product(product_id, product_name, product_price)


    elif role == "Authorize Orders":
        conn = create_connection(st.session_state.sqluser,st.session_state.sqluserpassword)
        cursor = conn.cursor()
        st.header("Authorize Orders Page")

        # Function to get pending orders for the logged-in supplier company
        def get_pending_orders():
            cursor.execute("""
                SELECT * FROM Order_info 
                WHERE Status = 'Pending' AND Supplier_Company_Id = %s
            """, (st.session_state.company_id,))
            data = cursor.fetchall()
            return data, cursor.column_names

        st.subheader("All Orders")
        order_table = st.empty()
        message_placeholder = st.empty()

        # Display pending orders
        data, columns = get_pending_orders()
        df = pd.DataFrame(data, columns=columns)
        df.index = range(1, len(df) + 1)
        if data:            
            order_table.write(df)
            order_ids = [order[0] for order in data]  # Assuming the first column is Order ID
            selected_order_id = st.selectbox("Select Order ID", order_ids, key="authorize_order_selectbox")
            add_status = st.selectbox("Add status", ["Accept", "Reject"], key="authorize_order_status")

            if add_status == "Accept":
                delivery_company = st.selectbox("Select Delivery Company", ["DHL Group", "Express Mail Service", "FedEx Corp", "TNT Express", "United Parcel Service"], key="authorize_delivery_company")
                submit_button = st.button("Deliver Order")
            else:
                submit_button = st.button("Reject Order")

            if submit_button:
                if add_status == "Accept":
                    # Check if the selected delivery company exists
                    cursor.execute("SELECT Shipment_Company_id FROM Shipment_Company WHERE Shipment_Company_name = %s", (delivery_company,))
                    shipment_company_id_result = cursor.fetchone()
                    shipment_company_id = shipment_company_id_result[0] if shipment_company_id_result else None

                    if not shipment_company_id:
                        message_placeholder.error(f"Delivery company {delivery_company} does not exist.")
                    else:
                        # Fetch order details
                        cursor.execute("""
                            SELECT o.Product_id, o.Quantity, o.Cost, o.Construction_Company_Id, p.Stock
                            FROM Order_info o
                            JOIN Product_info p ON o.Product_id = p.Product_id
                            WHERE o.Order_id = %s AND o.Status = 'Pending' AND o.Supplier_Company_Id = %s
                        """, (selected_order_id, st.session_state.company_id))
                        order_details = cursor.fetchone()

                        if order_details:
                            product_id, quantity, total_cost, construction_company_id, current_stock = order_details
                            
                            # Fetch the product name
                            cursor.execute("SELECT Product_name FROM Product_info WHERE Product_id = %s", (product_id,))
                            product_name = cursor.fetchone()[0]
                            
                            # Check cash balance
                            cursor.execute("SELECT Cash_Balance FROM Construction_Company WHERE Construction_Company_id = %s", (construction_company_id,))
                            cash_balance = cursor.fetchone()[0]

                            if cash_balance >= total_cost:
                                try:
                                    # Update the status of the order to Accepted and set Shipment_Company_Id
                                    cursor.execute("""
                                        UPDATE Order_info 
                                        SET Status = 'Accepted', Shipment_Company_Id = %s 
                                        WHERE Order_id = %s
                                    """, (shipment_company_id, selected_order_id))
                                    
                                    # Deduct the cost from Construction_Company's balance
                                    cursor.execute("""
                                        UPDATE Construction_Company 
                                        SET Cash_Balance = Cash_Balance - %s
                                        WHERE Construction_Company_id = %s
                                    """, (total_cost, construction_company_id))
                                    
                                    # Update Company_Inventory
                                    cursor.execute("""
                                        SELECT Quantity FROM Company_Inventory 
                                        WHERE Construction_Company_Id = %s AND Product_name = %s
                                    """, (construction_company_id, product_name))
                                    existing_quantity = cursor.fetchone()
                                    
                                    if existing_quantity:
                                        cursor.execute("""
                                            UPDATE Company_Inventory 
                                            SET Quantity = Quantity + %s 
                                            WHERE Construction_Company_Id = %s AND Product_name = %s
                                        """, (quantity, construction_company_id, product_name))
                                    else:
                                        cursor.execute("""
                                            INSERT INTO Company_Inventory (Construction_Company_Id, Product_name, Quantity) 
                                            VALUES (%s, %s, %s)
                                        """, (construction_company_id, product_name, quantity))
                                    
                                    conn.commit()
                                    st.success(f"Order {selected_order_id} has been delivered successfully!")
                                    
                                    # Refresh and display updated pending orders
                                    updated_data, updated_columns = get_pending_orders()
                                    updated_df = pd.DataFrame(updated_data, columns=updated_columns)
                                    order_table.subheader("Pending Orders List")
                                    order_table.write(updated_df)
                                    
                                except mysql.connector.Error as err:
                                    conn.rollback()
                                    st.error(f"Error processing order: {err}")
                            else:
                                st.error(f"Construction company with ID {construction_company_id} has insufficient balance.")
                        else:
                            st.error("Invalid Order ID or the order is not pending.")
                
                else:
                    try:
                        # Update the status of the order to Rejected
                        cursor.execute("""
                            UPDATE Order_info 
                            SET Status = 'Rejected' 
                            WHERE Order_id = %s AND Status = 'Pending'
                        """, (selected_order_id,))
                        conn.commit()
                        st.success(f"Order {selected_order_id} has been rejected successfully!")
                        
                        # Refresh and display updated pending orders
                        updated_data, updated_columns = get_pending_orders()
                        updated_df = pd.DataFrame(updated_data, columns=updated_columns)
                        order_table.subheader("Pending Orders List")
                        order_table.write(updated_df)
                        
                    except mysql.connector.Error as err:
                        conn.rollback()
                        st.error(f"Error processing order: {err}")
        else:
            st.warning("No pending orders for your company.")

        cursor.close()
        conn.close()

    
    elif role == "Delete Product":
        conn = create_connection(st.session_state.sqluser,st.session_state.sqluserpassword)
        cursor = conn.cursor()

        st.header("Delete Products page")

        # Function to get current products
        def get_current_products():
            cursor.execute("""
                SELECT Product_id, Product_name 
                FROM Product_info 
                WHERE Supplier_Company_id = %s
            """, (st.session_state.company_id,))
            products = cursor.fetchall()
            return pd.DataFrame(products, columns=["Product ID", "Product Name"])

        st.subheader("Current Products")
        product_table = st.empty()
        message_placeholder = st.empty()

        df = get_current_products()
        df.index = range(1, len(df) + 1)
        product_table.subheader("Current Products")
        product_table.write(df)

        if not df.empty:
            product_ids = df["Product ID"].tolist()  # Extract product IDs
            selected_product_id = st.selectbox("Select Product ID to delete:", product_ids)

            if st.button("Delete Product"):
                try:
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM Order_info 
                        WHERE Product_id = %s AND Status = 'Pending'
                        """, (selected_product_id,))
                    pending_orders_count = cursor.fetchone()[0]

                    if pending_orders_count > 0:
                        st.warning("Cannot delete this product as there are pending orders.")
                    
                    else:
                        # Temporarily disable foreign key checks
                        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

                        # Delete the selected product
                        cursor.execute("DELETE FROM Product_info WHERE Product_id = %s", (selected_product_id,))
                        conn.commit()

                        # Re-enable foreign key checks
                        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
                        
                        # Refresh and display the updated product list
                        updated_df = get_current_products()
                        updated_df.index = range(1, len(updated_df) + 1)
                        product_table.write(updated_df)

                        st.success(f"Product {selected_product_id} deleted successfully!")
                except mysql.connector.Error as err:
                    st.error(f"Error: {err}")
        else:
            st.warning("No products available for deletion.")

        cursor.close()
        conn.close()


    elif role == "Update Product":
        st.header("Update Product page")
        conn = create_connection(st.session_state.sqluser,st.session_state.sqluserpassword)
        cursor = conn.cursor()
        
        # Function to get current products
        def get_current_products():
            cursor.execute("""
                SELECT Product_id, Product_name, Product_price 
                FROM Product_info 
                WHERE Supplier_Company_id = %s
            """, (st.session_state.company_id,))
            products = cursor.fetchall()
            return pd.DataFrame(products, columns=["Product ID", "Product Name", "Product Price"])

        st.subheader("Current Products")
        product_table = st.empty()
        
        df = get_current_products()
        df.index = range(1, len(df) + 1)
        
        product_table.write(df)

        product_options = df["Product ID"].tolist()
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

            new_product_price = st.number_input("New Product Price", value=float(current_product_price), format="%.2f", key="new_product_price")
            
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
                    if new_product_price <= 0:
                        st.error("Product price must be greater than 1.")
                    else:
                        try:
                            if new_product_id and new_product_price >= 1:
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
                            
                            updated_df = get_current_products()
                            product_table.subheader("Current Products")
                            product_table.write(updated_df)
                            
                            st.success("Product updated successfully!")
                        except mysql.connector.Error as err:
                            st.error(f"Error: {err}")
        else:
            st.warn("Product ID not found or does not belong to your company.")
        
        cursor.close()
        conn.close()

    elif role=="Check transactions":
        conn = create_connection(st.session_state.sqluser,st.session_state.sqluserpassword)
        cursor = conn.cursor()
        orders=get_order_info(st.session_state.company_id,'SUPPLIER')
        if orders:
            columns = ["Order_id", "Product_id", "Construction_Company_Id", "Supplier_Company_Id", 
                    "Shipment", "Quantity", "Cost", "Status"]
                        
            df = pd.DataFrame(orders, columns=columns)            
            df.index=range(1,len(df)+1)
            
            st.header("Company Transaction history page ")
            st.write(df)
        else:
            st.warning("No Orders found.")
        
        cursor.close()
        conn.close()

    elif role=="Products info":
        st.header("Products info page")
        st.subheader("All Products")
        conn = create_connection(st.session_state.sqluser,st.session_state.sqluserpassword)
        cursor = conn.cursor()
        
        # Function to get current products
        def get_current_products():
            cursor.execute("""
                SELECT Product_id, Product_name, Product_price, Stock
                FROM Product_info 
                WHERE Supplier_Company_id = %s
            """, (st.session_state.company_id,))
            products = cursor.fetchall()
            return pd.DataFrame(products, columns=["Product ID", "Product Name", "Product Price","Stock"])
        df = get_current_products()
        df.index = range(1, len(df) + 1)
        if df.empty:
            st.warning("No products added for this company.")
        else:
            st.write(df)
