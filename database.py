import os
import mysql.connector

def create_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv('db_password'),
        database=os.getenv('database')
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
            Shipment_Company_name VARCHAR(100) NOT NULL UNIQUE
        )
    """)

    # Insert 2 shipment companies by default
    shipment_companies = [
        ("DHL", "DHL Group"),
        ("FDX", "FedEx Corp")
    ]

    for shipment_id, company_name in shipment_companies:
        cursor.execute("""
            INSERT INTO Shipment_Company (Shipment_Company_id, Shipment_Company_name)
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

    # Order_info table with Shipment_Company_Id column
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Order_info (
            Order_id VARCHAR(50) PRIMARY KEY,
            Product_id VARCHAR(50),
            Construction_Company_Id VARCHAR(50),
            Supplier_Company_Id VARCHAR(50),
            Shipment_Company_Id VARCHAR(50) DEFAULT NULL,
            Quantity INT NOT NULL,
            Cost DECIMAL(10, 2),
            Status ENUM('Pending', 'Accepted', 'Rejected') DEFAULT 'Pending',
            FOREIGN KEY (Product_id) REFERENCES Product_info(Product_id),
            FOREIGN KEY (Construction_Company_Id) REFERENCES Construction_Company(Construction_Company_id),
            FOREIGN KEY (Supplier_Company_Id) REFERENCES Supplier_Company(Supplier_Company_id),
            FOREIGN KEY (Shipment_Company_Id) REFERENCES Shipment_Company(Shipment_Company_id)
        )
    """)

    # Company_Inventory table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Company_Inventory (
            Inventory_id INT AUTO_INCREMENT PRIMARY KEY,
            Construction_Company_name VARCHAR(100) NOT NULL,
            Product_name VARCHAR(100) NOT NULL,
            Quantity INT NOT NULL
        )
    """)
    #procedure creation
    cursor.execute("""
                drop procedure if exists get_order_info;
            """)
    cursor.execute("""
                create procedure get_order_info(
                    IN in_company_id VARCHAR(50),
                    IN company_type ENUM('CONSTRUCTION', 'SUPPLIER')
                )
                BEGIN
                    if company_type = 'CONSTRUCTION' THEN
                        SELECT * FROM Order_info WHERE Construction_Company_Id = in_company_id;
                    elseif company_type = 'SUPPLIER' THEN
                        SELECT * FROM Order_info WHERE Supplier_Company_Id = in_company_id;
                    end if;
                end
            """)
    conn.commit()
    cursor.close()
    conn.close()