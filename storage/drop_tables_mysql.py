import mysql.connector

db_conn = mysql.connector.connect(
            host="acit3855-lab6a.eastus.cloudapp.azure.com", 
            user="events",
            password="evts", 
            database="events"
        )


db_cursor = db_conn.cursor()

db_cursor.execute('''
                    DROP TABLE temperature, air_pressure
                ''')

db_conn.commit()
db_conn.close()
