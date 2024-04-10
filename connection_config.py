connection_config_dict = {
    'user': '***REMOVED***',
    'password': '***REMOVED***',
    'host': '***REMOVED***',
    'database': 'db4hls',
    'port': 3306
}

import mysql.connector
from mysql.connector import Error

def create_db_connection(config):
    try:
        connection = mysql.connector.connect(**config)
        print("MySQL database connection successful")
        print("MySQL server version: ", connection.get_server_info())
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None
