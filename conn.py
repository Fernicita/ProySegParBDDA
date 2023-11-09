import pymongo
from bson.objectid import ObjectId

# Establecer la conexión con el servidor MongoDB (asegúrate de tener MongoDB en ejecución)
client = pymongo.MongoClient('localhost', 27017)  # El primer parámetro es el host y el segundo es el puerto

db = client['ProySegPar'] #

users_collection = db["users"]
articles_collection = db["articles"]
comments_collection = db["comments"]
tags_collection = db["tags"]
categories_collection = db["categories"]

def insertar_usuario():
    nombre = input("Ingrese el nombre del usuario: ")
    email = input("Ingrese el correo del usuario: ")

    user_data = {"name": nombre, "email": email, "articles": [], "comments": []}
    result = db.users.insert_one(user_data)

    print(f"Usuario creado con ID: {result.inserted_id}")

def ver_usuarios():
    print("lista de Usuarios: \n")
    for user in db.users.find():
        print(f"ID: {user['_id']}, Nombre: {user['name']}, Correo: {user['email']}, Articulos: {user['articles']}, Comentarios: {user['comments']}")



def insertar_articulo():
    print("lista de Usuarios: \n")
    for user in db.users.find():
        print(f"ID: {user['_id']}, Nombre: {user['name']}, Correo: {user['email']}")

    usuario_id = input("Ingrese el ID del usuario al que desea asociar el artículo: ")

    usuario = db.users.find_one({"_id": ObjectId(usuario_id)})
    nombre_usuario = usuario["name"] if usuario else "Usuario Desconocido"

    titulo = input("Ingrese el título del artículo: ")
    fecha = input("Ingrese la fecha del artículo (formato YYYY-MM-DD): ")
    contenido = input("Ingrese el contenido del artículo: ")

    article_data = {"title": titulo, "date": fecha, "text": contenido, "user_id": usuario_id, "user_name": nombre_usuario, "comments": [], "tags": [], "categories": []}
    result = db.articles.insert_one(article_data)

    db.users.update_one({"_id": ObjectId(usuario_id)}, {"$push": {"articles": ObjectId(result.inserted_id)}})

    print(f"Artículo creado con ID: {result.inserted_id}")

def ver_articulos():
    print("lista de usuarios:\n ")
    for user in db.users.find():
        print(f"ID: {user['_id']}, Nombre: {user['name']}, Correo: {user['email']}")

    usuario_id = input("Ingrese el ID del usuario al que desea asociar el artículo: ")
    usuario = db.users.find_one({"_id": ObjectId(usuario_id)})
    if usuario:
        articulos = db.articles.find({"user_id": usuario_id})
        print(f"Artículos de {usuario['name']} ({usuario['email']}):")
        for articulo in articulos:
            print(f"ID: {articulo['_id']}, Título: {articulo['title']}, Fecha: {articulo['date']}, Usuario: {articulo['user_name']} ,Contenido: {articulo['text']}")
    else:
        print("Usuario no encontrado.")



def insertar_comentario():
    print("lista de Usuarios: \n")
    for user in db.users.find():
        print(f"ID: {user['_id']}, Nombre: {user['name']}, Correo: {user['email']}")

    usuario_id = input("Ingrese el ID del usuario al que desea asociar al comentario: ")
    # Obtener el nombre del usuario basándote en el usuario_id
    usuario = db.users.find_one({"_id": ObjectId(usuario_id)})
    nombre_usuario = usuario["name"] if usuario else "Usuario Desconocido"

    comentario = input("Ingrese la el comentario: ")

    # Crear un nuevo comentario con el ID y el nombre del usuario
    comment_data = {"user_id": usuario_id, "user_name": nombre_usuario, "descripcion": comentario}
    result = db.comments.insert_one(comment_data)

    db.users.update_one({"_id": ObjectId(usuario_id)}, {"$push": {"comments": ObjectId(result.inserted_id)}})


    print(f"Comentario creado con ID: {result.inserted_id}")

def ver_comentarios():
    print("lista de usuarios:\n")
    for user in db.users.find():
        print(f"ID: {user['_id']}, Nombre: {user['name']}, Correo: {user['email']}")
    usuario_id = input("Ingrese el ID del usuario al que desea asociar al comentario: ")
    usuario = db.users.find_one({"_id": ObjectId(usuario_id)})
    if usuario:
        comentarios = db.comments.find({"user_id": usuario_id})
        print(f"Comentarios de {usuario['name']} ({usuario['email']}):")
        for comentario in comentarios:
            print(f"ID: {comentario['_id']}, Usuario: {comentario['user_name']}, comentario: {comentario['descripcion']}")
    else:
        print("Usuario no encontrado.")




'''
insertar_usuario()
insertar_articulo()
insertar_comentario()
'''
ver_usuarios()
print("comentarios: \n" )
ver_comentarios()
print("articulos: \n" )
ver_articulos()


# Cerrar la conexión a la base de datos
client.close()
