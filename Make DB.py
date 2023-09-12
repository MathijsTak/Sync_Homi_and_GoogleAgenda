import mysql.connector
from mysql.connector import Error
from getpass import getpass

def create_server_connection(host_name, user_name, user_password):
        connection = None
        try:
            connection = mysql.connector.connect(
                host=host_name,
                user=user_name,
                passwd=user_password
            )
            print("MySQL Database connection successful")
        except Error as err:
            print(f"Error: '{err}'")

        return connection

def create_db_connection(host_name, user_name, user_password, db_name):
        connection = None
        try:
            connection = mysql.connector.connect(
                host=host_name,
                user=user_name,
                passwd=user_password,
                database=db_name
            )
            print("MySQL Database connection successful")
        except Error as err:
            print(f"Error: '{err}'")

        return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")

host_name = input("Hostname: ")
user_name = input("Username: ")
user_password = getpass("User password: ")
db_name = input("Database name: ")

db_connection = create_db_connection(host_name, user_name, user_password, db_name)

if db_connection == None:
    server_connection = create_server_connection(host_name, user_name, user_password)

    query = f"""CREATE SCHEMA `{db_name}` ;"""

    execute_query(server_connection, query)

    db_connection = create_db_connection(host_name, user_name, user_password, db_name)

    query = """CREATE TABLE `users` (`IdUser` varchar(100) NOT NULL, 
    `CalendarId` varchar(100) DEFAULT NULL, 
    PRIMARY KEY (`IdUser`)) 
    ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;"""

    execute_query(db_connection, query)

email = input("Email: ")

query = f"""CREATE TABLE `{email}` (
`EventId` varchar(100) NOT NULL,
`AssignmentTitle` varchar(100) NOT NULL,
`AssignmentSubtitle` varchar(100) NOT NULL,
`AssignmentStart` datetime NOT NULL,
`AssignmentEnd` datetime NOT NULL,
PRIMARY KEY (`EventId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;"""

execute_query(db_connection, query)

query = f"""INSERT INTO `homi`.`users` (`IdUser`) VALUES ('{email}');"""

execute_query(db_connection, query)

