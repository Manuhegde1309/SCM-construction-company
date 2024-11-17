import uuid
import streamlit as st
from database import create_connection
import pandas as pd
import mysql.connector

def get_order_info(company_id, company_type):
    conn = create_connection(st.session_state.sqluser,st.session_state.sqluserpassword)
    cursor = conn.cursor()
    if conn and cursor:
        try:
            # Call stored procedure to get order information
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

def construction_company_page():
    conn = create_connection(st.session_state.sqluser,st.session_state.sqluserpassword)
    cursor = conn.cursor()

    # Fetch company name for the session's company_id
    cursor.execute("""
        SELECT Construction_Company_name 
        FROM Construction_Company 
        WHERE Construction_Company_id = %s
    """, (st.session_state.company_id,))
    result = cursor.fetchone()
    company_name = result[0] if result else "Unknown Company"

    cursor.close()
    conn.close()

    st.title(f"Welcome, {company_name}")
    st.write(f"This is the dashboard for Construction company {company_name} (ID: {st.session_state.company_id}).")

    choice = st.selectbox(
        "Select Action", 
        ["Add money/balance", "Place Orders", "Check Inventory", "Delete from inventory", "Check transactions"], 
        key="construction_company_actions"
    )

    if choice == "Add money/balance":
        st.header("Add money/balance")

        def get_current_balance():
            conn = create_connection(st.session_state.sqluser,st.session_state.sqluserpassword)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Cash_Balance FROM Construction_Company WHERE Construction_Company_id = %s", 
                (st.session_state.company_id,)
            )
            balance = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return balance

        balance_display = st.empty()
        current_balance = get_current_balance()
        balance_display.subheader(f"Current Cash Balance: {current_balance}")

        with st.form('add_money_form'):
            money = st.number_input("Enter amount to add", key="add_money", value=None)
            submitted = st.form_submit_button("Add money/balance")

            if submitted:
                if money == None or money <= 0:
                    st.error("Please enter an amount greater than 1 to add.")
                else:
                    conn = create_connection(st.session_state.sqluser,st.session_state.sqluserpassword)
                    cursor = conn.cursor()
                    try:
                        # Update cash balance in Construction_Company
                        cursor.execute("""
                            UPDATE Construction_Company 
                            SET Cash_Balance = Cash_Balance + %s 
                            WHERE Construction_Company_id = %s
                        """, (money, st.session_state.company_id))
                        conn.commit()

                        new_balance = get_current_balance()
                        balance_display.subheader(f"Current Cash Balance: {new_balance}")
                        st.success("Money added successfully!")
                    except Exception as e:
                        st.error(f"Error updating balance: {e}")
                    finally:
                        cursor.close()
                        conn.close()

    elif choice == "Place Orders":
        conn = create_connection(st.session_state.sqluser,st.session_state.sqluserpassword)
        cursor = conn.cursor()

        # Fetch product information excluding the "Stock" column
        cursor.execute("""
            SELECT Product_id, Product_name, Product_price, Supplier_Company_id FROM Product_info
        """)
        data = cursor.fetchall()
        columns = ["Product_id", "Product_name", "Product_price", "Supplier_Company_id"]
        df = pd.DataFrame(data, columns=columns)

        df.index = range(1, len(df) + 1)
        df.index.name = "Sl"
        st.subheader("Product list")
        st.dataframe(df)

        st.header("Place an order")
        with st.form("Place orders"):
            product_id = st.selectbox("Id of the Product", key="order_product_id", options=df["Product_id"])
            Quantity = st.number_input("Quantity", key="order_quantity", value=None)

            if st.form_submit_button("Place Orders"):
                if Quantity is None or Quantity <= 0:
                    st.error("Please enter a positive quantity.")
                else:
                    query = """
                        WITH ProductDetails AS (
                            SELECT 
                                Supplier_Company_id,
                                Product_price
                            FROM Product_info
                            WHERE Product_id = %s
                        ),
                        OrderDetails AS (
                            SELECT 
                                (pd.Product_price * %s) AS total_price,
                                cc.Cash_Balance
                            FROM ProductDetails pd
                            JOIN Construction_Company cc ON cc.Construction_Company_id = %s
                        )
                        SELECT 
                            pd.Supplier_Company_id,
                            od.total_price,
                            od.Cash_Balance
                        FROM ProductDetails pd, OrderDetails od
                    """
                    cursor.execute(query, (product_id, Quantity, st.session_state.company_id))
                    result = cursor.fetchone()

                    if result:
                        supply_company_id, t_price, cash_balance = result

                        if cash_balance > t_price:
                            orderId = "OR" + str(uuid.uuid4().hex[:4])
                            # Insert new order information into Order_info
                            cursor.execute("""
                                INSERT INTO Order_info(Order_id, Product_id, Construction_Company_Id, Supplier_Company_Id, Quantity, Cost) 
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (orderId, product_id, st.session_state.company_id, supply_company_id, Quantity, t_price))
                            conn.commit()
                            st.success("Order made successfully")
                        else:
                            st.error("Insufficient balance")
                    else:
                        st.error("Error fetching product or balance details")

        cursor.close()
        conn.close()

    elif choice == "Check Inventory":
        conn = create_connection(st.session_state.sqluser,st.session_state.sqluserpassword)
        cursor = conn.cursor()
        
        # Fetch inventory for the current construction company
        cursor.execute("""
            SELECT Product_name, Quantity 
            FROM Company_Inventory 
            WHERE Construction_Company_Id = %s
        """, (st.session_state.company_id,)) 
        data = cursor.fetchall()
        columns = ["Product Name", "Quantity"]
        df = pd.DataFrame(data, columns=columns)
        df.index = range(1, len(df) + 1)
        df.index.name = "Sl"

        cursor.close()
        conn.close()

        if not df.empty:
            st.header("Company Inventory")
            st.dataframe(df)
        else:
            st.warning("No products in inventory for this company.")

    elif choice == "Delete from inventory":
        conn = create_connection(st.session_state.sqluser,st.session_state.sqluserpassword)
        cursor = conn.cursor()

        def get_current_inventory():
            cursor.execute("""
                SELECT Product_name, Quantity 
                FROM Company_Inventory 
                WHERE Construction_Company_Id = %s
            """, (st.session_state.company_id,))
            result = cursor.fetchall()
            columns = ["Product_name", "Quantity"]
            return pd.DataFrame(result, columns=columns)

        st.subheader("Company Inventory")
        inventory_display = st.empty()

        df = get_current_inventory()
        df.index = range(1, len(df) + 1)
        df.index.name = "Sl"

        if not df.empty:
            inventory_display.dataframe(df)
            st.header("Delete from Inventory")
            with st.form("remove from inventory"):
                product_name = st.selectbox("Select product to remove/delete", options=df["Product_name"])
                quantity_to_remove = st.number_input("Enter remove quantity", key="remove_quantity", value=None)

                if st.form_submit_button("Submit"):
                    if quantity_to_remove == None or quantity_to_remove <= 0:
                        st.error("Please enter a quantity greater than 1 to remove.")
                    else:
                        try:
                            # Update inventory quantity for selected product
                            cursor.execute("""
                                UPDATE Company_Inventory 
                                SET Quantity = Quantity - %s 
                                WHERE Construction_Company_Id = %s AND Product_name = %s
                            """, (quantity_to_remove, st.session_state.company_id, product_name))

                            # Delete product from inventory if quantity is zero or less
                            cursor.execute("""
                                DELETE FROM Company_Inventory 
                                WHERE Construction_Company_Id = %s AND Product_name = %s AND Quantity <= 0
                            """, (st.session_state.company_id, product_name))
                            conn.commit()

                            updated_df = get_current_inventory()
                            inventory_display.dataframe(updated_df)
                            st.success("Inventory updated successfully!")
                        except Exception as e:
                            st.error(f"Error updating inventory: {e}")
        else:
            st.warning("No products in inventory for this company.")

        cursor.close()
        conn.close()

    elif choice == "Check transactions":
        conn = create_connection(st.session_state.sqluser,st.session_state.sqluserpassword)
        cursor = conn.cursor()

        # Retrieve order information for the construction company
        orders = get_order_info(st.session_state.company_id, 'CONSTRUCTION')

        if orders:
            columns = ["Order_id", "Product_id", "Construction_Company_Id", "Supplier_Company_Id", 
                    "Shipment", "Quantity", "Cost", "Status"]
            df = pd.DataFrame(orders, columns=columns)
            df.index = range(1, len(df) + 1)
            st.header("Company Transaction History")
            st.write(df)
        else:
            st.warning("No Orders found.")

        cursor.close()
        conn.close()
