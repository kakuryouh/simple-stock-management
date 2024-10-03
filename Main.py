import matplotlib
import mysql.connector

#Functions to manipulate database

def Show_ALL_Tables():
    Show_All_Table = """SHOW TABLES"""
    curA.execute(Show_All_Table)
    Tables = curA.fetchall()

    for table in Tables:
        print(table[0])

#FUnctions to insert new product
def Insert_New_Product():
    New_Product_Name = input("\nEnter New Product Name = ")
    New_Product_Quantity = int(input("Enter New_Product_QUantity = "))
    New_Product_Price = int(input("Enter New_Product_Price = "))

    NEW_ITEM = (New_Product_Name, New_Product_Quantity, New_Product_Price)

    insert_new_item = """INSERT INTO products(Product_Name, Quantity, Product_Price) Values(%s. %s, %s)"""
    
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
                    print(f"ID:{row[0]}, Product_Name:{row[1]}, Quantity:{row[2]}, Product_Price:{row[3]}")
            
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
    insert_new_transaction = """INSERT INTO transaction (TransactionDate, Total_Amount) VALUES(NOW(), %s)"""
    insert_transation_detail = """INSERT INTO transactiondetails (TransactionID, ProductID, ProductName, Quantity, Price) values(%s, %s, %s, %s, %s)"""
    
    #Get the list of products for a transactions
    Show_table("products")
    print("\n")
    Products = Input_products_for_transaction()
    
    #Add new transactions
    Total_Amount = sum([Product['Quantity'] * Product['Price'] for Product in Products])
    curA.execute(insert_new_transaction, (Total_Amount,))

    transactionID = curA.lastrowid

    #Insert New transaction details and update the stocks in products
    for product in Products:
        curA.execute(insert_transation_detail, (transactionID, product['ProductID'], product['ProductName'], product['Quantity'], product['Price']))
    
        update_stocks = """Update products SET Quantity = Quantity - %s WHERE ID = %s"""
        curA.execute(update_stocks, (product['Quantity'], product['ProductID']))
    
    cnx.commit()
    print("transaction was successful.")

#Connections to DBMS, change when using a different DB connections
cnx = mysql.connector.connect(user = 'root', password = '', host = '127.0.0.1', database = 'inventory')

#Cursors to use DBMS
if cnx.is_connected():
    print("COnnected to MySQL\n")

curA = cnx.cursor()

pointer = 0

while(pointer != 6):
    print("\nWelcome\n")
    print("1. Insert New products\n")
    print("2. Show Table\n")
    print("3. Delete Products from table\n")
    print("4. Edit Products info\n")
    print("5. Add New Transactions\n")
    print("6. Exit\n")

    pointer = int(input("Choose [1-6] : "))

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
    
    elif pointer == 6:
        check = input("Are you sure? {y/n) : ")
        if len(check) == 1 and check == "y":
            print("Shutting Down...")
            
        else:
            pointer = 0
            print("\n")
    
    else: print("Invalid COmmand\n")

curA.close()
cnx.close()