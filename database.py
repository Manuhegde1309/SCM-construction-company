import os
import mysql.connector

def create_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv('db_password'),
        database="dbms_project_testing"
    )
    return connection

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
        """, (shipment_id, company_name, shipment_id))

    # Product_info table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Product_info (
            Product_id VARCHAR(50) PRIMARY KEY,
            Product_name VARCHAR(100) NOT NULL,
            Product_price DECIMAL(10, 2) NOT NULL,
            Supplier_Company_id VARCHAR(50),      
            FOREIGN KEY (Supplier_Company_id) REFERENCES Supplier_Company(Supplier_Company_id)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
