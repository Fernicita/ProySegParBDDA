import pymongo

# Establecer la conexión con el servidor MongoDB (asegúrate de tener MongoDB en ejecución)
client = pymongo.MongoClient('localhost', 27017)  # El primer parámetro es el host y el segundo es el puerto

db = client['ProySegPar'] #

users_collection = db["users"]
articles_collection = db["articles"]
comments_collection = db["comments"]
tags_collection = db["tags"]
categories_collection = db["categories"]

# Ejemplo de inserción de datos en la colección de usuarios
user_data = {
    "username": "usuario1",
    "email": "usuario1@example.com",
    "nombre": "Nombre del Usuario 1"
}
user_id = users_collection.insert_one(user_data).inserted_id
print(f"Usuario insertado con ID: {user_id}")

# Ejemplo de consulta en la colección de usuarios
user = users_collection.find_one({"username": "usuario1"})
if user:
    print(f"Usuario encontrado: {user}")


# Cerrar la conexión a la base de datos
client.close()
