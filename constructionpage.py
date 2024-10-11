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

    # Display the company name and other details
    st.title(f"Welcome, {company_name}")
    st.write(f"This is the dashboard for Construction company {company_name} (ID: {st.session_state.company_id}).")    
    
    choice = st.radio("Select Action", ["Add money/balance", "Place Orders"])
    if choice=="Add money/balance":
        with st.form('Construction company page'):
            money= st.number_input("money", min_value=10000)
            if st.form_submit_button("Add money/balance"):
                cursor.execute("""
                update construction_company set Cash_Balance=Cash_balance+%s where Construction_Company_id=%s
                """,(money,st.session_state.company_id)
                )
                conn.commit()
                st.success("money added successfully!")
    else:
        cursor.execute("""
        select * from product_info
       """)
        data=cursor.fetchall()
        columns=cursor.column_names
        df=pd.DataFrame(data, columns=columns)
        st.subheader("Product list")
        st.dataframe(df)
        st.write("place an order")
        with st.form("Place orders"):
            #product_id=st.multiselect("Id of the Product",df["Product_id"])
            #this is for single type of product only.For multiple types,it is under development
            product_id=st.text_input("Id of the Product")
            Quantity=st.number_input("Quantity", min_value=1)
            supply_company_id=st.text_input("SupplyCompanyId (Alphanumeric)")
            if st.form_submit_button("Place Orders"):
                cursor.execute("""
                    select (Product_price*%s) as total_price from product_info where product_id=%s and supplier_company_id=%s
                """,(Quantity,product_id,supply_company_id))
                price=cursor.fetchone()
                t_price=price[0] if price is not None else 0
                cursor.execute("""
                    select Cash_Balance from Construction_company where Construction_company_id=%s
                """,(st.session_state.company_id,))
                minprice=cursor.fetchone()
                if(minprice[0]>t_price):
                    orderId="OR"+str(uuid.uuid4().hex[:4])
                    cursor.execute("""
                        insert into order_info(Order_id,Product_Id,Construction_Company_Id,Supplier_Company_Id,Quantity,Cost) values(%s,%s,%s,%s,%s,%s)
                    """,(orderId,product_id,st.session_state.company_id,supply_company_id,Quantity,t_price)
                    )
                    conn.commit()
                    st.success("order made successfully")
                else:
                    st.error("insufficient balance")
    cursor.close()
    conn.close()
