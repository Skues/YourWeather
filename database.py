import mysql.connector
import os

# db = mysql.connector.connect(
#     host="localhost",
#     user="buzio",
#     password="password",
#     database="WeatherWebsite"
# )


class databaseConnection:
    def __init__(self):
        self.db = self.connectDatabase()

    def connectDatabase(self):
        try:
            db = mysql.connector.connect(
                host="localhost",
                user=os.environ.get("MYSQL_USER"),
                password=os.environ.get("MYSQL_PASSWORD"),
                database=os.environ.get("MYSQL_DB"),
            )
            return db
        except Exception as e:
            raise (e)
            exit

    def insertValues(self, table, columns, values):
        columnText = ""
        valueText = ""
        columnText += f"{columns[0]}"
        valueText += f"'{values[0]}'"
        if len(columns) != len(values):
            return "Length of columns and values not equal."
        for i in range(1, len(columns)):
            columnText += f", {columns[i]}"
            valueText += f", '{values[i]}'"
        print(columnText)
        print(valueText)
        sql = f"INSERT INTO {table} ({columnText}) VALUES ({valueText})"
        print(sql)
        self.db.cursor().execute(sql)
        self.db.commit()

    def selectWhere(self, table, column, value):
        sql = f"SELECT FROM {table} WHERE {column} = '{value}'"
        self.db.cursor().execute(sql)
        self.db.commit()

    def showTable(self, cursor, table):
        sql = f"SELECT * FROM {table}"
        cursor.execute(sql)
        result = cursor.fetchall()
        print(result)

    def deleteID(self, table, id):
        sql = f"DELETE FROM {table} WHERE id = {id}"
        self.db.cursor().execute(sql)
        self.db.commit()
        return False

    def deleteAll(self, table):
        sql = f"DELETE FROM {table}"
        self.db.cursor().execute(sql)
        self.db.commit()
        return False


# mycursor = db.cursor()
# # mycursor.execute("ALTER TABLE users add column id INT auto_increment primary key")
# print(db)
