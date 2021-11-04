import mysql.connector

db_conn = mysql.connector.connect(
            host="acit3855-lab6a.eastus.cloudapp.azure.com", 
            user="your_username",
            password="your_password", 
            database="your_database"
        )

db_cursor = db_conn.cursor()

db_cursor.execute('''
          CREATE TABLE temperature
          (id INT NOT NULL AUTO_INCREMENT, 
           sensor_id VARCHAR(250) NOT NULL,
           coordinates VARCHAR(250) NOT NULL,
           low VARCHAR(250) NOT NULL,
           intermediate VARCHAR(250) NOT NULL,
           high VARCHAR(250) NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT temperature_pk PRIMARY KEY (id))
          ''')

db_cursor.execute('''
          CREATE TABLE air_pressure
          (id INT NOT NULL AUTO_INCREMENT, 
           sensor_id VARCHAR(250) NOT NULL,
           coordinates VARCHAR(250) NOT NULL,
           air_pressure VARCHAR(250) NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT air_pressure_pk PRIMARY KEY (id))
          ''')

db_conn.commit()
db_conn.close()
