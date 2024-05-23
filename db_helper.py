import mysql.connector
cnx = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Prusshita@1234",
            database="ecommerce_data"
        )

def get_total_order_price(order_id):
    try:
        cursor = cnx.cursor()
        query = """
                SELECT SUM(item_id.price) 
                FROM orders 
                JOIN item_id ON orders.id = item_id.id 
                WHERE orders.order_id = %s
                """
        cursor.execute(query, (order_id,))
        result = cursor.fetchone()[0]  
        cursor.close()

        return result if result is not None else 0 
    except mysql.connector.Error as err:
        print("MySQL Error:", err)
        return None


      
def insert_order_tracking(order_id , status):
    cursor = cnx.cursor()
    insert_query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"
    cursor.execute(insert_query, (order_id, status))
    cnx.commit()
    cursor.close()

def insert_order_item(id, size, order_id):
    try:
        cursor = cnx.cursor()
        insert_query = "INSERT INTO orders (id, size, order_id) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (id, size, order_id))
        cnx.commit()
        cursor.close()
        print("Order item inserted successfully")
        return 1
    except mysql.connector.Error as err:
        print(f"Error in inserting item: {err}")
        cnx.rollback()
        return -1 
    except Exception as e:
        print(f"An error occurred: {e}")
        cnx.rollback()
        return -1 

def get_next_order_id():
    cursor = cnx.cursor()
    query = "SELECT MAX(order_id) from orders"
    cursor.execute(query)
    result = cursor.fetchone()[0]
    cursor.close()
    if result is None:
        return 1
    else:
        return result+1
def get_order_status(order_id: int):
    try:
        
        cursor = cnx.cursor()
        query = "SELECT status FROM order_tracking WHERE order_id = %s"
        cursor.execute(query, (order_id,))
        result = cursor.fetchone()
        cursor.close()

        if result is not None:
            return result[0]
        else:
            return None
    except mysql.connector.Error as err:
        print("MySQL Error:", err)
        return None