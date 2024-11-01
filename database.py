import os
import mysql.connector

def create_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv('db_password'),
        database="dbms_project_testing1"
    )
    return connection

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    # Admin Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Admin (
            Admin_id VARCHAR(50) PRIMARY KEY,
            Firstname VARCHAR(50) NOT NULL,
            Middlename VARCHAR(50),
            Lastname VARCHAR(50) NOT NULL,
            Password VARCHAR(255) NOT NULL
        )
    """)

    # Construction_Company Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Construction_Company (
            Construction_Company_id VARCHAR(50) PRIMARY KEY,
            Construction_Company_name VARCHAR(100) NOT NULL UNIQUE,
            Cash_Balance DECIMAL(20, 2) DEFAULT 10000000,
            Admin_id VARCHAR(50),
            FOREIGN KEY (Admin_id) REFERENCES Admin(Admin_id)
        )
    """)

    # Supplier_Company Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Supplier_Company (
            Supplier_Company_id VARCHAR(50) PRIMARY KEY,
            Supplier_Company_name VARCHAR(100) NOT NULL UNIQUE,
            Password VARCHAR(255) NOT NULL
        )
    """)

    # Shipment_Company Table
    cursor.execute("""  
        CREATE TABLE IF NOT EXISTS Shipment_Company (
            Shipment_Company_id VARCHAR(50) PRIMARY KEY,
            Shipment_Company_name VARCHAR(100) NOT NULL UNIQUE
        )
    """)

    # 5 Shipment companies by default
    shipment_companies = [
    ("DHL", "DHL Group"),
    ("EMS", "Express Mail Service"),
    ("FDX", "FedEx Corp"),
    ("TNT", "TNT Express"),
    ("UPS", "United Parcel Service")
]

    for shipment_id, company_name in shipment_companies:
        cursor.execute("""
            INSERT INTO Shipment_Company (Shipment_Company_id, Shipment_Company_name)
            SELECT %s, %s
            WHERE NOT EXISTS (SELECT 1 FROM Shipment_Company WHERE Shipment_Company_id = %s)
        """, (shipment_id, company_name, shipment_id))

    # Product_info Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Product_info (
            Product_id VARCHAR(50) PRIMARY KEY,
            Product_name VARCHAR(100) NOT NULL,
            Product_price DECIMAL(12, 2) NOT NULL,
            Supplier_Company_id VARCHAR(50),
            Stock INT DEFAULT 10000,
            FOREIGN KEY (Supplier_Company_id) REFERENCES Supplier_Company(Supplier_Company_id)
        )
    """)

    # Order_info Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Order_info (
            Order_id VARCHAR(50) PRIMARY KEY,
            Product_id VARCHAR(50),
            Construction_Company_Id VARCHAR(50),
            Supplier_Company_Id VARCHAR(50),
            Shipment_Company_Id VARCHAR(50) DEFAULT NULL,
            Quantity INT NOT NULL,
            Cost DECIMAL(12, 2),
            Status ENUM('Pending', 'Accepted', 'Rejected') DEFAULT 'Pending',
            FOREIGN KEY (Product_id) REFERENCES Product_info(Product_id),
            FOREIGN KEY (Construction_Company_Id) REFERENCES Construction_Company(Construction_Company_id),
            FOREIGN KEY (Supplier_Company_Id) REFERENCES Supplier_Company(Supplier_Company_id),
            FOREIGN KEY (Shipment_Company_Id) REFERENCES Shipment_Company(Shipment_Company_id)
        )
    """)

    # Company_Inventory Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Company_Inventory (
            Construction_Company_Id VARCHAR(50) NOT NULL,
            Product_name VARCHAR(100) NOT NULL,
            Quantity INT NOT NULL,
            FOREIGN KEY (Construction_Company_Id) REFERENCES Construction_Company(Construction_Company_id)
        )
    """)
    
    # Procedure for Order info
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
    
    # Trigger for Stock update
    cursor.execute("""
        DROP TRIGGER IF EXISTS update_stock_on_order_accept;
    """)
    cursor.execute("""
        CREATE TRIGGER update_stock_on_order_accept
        AFTER UPDATE ON Order_info
        FOR EACH ROW
        BEGIN
            DECLARE current_stock INT;

            IF NEW.Status = 'Accepted' THEN
                -- Check current stock
                SELECT Stock INTO current_stock
                FROM Product_info
                WHERE Product_id = NEW.Product_id;

                -- Restock if necessary
                IF current_stock < NEW.Quantity THEN
                    UPDATE Product_info
                    SET Stock = current_stock + (NEW.Quantity * 2)
                    WHERE Product_id = NEW.Product_id;
                END IF;

                -- Deduct the ordered quantity from stock
                UPDATE Product_info
                SET Stock = Stock - NEW.Quantity
                WHERE Product_id = NEW.Product_id;
            END IF;
        END;
    """)

    conn.commit()
    cursor.close()
    conn.close()
