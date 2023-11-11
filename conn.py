import pymongo
from bson.objectid import ObjectId
import flet as ft
from datetime import datetime


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

def ver_usuarios_nombres():
    print("lista de Usuarios: \n")
    for user in db.users.find():
        print(f"ID: {user['_id']}, Nombre: {user['name']}, Correo: {user['email']}")

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

    # Pedir tags al usuario
    # Pedir tags al usuario
    tags_input = input("Ingrese los nombres de los tags, separados por comas (si no existen se crearán): ")
    tags_nombres = [x.strip() for x in tags_input.split(",") if x.strip()]

    # Inicializar la lista de ObjectIds de tags para el artículo
    tags_ids = []

    # Verificar si cada tag ya existe, si no, crearlo
    for nombre_tag in tags_nombres:
        tag = db.tags.find_one({"name": nombre_tag})
        if tag:
            tags_ids.append(tag['_id'])
        else:
            # Si el tag no existe, crearlo con una lista de URLs vacía
            nuevo_tag = {"name": nombre_tag, "urls": []}
            tag_result = db.tags.insert_one(nuevo_tag)
            tags_ids.append(tag_result.inserted_id)
            print(f"Tag creado con ID: {tag_result.inserted_id} y nombre {nombre_tag}")

    # Crear el artículo con los tags aso
    # Pedir categorías al usuario
    categorias_input = input("Ingrese los nombres de las categorías, separados por comas (si no existen se crearán): ")
    categorias_nombres = [x.strip() for x in categorias_input.split(",") if x.strip()]

    # Inicializar la lista de ObjectIds de categorías para el artículo
    categorias_ids = []

    # Verificar si cada tag ya existe, si no, crearlo
    for nombre_categoria in categorias_nombres:
        categoria = db.categories.find_one({"name": nombre_categoria})
        if categoria:
            categorias_ids.append(categoria['_id'])
        else:
            # Si la categoría no existe, crearla con una lista de URLs vacía
            nueva_categoria = {"name": nombre_categoria, "urls": []}
            categoria_result = db.categories.insert_one(nueva_categoria)
            categorias_ids.append(categoria_result.inserted_id)
            print(f"Categoría creada con ID: {categoria_result.inserted_id} y nombre {nombre_categoria}")

    # Crear el artículo con los tags y categorías asociadas
    article_data = {
        "title": titulo,
        "date": fecha,
        "text": contenido,
        "user_id": usuario_id,
        "user_name": nombre_usuario,
        "comments": [],
        "tags": tags_ids,  # Asociar los tags existentes o recién creados
        "categories": categorias_ids  # Asociar las categorías existentes o recién creadas
    }
    article_result = db.articles.insert_one(article_data)

    # Actualizar la colección de tags para incluir la URL del nuevo artículo
    for tag_id in tags_ids:
        db.tags.update_one({"_id": tag_id}, {"$push": {"urls": article_result.inserted_id}})
    for categoria_id in categorias_ids:
        db.categories.update_one({"_id": categoria_id}, {"$push": {"urls": article_result.inserted_id}})

    # Actualizar el usuario con el nuevo artículo
    db.users.update_one({"_id": ObjectId(usuario_id)}, {"$push": {"articles": article_result.inserted_id}})

    print(f"Artículo creado con ID: {article_result.inserted_id}")


def ver_articulos():
    print("Lista de usuarios:\n ")
    for user in db.users.find():
        print(f"ID: {user['_id']}, Nombre: {user['name']}, Correo: {user['email']}")

    usuario_id = input("Ingrese el ID del usuario al que desea asociar el artículo: ")
    usuario = db.users.find_one({"_id": ObjectId(usuario_id)})

    if usuario:
        articulos = db.articles.find({"user_id": usuario_id})

        print(f"\nArtículos de {usuario['name']} ({usuario['email']}):\n")
        for articulo in articulos:
            # Obtener nombres de tags y categorías
            nombres_tags = [db.tags.find_one({"_id": tag_id})['name'] for tag_id in articulo['tags']]
            nombres_categorias = [db.categories.find_one({"_id": categoria_id})['name'] for categoria_id in articulo['categories']]

            # Obtener comentarios asociados al artículo
            comentarios = db.comments.find({"article_id": articulo['_id']})

            print(f"ID: {articulo['_id']}")
            print(f"Título: {articulo['title']}")
            print(f"Fecha: {articulo['date']}")
            print(f"Usuario: {articulo['user_name']}")
            print(f"Contenido: {articulo['text']}")
            print(f"Tags: {nombres_tags}")
            print(f"Categorías: {nombres_categorias}")

            print("Comentarios:")
            for comentario in comentarios:
                print(f"- ID: {comentario['_id']}, Usuario: {comentario['user_name']}, Texto: {comentario['text']}")

            print("-" * 30)

    else:
        print("Usuario no encontrado.")

def insertar_comentario_articulo():
    print("Lista de Artículos:\n")
    for article in articles_collection.find():
        print(f"ID: {article['_id']}, Título: {article['title']}")

    articulo_id = input("Ingrese el ID del artículo al que desea asociar el comentario: ")
    articulo = articles_collection.find_one({"_id": ObjectId(articulo_id)})
    if not articulo:
        print("Artículo no encontrado.")
        return
    titulo_articulo = articulo["title"]

    usuario_id = input("Ingrese el ID del usuario que realiza el comentario: ")
    usuario = users_collection.find_one({"_id": ObjectId(usuario_id)})
    if not usuario:
        print("Usuario no encontrado.")
        return
    nombre_usuario = usuario["name"]

    comentario = input("Ingrese el comentario: ")

    comment_data = {
        "article_id": ObjectId(articulo_id), 
        "article_title": titulo_articulo, 
        "user_id": ObjectId(usuario_id), 
        "user_name": nombre_usuario, 
        "text": comentario
    }
    result = comments_collection.insert_one(comment_data)

    # Actualizar la colección de artículos con la referencia del nuevo comentario
    articles_collection.update_one(
        {"_id": ObjectId(articulo_id)}, 
        {"$push": {"comments": result.inserted_id}}
    )

    # Actualizar la colección de usuarios con la referencia del nuevo comentario
    users_collection.update_one(
        {"_id": ObjectId(usuario_id)}, 
        {"$push": {"comments": result.inserted_id}}
    )
    
    print(f"Comentario creado con ID: {result.inserted_id}")


def ver_comentarios_usuario():
    ver_usuarios_nombres()
    usuario_id = input("Ingrese el ID del usuario del cual desea ver los comentarios: ")
    usuario = db.users.find_one({"_id": ObjectId(usuario_id)})

    if usuario:
        comentarios = db.comments.find({"user_id": ObjectId(usuario_id)})
        print(f"Comentarios de {usuario['name']} ({usuario['email']}):")

        for comentario in comentarios:
            print(f"- ID: {comentario['_id']}")
            print(f"  Usuario: {comentario['user_name']}")
            print(f"  Comentario: {comentario['text']}")
            print(f"  En el Articulo: {comentario['article_title']}")
            print("-" * 30)
    else:
        print("Usuario no encontrado.")




def ver_comentarios_articulo():
    print("Lista de Artículos:\n")
    for article in articles_collection.find():
        print(f"ID: {article['_id']}, Título: {article['title']}")

    articulo_id = input("Ingrese el ID del artículo para ver los comentarios: ")
    articulo = articles_collection.find_one({"_id": ObjectId(articulo_id)})
    if articulo:
        
        comentarios = db.comments.find({"article_id": articulo['_id']})
        print("Comentarios:")
        for comentario in comentarios:
            print(f"- ID: {comentario['_id']}, Usuario: {comentario['user_name']}, Texto: {comentario['text']}")

        print("-" * 30)
    else:
        print("Artículo no encontrado.")

def crear_categoria():
    nombre_categoria = input("Ingrese el nombre de la categoría: ")
    
    # Mostrar todos los artículos disponibles para asociar
    print("Lista de Artículos disponibles para asociar a la categoría:\n")
    for article in db.articles.find():
        print(f"ID: {article['_id']}, Título: {article['title']}")

    # Pedir al usuario que introduzca los IDs de los artículos, separados por comas
    articulos_input = input("Ingrese los IDs de los artículos asociados a la categoría, separados por comas (deje en blanco si no desea asociar artículos): ")
    
    # Convertir la cadena de IDs en una lista, y crear ObjectIds válidos para MongoDB
    articulos_ids = [ObjectId(x.strip()) for x in articulos_input.split(",") if x.strip()] if articulos_input else []
    
    # Crear el documento categoría
    categoria_data = {"name": nombre_categoria, "urls": articulos_ids}
    result = db.categories.insert_one(categoria_data)
    
    # Si se proporcionaron artículos, actualizar sus documentos para añadir esta categoría
    if articulos_ids:
        for articulo_id in articulos_ids:
            db.articles.update_one({"_id": articulo_id}, {"$push": {"categories": result.inserted_id}})
    
    print(f"Categoría creada con ID: {result.inserted_id}")

def ver_categorias():
    print("Lista de Categorías:\n")
    for categoria in db.categories.find():
        print(f"ID: {categoria['_id']}, Nombre: {categoria['name']}")

        # Mostrar artículos asociados a la categoría
        articulos_asociados = db.articles.find({"categories": categoria['_id']})
        if articulos_asociados:
            print("Artículos asociados:")
            for articulo in articulos_asociados:
                print(f"- ID: {articulo['_id']}, Título: {articulo['title']}")
        else:
            print("No hay artículos asociados a esta categoría.")

        print("-" * 30)

def crear_tag():
    nombre_tag = input("Ingrese el nombre del tag: ")
    
    # Mostrar todos los artículos disponibles para asociar
    print("Lista de Artículos disponibles para asociar al tag:\n")
    for article in db.articles.find():
        print(f"ID: {article['_id']}, Título: {article['title']}")

    # Pedir al usuario que introduzca los IDs de los artículos, separados por comas
    articulos_input = input("Ingrese los IDs de los artículos asociados al tag, separados por comas (deje en blanco si no desea asociar artículos): ")
    
    # Convertir la cadena de IDs en una lista, y crear ObjectIds válidos para MongoDB
    articulos_ids = [ObjectId(x.strip()) for x in articulos_input.split(",") if x.strip()] if articulos_input else []
    
    # Crear el documento tag
    tag_data = {"name": nombre_tag, "urls": articulos_ids}
    result = db.tags.insert_one(tag_data)
    
    # Si se proporcionaron artículos, actualizar sus documentos para añadir este tag
    if articulos_ids:
        for articulo_id in articulos_ids:
            db.articles.update_one({"_id": articulo_id}, {"$push": {"tags": result.inserted_id}})
    
    print(f"Tag creado con ID: {result.inserted_id}")

def ver_tags():
    print("Lista de Tags:\n")
    for tag in db.tags.find():
        print(f"ID: {tag['_id']}, Nombre: {tag['name']}")

        # Mostrar artículos asociados al tag
        articulos_asociados = db.articles.find({"tags": tag['_id']})
        if articulos_asociados:
            print("Artículos asociados:")
            for articulo in articulos_asociados:
                print(f"- ID: {articulo['_id']}, Título: {articulo['title']}")
        else:
            print("No hay artículos asociados a este tag.")

        print("-" * 30)




def eliminar_usuario():
    # Mostrar todos los usuarios disponibles para eliminar
    print("Lista de Usuarios disponibles para eliminar:\n")
    for user in db.users.find():
        print(f"ID: {user['_id']}, Nombre: {user['name']}")

    # Pedir al usuario que introduzca el ID del usuario a eliminar
    usuario_id = input("Ingrese el ID del usuario que desea eliminar: ")
    
    try:
        # Convertir el string de entrada en un ObjectId de MongoDB
        usuario_id = ObjectId(usuario_id)
        
        # Eliminar el usuario
        result = db.users.delete_one({"_id": usuario_id})
        
        if result.deleted_count:
            print(f"Usuario con ID: {usuario_id} ha sido eliminado.")
        else:
            print(f"No se encontró el usuario con ID: {usuario_id} o no pudo ser eliminado.")

    except Exception as e:
        print(f"Ocurrió un error al eliminar el usuario: {e}")

def eliminar_articulo():
    # Mostrar todos los artículos disponibles para eliminar
    print("Lista de Artículos disponibles para eliminar:\n")
    for article in db.articles.find():
        print(f"ID: {article['_id']}, Título: {article['title']}")

    # Pedir al usuario que introduzca el ID del artículo a eliminar
    articulo_id = input("Ingrese el ID del artículo que desea eliminar: ")
    
    try:
        # Convertir el string de entrada en un ObjectId de MongoDB
        articulo_id = ObjectId(articulo_id)

        # Eliminar el artículo
        db.articles.delete_one({"_id": articulo_id})
        
        # Eliminar todas las referencias del artículo en la colección de comentarios
        db.comments.delete_many({"article_id": articulo_id})

        # Eliminar las referencias del artículo en la colección de tags
        db.tags.update_many({}, {"$pull": {"urls": articulo_id}})

        # Eliminar las referencias del artículo en la colección de categorías
        db.categories.update_many({}, {"$pull": {"urls": articulo_id}})

        print(f"Artículo con ID: {articulo_id} y todas sus referencias han sido eliminados.")

    except Exception as e:
        print(f"Ocurrió un error al eliminar el artículo: {e}")



def eliminar_comentario():
    # Mostrar todos los comentarios disponibles para eliminar
    print("Lista de Comentarios disponibles para eliminar:\n")
    for comment in db.comments.find():
        print(f"ID: {comment['_id']}, Texto: {comment['text']}")

    # Pedir al usuario que introduzca el ID del comentario a eliminar
    comentario_id = input("Ingrese el ID del comentario que desea eliminar: ")
    
    try:
        # Convertir el string de entrada en un ObjectId de MongoDB
        comentario_id = ObjectId(comentario_id)
        
        # Buscar el comentario para obtener el ID del artículo y del usuario asociado
        comentario = db.comments.find_one({"_id": comentario_id})
        if comentario:
            articulo_id = comentario['article_id']
            usuario_id = comentario['user_id']

            # Eliminar el comentario
            result = db.comments.delete_one({"_id": comentario_id})
            
            if result.deleted_count:
                print(f"Comentario con ID: {comentario_id} ha sido eliminado.")

                # Actualizar la colección de artículos para eliminar la referencia al comentario
                if articulo_id:
                    db.articles.update_one({"_id": articulo_id}, {"$pull": {"comments": comentario_id}})
                    print(f"Referencia al comentario eliminada del artículo con ID: {articulo_id}")

                # Actualizar la colección de usuarios para eliminar la referencia al comentario
                if usuario_id:
                    db.users.update_one({"_id": usuario_id}, {"$pull": {"comments": comentario_id}})
                    print(f"Referencia al comentario eliminada del usuario con ID: {usuario_id}")
            else:
                print(f"No se encontró el comentario con ID: {comentario_id} o no pudo ser eliminado.")

        else:
            print(f"No se encontró el comentario con ID: {comentario_id}")

    except Exception as e:
        print(f"Ocurrió un error al eliminar el comentario: {e}")

def eliminar_tag():
    # Mostrar todos los tags disponibles para eliminar
    print("Lista de Tags disponibles para eliminar:\n")
    for tag in db.tags.find():
        print(f"ID: {tag['_id']}, Nombre: {tag['name']}")

    # Pedir al usuario que introduzca el ID del tag a eliminar
    tag_id = input("Ingrese el ID del tag que desea eliminar: ")

    try:
        # Convertir el string de entrada en un ObjectId de MongoDB
        tag_id = ObjectId(tag_id)

        # Eliminar el tag
        result = db.tags.delete_one({"_id": tag_id})

        if result.deleted_count:
            print(f"Tag con ID: {tag_id} ha sido eliminado.")

            # Actualizar la colección de artículos para eliminar la referencia al tag
            updated_articles = db.articles.update_many({"tags": tag_id}, {"$pull": {"tags": tag_id}})
            print(f"Se han actualizado {updated_articles.modified_count} artículos para eliminar la referencia al tag eliminado.")

        else:
            print(f"No se encontró el tag con ID: {tag_id} o no pudo ser eliminado.")

    except Exception as e:
        print(f"Ocurrió un error al eliminar el tag: {e}")

def eliminar_categoria():
    # Mostrar todas las categorías disponibles para eliminar
    print("Lista de Categorías disponibles para eliminar:\n")
    for categoria in db.categories.find():
        print(f"ID: {categoria['_id']}, Nombre: {categoria['name']}")

    # Pedir al usuario que introduzca el ID de la categoría a eliminar
    categoria_id = input("Ingrese el ID de la categoría que desea eliminar: ")

    try:
        # Convertir el string de entrada en un ObjectId de MongoDB
        categoria_id = ObjectId(categoria_id)

        # Eliminar la categoría
        result = db.categories.delete_one({"_id": categoria_id})

        if result.deleted_count:
            print(f"Categoría con ID: {categoria_id} ha sido eliminada.")

            # Actualizar la colección de artículos para eliminar la referencia a la categoría
            updated_articles = db.articles.update_many(
                {"categories": categoria_id},
                {"$pull": {"categories": categoria_id}}
            )
            print(f"Se han actualizado {updated_articles.modified_count} artículos para eliminar la referencia a la categoría eliminada.")

        else:
            print(f"No se encontró la categoría con ID: {categoria_id} o no pudo ser eliminada.")

    except Exception as e:
        print(f"Ocurrió un error al eliminar la categoría: {e}")


eliminar_comentario()
# Cerrar la conexión a la base de dat
# Agrega la función al menú o a la parte del código donde quieres que se pueda ejecutar.
#insertar_articulo()
#insertar_usuario()
#insertar_comentario_articulo()
'''
insertar_usuario()
insertar_articulo()
insertar_comentario()654e74a9a69ee87308ae00a4
'''
#ver_usuarios()
#print("comentarios: \n" )
#ver_comentarios_usuario()
#print("articulos: \n" )
#ver_articulos()
#ver_comentarios_articulo()
#ver_categorias()
#ver_tags()

# Cerrar la conexión a la base de datos
client.close()
