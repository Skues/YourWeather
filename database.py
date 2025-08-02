import mysql.connector
import os

# db = mysql.connector.connect(
#     host="localhost",
#     user="buzio",
#     password="password",
#     database="WeatherWebsite"
# )

def connectDatabase():
    try:
        db = mysql.connector.connect(
        host="localhost",
        user=os.environ.get("MYSQL_USER"),
        password=os.environ.get("MYSQL_PASSWORD"),
        database=os.environ.get("MYSQL_DB")
        )
        return db
    except Exception as e:
        raise(e)
def insertValues(db, table, columns, values):
    columnText = ""
    valueText = ""
    columnText += f"{columns[0]}"
    valueText += f"'{values[0]}'"
    if len(columns) != len(values):
        return "Length of columns and values not equal."
    for i in  range(1, len(columns)):
        columnText += f", {columns[i]}"
        valueText += f", '{values[i]}'"
    print(columnText)
    print(valueText)
    sql = f"INSERT INTO {table} ({columnText}) VALUES ({valueText})"
    print(sql)
    db.cursor().execute(sql)
    db.commit()
    
def selectWhere(db, table, column, value):
    sql = f"SELECT FROM {table} WHERE {column} = '{value}'"
    db.cursor.execute(sql)
    db.commit()

def showTable(cursor, table):
    sql = f"SELECT * FROM {table}"
    cursor.execute(sql)
    result = cursor.fetchall()
    print(result)

    
def deleteID(db, table, id):
    sql = f"DELETE FROM {table} WHERE id = {id}"
    db.cursor().execute(sql)
    db.commit()
    return False

def deleteAll(db, table):
    sql = f"DELETE FROM {table}"
    db.cursor().execute(sql)
    db.commit()
    return False
# mycursor = db.cursor()
# # mycursor.execute("ALTER TABLE users add column id INT auto_increment primary key")
# print(db)   
