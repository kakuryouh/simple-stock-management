import matplotlib.pyplot as plt
import mysql.connector
from datetime import datetime
import pandas as pd
import numpy as np

#Functions to manipulate database

def Show_ALL_Tables():
    Show_All_Table = """SHOW TABLES"""
    curA.execute(Show_All_Table)
    Tables = curA.fetchall()

    for table in Tables:
        print(table[0])

def Show_All_Product_type():
    Show_Type = """SELECT Type FROM Products unique"""
    curA.execute(Show_Type)
    Types = curA.fetchall()

    for Type in Types:
        print(Type[0], " ")

#FUnctions to insert new product
def Insert_New_Product():
    New_Product_Name = input("\nEnter New Product Name = ")
    New_Product_Quantity = int(input("Enter New Product QUantity = "))
    New_Product_Price = int(input("Enter New Product Price = "))
    New_Product_Type = input("Enter NewProduct Type (", Show_All_Product_type, ") = ")

    NEW_ITEM = (New_Product_Name, New_Product_Quantity, New_Product_Price, New_Product_Type)

    insert_new_item = """INSERT INTO products(Product_Name, Quantity, Product_Price, Type) Values(%s. %s, %s, %s)"""
    
    curA.execute(insert_new_item, NEW_ITEM)

    query_last_products = """SELECT * from products ORDER BY ID DESC LIMIT 1"""

    curA.execute(query_last_products)
    print(curA.fetchall())

    check = input("\nis this correct? (y/n) = ")

    if len(check) == 1 and check.lower() == "y":
        cnx.commit()
        print("\nsuccesfully inserted\n")
    else:
        cnx.rollback()
        print("\ntransaction canceled\n")

#functions to show all data in a table
def Show_table(Table_name):

    query = f"SELECT * FROM {Table_name}"

    curA.execute(query)
    rows = curA.fetchall()

    match Table_name:
        case "products":
            if rows:
                print("\nproducts Data:\n")

                for row in rows:
                    print(f"ID:{row[0]}, Product Name:{row[1]}, Quantity:{row[2]}, Product Price:{row[3]}, Product Type{row[4]}")
            
            else:
                print("\nNo Data was received\n")

        case "transaction":
            if rows:
                print("\ntransaction Data:\n")

                for row in rows:
                    print(f"Transaction ID:{row[0]}, Transaction Date:{row[1]}, Total Amount:{row[2]}")
                
            else:
                print("\nNo Data was received\n")
        
        case "transactiondetails":
            if rows:
                print("\nTransaction Details Data:\n")

                for row in rows:
                    print(f"Detail ID:{row[0]}, Transaction ID:{row[1]}, Product ID:{row[2]}, Product Name:{row[3]}, QUantity:{row[4]}, Price:{row[5]}")
            
            else:
                print("\nNo Data was received\n")
        
        case _:
            print(f"\nTable {Table_name} Doesn't Exist\n")
            

#Delete data from products
def Delete_product():
    
    flag = Show_table("products")
    if flag == False:
        return

    ID = input("\nID of Product to delete: ")

    query_by_ID = f"SELECT * from products where ID = {ID}"

    curA.execute(query_by_ID)
    print(curA.fetchall())
    check = input("is this correct? (y/n) = ")

    if len(check) == 1 and check == 'y':
        delete_item = f"DELETE FROM products WHERE ID = {ID}"
        curA.execute(delete_item)
        cnx.commit()
        print("succesfully Deleted\n")

#Edit info from products table (CANNOT EDIT PRODUCT NAME)
def Edit_products_info():
    
    flag = Show_table("products")
    if flag == False:
        return

    ID = input("ID of Product to Edit: ")

    query_by_ID = f"SELECT * from products where ID = {ID}"

    curA.execute(query_by_ID)
    print(curA.fetchall())
    check = input("is this correct? (y/n) = ")

    if len(check) == 1 and check == 'y':
        New_Item_Quantity = int(input("Enter New Quantity for the Item : "))
        New_Item_Price = int(input("Enter New Price for the Item: "))
        New_Item_Values = (New_Item_Quantity, New_Item_Price)

        Edit_item = f"UPDATE products SET Quantity = (%s), Product_Price = (%s) where ID = {ID}"
        curA.execute(Edit_item, New_Item_Values)
        cnx.commit()
        print("succesfully Changed\n")

def get_product_name(productID):
    get_name = f"SELECT Product_Name from products where ID = {productID}"
    curA.execute(get_name)
    result = curA.fetchone()

    if result:
        return result[0]
    else:
        return None

def get_product_price(productID):
    get_price = f"SELECT Product_Price from products where ID = {productID}"
    curA.execute(get_price)
    result = curA.fetchone()

    if result:
        return result[0]
    else:
        return None

def Input_products_for_transaction():
    Products = []

    while True:
        productID = input("Enter Product ID (or type 'done' to finish): ")
        if productID.lower() == "done":
            break
        else:
            productID = int(productID)

            quantity = int(input("Enter Quantity: "))

            price = get_product_price(productID)

            name = get_product_name(productID)

            if price is not None:
                Products.append({
                    'ProductID' : productID,
                    'ProductName' : name,
                    'Quantity' : quantity,
                    'Price' : price
                })

                print(f"Added product {productID} {name} (Quantity: {quantity}, Price: {price})")
            else:
                print(f"Product ID {productID} Not found in database")
    return Products

def New_Transactions():
    insert_new_transaction = """INSERT INTO transaction (TransactionDate, Total_Amount) VALUES(%s, %s)"""
    insert_transation_detail = """INSERT INTO transactiondetails (TransactionID, ProductID, ProductName, Quantity, Price) values(%s, %s, %s, %s, %s)"""
    
    #Get the list of products for a transactions
    Show_table("products")
    print("\n")
    Products = Input_products_for_transaction()
    
    #Add new transactions
    date = get_current_date()
    Total_Amount = sum([Product['Quantity'] * Product['Price'] for Product in Products])
    curA.execute(insert_new_transaction, (date, Total_Amount))

    transactionID = curA.lastrowid

    #Insert New transaction details and update the stocks in products
    for product in Products:
        curA.execute(insert_transation_detail, (transactionID, product['ProductID'], product['ProductName'], product['Quantity'], product['Price']))
    
        update_stocks = """Update products SET Quantity = Quantity - %s WHERE ID = %s"""
        curA.execute(update_stocks, (product['Quantity'], product['ProductID']))
    
    cnx.commit()
    print("transaction was successful.")

def get_current_date():
    Today_date = datetime.now().strftime('%Y-%m-%d')

    return Today_date

def Today_Transaction():
    date = get_current_date()
    Total_sales_today = f"SELECT Total_Amount FROM transaction WHERE TransactionDate = '{date}'"

    curA.execute(Total_sales_today)
    Total = curA.fetchall()
    sum = 0

    for Totals in Total:
        sum = sum + Totals[0]
    
    return sum

def sales_from_7_days():
    Sales7 = """
            SELECT TransactionDate as sale_date, SUM(Total_Amount) as total_sales
            FROM transaction
            WHERE TransactionDate >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY sale_date
            ORDER BY sale_date ASC;
            """

    curA.execute(Sales7)
    result = curA.fetchall()

    # Convert result to DataFrame
    df = pd.DataFrame(result, columns=['sale_date', 'total_sales'])
    df['sale_date'] = pd.to_datetime(df['sale_date']).dt.date
    print(df)
    return df

def Top_5_Types(date):
    Top5 = f"SELECT p.Type as product_type, SUM(td.Quantity) as total_sold FROM transactiondetails td JOIN products p ON td.ProductID = p.ID JOIN transaction t ON td.TransactionID = t.TransactionID WHERE t.TransactionDate = '{date}' GROUP BY product_type ORDER BY total_sold DESC LIMIT 5;"
            
    curA.execute(Top5)
    result = curA.fetchall()

    # Convert result to DataFrame
    df = pd.DataFrame(result, columns=['product_type', 'total_sold'])
    print(df)
    return df

def plot_sales_last_7_days():
    df = sales_from_7_days()
    
    if df is not None and not df.empty:
        # Plot
        plt.figure(figsize=(10, 5))
        plt.bar(df['sale_date'], df['total_sales'], color='lightcoral')
        plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.DayLocator())
        plt.title("Total Sales for the Last 7 Days")
        plt.xlabel("Date")
        plt.ylabel("Total Sales")
        plt.show()
    else:
        print("No sales data available for the last 7 days.\n")

def plot_top_5_product_types(date):
    df = Top_5_Types(date)
    
    if df is not None and not df.empty:
        # Plot
        labels = [f'{product_type} ({quantity})' for product_type, quantity in zip(df['product_type'], df['total_sold'])]

        plt.figure(figsize=(7, 7))
        plt.pie(df['total_sold'], labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title(f"Top 5 Product Types Sold on {date}")
        plt.show()
    else:
        print(f"No data available for {date}.\n")

def Main_Menu():

    pointer = 0
    Sales = Today_Transaction()

    while(pointer != 7):
        print("\nWelcome\n")
        print("1. Insert New products\n")
        print("2. Show Table\n")
        print("3. Delete Products from table\n")
        print("4. Edit Products info\n")
        print("5. Add New Transactions\n")
        print("6. Sales Analytics\n")
        print("7. Exit\n")

        print("\nToday Sales : Rp.", Sales, "\n")

        pointer = int(input("Choose [1-7] : "))

        if pointer == 1:
            Insert_New_Product()

        elif pointer == 2:
            Show_ALL_Tables()
            
            Table_name = input("Pick Table to Show: ")

            Show_table(Table_name)

        elif pointer == 3:
            Delete_product()

        elif pointer == 4:
            Edit_products_info()

        elif pointer == 5:
            New_Transactions()
            Sales = Today_Transaction()
        
        elif pointer == 6:
            choice = 0

            print("1. Last 7 Days Sales Comparison\n")
            print("2. Top 5 Item Type Sold\n")

            choice = int(input("Choose [1-2] = "))

            if choice == 1:
                plot_sales_last_7_days()
            
            elif choice == 2:
                date = input("Enter the date (YYYY-MM-DD): ")
                plot_top_5_product_types(date)
        
        elif pointer == 7:
            check = input("Are you sure? {y/n) : ")
            if len(check) == 1 and check == "y":
                print("Shutting Down...")
                
            else:
                pointer = 0
                print("\n")
        
        else: print("Invalid COmmand\n")

#Connections to DBMS, change when using a different DB connections
cnx = mysql.connector.connect(user = 'root', password = '', host = '127.0.0.1', database = 'inventory')

#Cursors to use DBMS
if cnx.is_connected():
    print("Connected to MySQL\n")
    curA = cnx.cursor()

    Main_Menu()
    curA.close()
    cnx.close()

else:
    print("Error Cannot connect to ")