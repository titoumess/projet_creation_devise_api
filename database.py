import mysql.connector
from mysql.connector import Error

def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="projet_dl"
        )
        if connection.is_connected():
            print("Connexion réussie à la base de données MySQL")
    except Error as e:
        print(f"Erreur lors de la connexion à MySQL : {e}")
    return connection