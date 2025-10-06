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
        sql = "INSERT INTO %s (%s) VALUES (%s)"
        print(sql)
        self.db.cursor().execute(sql, (table, columnText, valueText))
        self.db.commit()

    def selectWhere(self, table, column, value):
        sql = "SELECT FROM %s WHERE %s = '%s'"
        self.db.cursor().execute(sql, (table, column, value))
        self.db.commit()

    def showTable(self, cursor, table):
        sql = "SELECT * FROM %s"
        cursor.execute(sql, (table))
        result = cursor.fetchall()
        print(result)

    def deleteID(self, table, id):
        sql = "DELETE FROM %s WHERE id = %s"
        self.db.cursor().execute(sql, (table, id))
        self.db.commit()
        return False

    def deleteAll(self, table):
        sql = "DELETE FROM %s"
        self.db.cursor().execute(sql, (table))
        self.db.commit()
        return False


# mycursor = db.cursor()
# # mycursor.execute("ALTER TABLE users add column id INT auto_increment primary key")
# print(db)
