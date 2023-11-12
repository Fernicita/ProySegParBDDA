import tkinter as tk
from tkinter import messagebox
from pymongo import MongoClient, errors
from bson.objectid import ObjectId
import datetime

class BlogInterface:
    def __init__(self, master):
        self.master = master
        self.master.title("Blog")

        # Conexión a la base de datos local
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.ProySegPar
        self.users_collection = self.db.users
        self.articles_collection = self.db.articles
        self.comments_collection = self.db.comments
        self.categories_collection = self.db.categories
        self.tags_collection = self.db.tags

        # Crear widgets
        self.create_widgets()

    def create_widgets(self):
        # Crear un contenedor Frame para los botones
        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=10)

        # Botones de inicio
        tk.Button(button_frame, text="Usuarios", command=self.show_user_options).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Categorías", command=self.show_category_options).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Comentarios", command=self.show_comment_options).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Tags", command=self.show_tag_options).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Artículos", command=self.show_article_options).pack(side=tk.LEFT, padx=10)

#Users
    def show_user_options(self):
        user_options_window = tk.Toplevel(self.master)
        user_options_window.title("Opciones de Usuario")

        options_frame = tk.Frame(user_options_window)
        options_frame.pack(side=tk.RIGHT, padx=10)

        data_frame = tk.Frame(user_options_window)
        data_frame.pack(side=tk.LEFT, padx=10)

        tk.Button(options_frame, text="Agregar Usuario", command=self.add_user_dialog).pack(pady=10)
        tk.Button(options_frame, text="Eliminar Usuario", command=self.delete_user).pack(pady=10)
        tk.Button(options_frame, text="Editar Usuario", command=self.edit_user).pack(pady=10)
        tk.Button(options_frame, text="Mostrar Artículos con esta categoria", command=self.show_articles_with_category).pack(pady=10)

        self.display_user_data(data_frame)

    def display_user_data(self, frame):
        users = self.users_collection.find()
        user_list = [f"ID: {user['_id']}, Name: {user.get('name', 'N/A')}, Email: {user.get('email', 'N/A')}" for user in users]

        # Limpiar el contenido anterior
        for widget in frame.winfo_children():
            widget.destroy()

        listbox = tk.Listbox(frame, selectmode=tk.SINGLE, width=90, height=10)
        listbox.pack()

        if user_list:
            for user_info in user_list:
                listbox.insert(tk.END, user_info)
        else:
            listbox.insert(tk.END, "No users found.")

        # Guardar frame como atributo de instancia
        self.user_data_frame = frame

    # Parte para que salga lo gráfico de añadir a un usuario
    def add_user_dialog(self):
        add_user_dialog = tk.Toplevel(self.master)
        add_user_dialog.title("Agregar Usuario")

        tk.Label(add_user_dialog, text="Name:").grid(row=0, column=0, padx=10, pady=5)
        name_entry = tk.Entry(add_user_dialog)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(add_user_dialog, text="Email:").grid(row=1, column=0, padx=10, pady=5)
        email_entry = tk.Entry(add_user_dialog)
        email_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Button(add_user_dialog, text="Add User", command=lambda: self.add_user(name_entry.get(), email_entry.get(), add_user_dialog)).grid(row=2, column=0, columnspan=2, pady=10)

    # Funciones
    def add_user(self, name, email, add_user_dialog):
        if name and email:
            try:
                user_data = {"name": name, "email": email, "articles": [], "comments": []}
                result = self.users_collection.insert_one(user_data)
                messagebox.showinfo("Todo bien,", f"User {name} añadido con un ID: {result.inserted_id}")

                # Llamada a la función para mostrar la información actualizada
                self.display_user_data(self.user_data_frame)

                add_user_dialog.destroy()
            except errors.PyMongoError as e:
                messagebox.showerror("Error :c", f"Error al añadir al usuario {e}")
        else:
            messagebox.showwarning("¡Aguas!", "Por favor llena el usuario y el email.")

    def delete_user(self):
    # Verificar si hay un usuario seleccionado
        selection = self.user_data_frame.winfo_children()[0].curselection()
        if not selection:
            messagebox.showwarning("¡Aguas!", "Por favor selecciona un usuario para eliminarlo.")
            return

        # Confirmar la eliminación del usuario
        response = messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres eliminar al usuario seleccionado?")
        if response:
            # Obtener el ID del usuario seleccionado
            selected_user = self.user_data_frame.winfo_children()[0].get(selection[0])
            user_id = selected_user.split(",")[0].split(":")[1].strip()
            
            try:
                # Eliminar el usuario
                result = self.users_collection.delete_one({"_id": ObjectId(user_id)})
                if result.deleted_count:
                    messagebox.showinfo("Éxito", "Usuario eliminado correctamente.")
                else:
                    messagebox.showwarning("Error", "El usuario no pudo ser eliminado.")
                
                # Actualizar la lista de usuarios
                self.display_user_data(self.user_data_frame)
            except errors.PyMongoError as e:
                messagebox.showerror("Error", f"Error al eliminar el usuario: {e}")



    def edit_user(self):
    # Verificar si hay un usuario seleccionado
        selection = self.user_data_frame.winfo_children()[0].curselection()
        if not selection:
            messagebox.showwarning("¡Aguas!", "Por favor selecciona un usuario para editarlo.")
            return

        # Obtener el ID del usuario seleccionado
        selected_user_info = self.user_data_frame.winfo_children()[0].get(selection[0])
        user_id = selected_user_info.split(",")[0].split(":")[1].strip()
        
        try:
            # Buscar los datos del usuario
            user_data = self.users_collection.find_one({"_id": ObjectId(user_id)})
            if not user_data:
                messagebox.showwarning("Error", "El usuario no pudo ser encontrado.")
                return

            # Abrir una nueva ventana de diálogo con los campos del usuario
            edit_user_dialog = tk.Toplevel(self.master)
            edit_user_dialog.title("Editar Usuario")

            # Nombre
            tk.Label(edit_user_dialog, text="Nombre:").grid(row=0, column=0, padx=10, pady=5)
            name_entry = tk.Entry(edit_user_dialog)
            name_entry.grid(row=0, column=1, padx=10, pady=5)
            name_entry.insert(0, user_data.get('name', ''))

            # Email
            tk.Label(edit_user_dialog, text="Email:").grid(row=1, column=0, padx=10, pady=5)
            email_entry = tk.Entry(edit_user_dialog)
            email_entry.grid(row=1, column=1, padx=10, pady=5)
            email_entry.insert(0, user_data.get('email', ''))

            # Botón para guardar los cambios
            tk.Button(edit_user_dialog, text="Guardar Cambios",
                    command=lambda: self.update_user(user_id, name_entry.get(), email_entry.get(), edit_user_dialog)).grid(row=2, column=0, columnspan=2, pady=10)
        except errors.PyMongoError as e:
            messagebox.showerror("Error", f"Error al recuperar el usuario para editar: {e}")
    
        
    def update_user(self, user_id, name, email, edit_user_dialog):
        # Verificar que los campos no estén vacíos
        if not name or not email:
            messagebox.showwarning("¡Aguas!", "El nombre y el email no pueden estar vacíos.")
            return

        try:
            # Actualizar los datos del usuario
            self.users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"name": name, "email": email}})
            messagebox.showinfo("Éxito", "Usuario actualizado correctamente.")
            
            # Actualizar la lista de usuarios y cerrar la ventana de diálogo
            self.display_user_data(self.user_data_frame)
            edit_user_dialog.destroy()
        except errors.PyMongoError as e:
            messagebox.showerror("Error", f"Error al actualizar el usuario: {e}")



    def search_user(self):
        try:
            users = self.users_collection.find()
            user_list = "\n".join([f"ID: {user['_id']}, Name: {user.get('name', 'N/A')}, Email: {user.get('email', 'N/A')}" for user in users])
            if user_list:
                messagebox.showinfo("Users", user_list)
            else:
                messagebox.showinfo("Users", "No users found.")
        except errors.PyMongoError as e:
            messagebox.showerror("Error", f"Error retrieving users: {e}")

#Categories
    def show_category_options(self):
        category_options_window = tk.Toplevel(self.master)
        category_options_window.title("Opciones para Categoría")

        options_frame = tk.Frame(category_options_window)
        options_frame.pack(side=tk.RIGHT, padx=10)

        data_frame = tk.Frame(category_options_window)
        data_frame.pack(side=tk.LEFT, padx=10)

        tk.Button(options_frame, text="Agregar Categoría", command=self.add_category_dialog).pack(pady=10)
        tk.Button(options_frame, text="Eliminar Categoría", command=self.delete_category).pack(pady=10)
        tk.Button(options_frame, text="Editar Categoría", command=self.edit_category).pack(pady=10)
        tk.Button(options_frame, text="Mostrar Artículos con Categoría", command=self.show_articles_with_category).pack()
        self.display_category_data(data_frame)
        
        
    def display_category_data(self, frame):
        categories = self.categories_collection.find()
        category_list = []

        for category in categories:
            category_name = category.get('name', 'N/A')
            category_urls = category.get('urls', [])
            category_urls_str = ', '.join(map(str, category_urls))
            category_info = f"ID: {category['_id']}, Name: {category_name}, URLs: {category_urls_str}"

            category_list.append(category_info)

        # Limpiar el contenido anterior
        for widget in frame.winfo_children():
            widget.destroy()

        listbox = tk.Listbox(frame, selectmode=tk.SINGLE, width=90, height=10)
        listbox.pack()

        if category_list:
            for category_info in category_list:
                listbox.insert(tk.END, category_info)
        else:
            listbox.insert(tk.END, "No categories found.")

        # Guardar frame como atributo de instancia
        self.category_data_frame = frame


    def add_category_dialog(self):
        add_category_dialog = tk.Toplevel(self.master)
        add_category_dialog.title("Agregar Categoría")

        tk.Label(add_category_dialog, text="Name:").grid(row=0, column=0, padx=10, pady=5)
        name_entry = tk.Entry(add_category_dialog)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Button(add_category_dialog, text="Add Category", command=lambda: self.add_category(name_entry.get(), add_category_dialog)).grid(row=2, column=0, columnspan=2, pady=10)


    def add_category(self, name, add_category_dialog):
        if name:
            try:
                category_data = {"name": name, "url": []}  # Agregamos "url": [] por defecto
                result = self.categories_collection.insert_one(category_data)
                messagebox.showinfo("Todo bien,", f"Categoría {name} añadida con un ID: {result.inserted_id}")

                # Llamada a la función para mostrar la información actualizada
                self.display_category_data(self.category_data_frame)

                add_category_dialog.destroy()
            except errors.PyMongoError as e:
                messagebox.showerror("Error :c", f"Error al añadir la categoría {e}")
        else:
            messagebox.showwarning("¡Aguas!", "Por favor llena el nombre de la categoría.")


    def delete_category(self):
        # Verificar si hay una categoría seleccionada
        selection = self.category_data_frame.winfo_children()[0].curselection()
        if not selection:
            messagebox.showwarning("¡Aguas!", "Por favor selecciona una categoría para eliminarla.")
            return

        # Confirmar la eliminación de la categoría
        response = messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres eliminar la categoría seleccionada?")
        if response:
            # Obtener el ID de la categoría seleccionada
            selected_category = self.category_data_frame.winfo_children()[0].get(selection[0])
            category_id = selected_category.split(",")[0].split(":")[1].strip()

            try:
                # Eliminar la categoría
                result = self.categories_collection.delete_one({"_id": ObjectId(category_id)})
                if result.deleted_count:
                    messagebox.showinfo("Éxito", "Categoría eliminada correctamente.")

                    # Actualizar la colección de artículos para eliminar la referencia a la categoría
                    updated_articles = self.articles_collection.update_many(
                        {"categories": ObjectId(category_id)},
                        {"$pull": {"categories": ObjectId(category_id)}}
                    )

                    # Mostrar el mensaje de actualización
                    messagebox.showinfo("Éxito", f"Se han actualizado {updated_articles.modified_count} artículos para eliminar la referencia a la categoría eliminada.")

                else:
                    messagebox.showwarning("Error", "La categoría no pudo ser eliminada.")

                # Actualizar la lista de categorías
                self.display_category_data(self.category_data_frame)

            except errors.PyMongoError as e:
                messagebox.showerror("Error", f"Error al eliminar la categoría: {e}")

    def edit_category(self):
        # Verificar si hay una categoría seleccionada
        selection = self.category_data_frame.winfo_children()[0].curselection()
        if not selection:
            messagebox.showwarning("¡Aguas!", "Por favor selecciona una categoría para editar.")
            return

        # Obtener el ID de la categoría seleccionada
        selected_category_info = self.category_data_frame.winfo_children()[0].get(selection[0])
        category_id = selected_category_info.split(",")[0].split(":")[1].strip()

        try:
            # Buscar los datos de la categoría
            category_data = self.categories_collection.find_one({"_id": ObjectId(category_id)})
            if not category_data:
                messagebox.showwarning("Error", "La categoría no pudo ser encontrada.")
                return

            # Abrir una nueva ventana de diálogo con los campos de la categoría
            edit_category_dialog = tk.Toplevel(self.master)
            edit_category_dialog.title("Editar Categoría")

            # Nombre
            tk.Label(edit_category_dialog, text="Nombre:").grid(row=0, column=0, padx=10, pady=5)
            name_entry = tk.Entry(edit_category_dialog)
            name_entry.grid(row=0, column=1, padx=10, pady=5)
            name_entry.insert(0, category_data.get('name', ''))

            # Botón para guardar los cambios
            tk.Button(edit_category_dialog, text="Guardar Cambios",
                    command=lambda: self.update_category(category_id, name_entry.get(), edit_category_dialog)).grid(row=1, column=0, columnspan=2, pady=10)

        except errors.PyMongoError as e:
            messagebox.showerror("Error", f"Error al recuperar la categoría para editar: {e}")


    def update_category(self, category_id, name, edit_category_dialog):
        # Verificar que los campos no estén vacíos
        if not name:
            messagebox.showwarning("¡Aguas!", "El nombre de la categoría no puede estar vacío.")
            return

        try:
            # Obtener datos antiguos de la categoría
            old_category_data = self.categories_collection.find_one({"_id": ObjectId(category_id)})

            # Actualizar los datos de la categoría
            self.categories_collection.update_one({"_id": ObjectId(category_id)}, {"$set": {"name": name}})
            messagebox.showinfo("Éxito", "Categoría actualizada correctamente.")

            # Actualizar la lista de categorías y cerrar la ventana de diálogo
            self.display_category_data(self.category_data_frame)
            edit_category_dialog.destroy()

            # Actualizar la categoría en los artículos
            articles_with_category = self.articles_collection.find({"categories": category_id})
            for article in articles_with_category:
                updated_categories = [cat_id if cat_id != category_id else str(old_category_data["_id"]) for cat_id in article['categories']]
                self.articles_collection.update_one(
                    {"_id": article["_id"]},
                    {"$set": {"categories": updated_categories}}
                )

        except errors.PyMongoError as e:
            messagebox.showerror("Error", f"Error al actualizar la categoría: {e}")

    def show_articles_with_category(self):
        # Verificar si hay una categoría seleccionada
        selection = self.category_data_frame.winfo_children()[0].curselection()
        if not selection:
            messagebox.showwarning("¡Aguas!", "Por favor selecciona una categoría para ver los artículos.")
            return

        try:
            # Obtener el ID de la categoría seleccionada
            selected_category_info = self.category_data_frame.winfo_children()[0].get(selection[0])
            category_id = selected_category_info.split(",")[0].split(":")[1].strip()

            # Buscar los artículos con la categoría específica
            articles_with_category = self.articles_collection.find({"categories": ObjectId(category_id)})

            # Crear una nueva ventana para mostrar los artículos con la categoría
            articles_with_category_dialog = tk.Toplevel(self.master)
            articles_with_category_dialog.title("Artículos con Categoría")

            # Crear un widget para mostrar la lista de artículos con la categoría
            articles_listbox = tk.Listbox(articles_with_category_dialog, width=50, height=10)
            articles_listbox.pack(pady=10)

            # Mostrar los títulos de los artículos en el widget
            for article in articles_with_category:
                articles_listbox.insert(tk.END, article.get('title', 'N/A'))

        except errors.PyMongoError as e:
            messagebox.showerror("Error", f"Error al recuperar artículos con la categoría: {e}")

#Comments
    def show_comment_options(self):
        comment_options_window = tk.Toplevel(self.master)
        comment_options_window.title("Opciones de Comentarios")

        options_frame = tk.Frame(comment_options_window)
        options_frame.pack(side=tk.RIGHT, padx=10)

        data_frame = tk.Frame(comment_options_window)
        data_frame.pack(side=tk.LEFT, padx=10)

        tk.Button(options_frame, text="Agregar Comentario", command=self.add_comment_dialog).pack(pady=10)
        tk.Button(options_frame, text="Eliminar Comentario", command=self.delete_comment).pack(pady=10)
        tk.Button(options_frame, text="Editar Comentario", command=self.edit_comment).pack(pady=10)
        self.display_comment_data(data_frame)

    def display_comment_data(self, frame):
        comments = self.comments_collection.find()
        comment_list = []

        for comment in comments:
            user_name = comment.get('user_name', 'N/A')
            text = comment.get('text', 'N/A')
            article_title = comment.get('article_title', 'N/A')
            comment_info = f"ID: {comment['_id']}, Usuario: {user_name}, Comentario: {text}, En el Articulo: {article_title}"

            comment_list.append(comment_info)

        # Limpiar el contenido anterior
        for widget in frame.winfo_children():
            widget.destroy()

        listbox = tk.Listbox(frame, selectmode=tk.SINGLE, width=90, height=10)
        listbox.pack()

        if comment_list:
            for comment_info in comment_list:
                listbox.insert(tk.END, comment_info)
        else:
            listbox.insert(tk.END, "No comments found.")

        # Guardar frame como atributo de instancia
        self.comment_data_frame = frame

    def add_comment_dialog(self):
        add_comment_dialog = tk.Toplevel(self.master)
        add_comment_dialog.title("Agregar Comentario")

        # Lista de correos electrónicos
        tk.Label(add_comment_dialog, text="Correo Electrónico:").grid(row=0, column=0, padx=10, pady=5)
        user_emails = [user['email'] for user in self.users_collection.find()]
        selected_user_email = tk.StringVar(add_comment_dialog)
        user_email_menu = tk.OptionMenu(add_comment_dialog, selected_user_email, *user_emails)
        user_email_menu.grid(row=0, column=1, padx=10, pady=5)

        # Campo de texto para el comentario
        tk.Label(add_comment_dialog, text="Comentario:").grid(row=1, column=0, padx=10, pady=5)
        text_entry = tk.Entry(add_comment_dialog)
        text_entry.grid(row=1, column=1, padx=10, pady=5)

        # Lista de títulos de artículos
        tk.Label(add_comment_dialog, text="En el Articulo:").grid(row=2, column=0, padx=10, pady=5)
        article_titles = [article['title'] for article in self.articles_collection.find()]
        selected_article_title = tk.StringVar(add_comment_dialog)
        article_title_menu = tk.OptionMenu(add_comment_dialog, selected_article_title, *article_titles)
        article_title_menu.grid(row=2, column=1, padx=10, pady=5)

        tk.Button(add_comment_dialog, text="Agregar Comentario",
                command=lambda: self.add_comment_logic(selected_user_email.get(), text_entry.get(), selected_article_title.get(), add_comment_dialog)).grid(row=3, column=0, columnspan=2, pady=10)


    def add_comment_logic(self, user_email, text, article_title, add_comment_dialog):
        if user_email and text and article_title:
            try:
                # Buscar el ID del usuario asociado al correo electrónico
                user = self.users_collection.find_one({"email": user_email})
                if not user:
                    messagebox.showerror("Error", "Usuario no encontrado.")
                    return

                user_id = user['_id']
                user_name = user['name']

                # Buscar el artículo por título
                article = self.articles_collection.find_one({"title": article_title})
                if not article:
                    messagebox.showerror("Error", "Artículo no encontrado.")
                    return

                article_id = article['_id']

                # Crear el comentario asociado al artículo
                comment_data = {
                    "article_id": article_id,
                    "article_title": article_title,
                    "user_id": user_id,
                    "user_name": user_name,
                    "user_email": user_email,
                    "text": text
                }

                result = self.comments_collection.insert_one(comment_data)

                # Actualizar la colección de artículos con la referencia del nuevo comentario
                self.articles_collection.update_one(
                    {"_id": article_id},
                    {"$push": {"comments": result.inserted_id}}
                )

                # Actualizar la colección de usuarios con la referencia del nuevo comentario
                self.users_collection.update_one(
                    {"_id": user_id},
                    {"$push": {"comments": result.inserted_id}}
                )

                messagebox.showinfo("Todo bien,", f"Comentario agregado con ID: {result.inserted_id}")

                # Llamada a la función para mostrar la información actualizada
                self.display_comment_data(self.comment_data_frame)

                add_comment_dialog.destroy()
            except errors.PyMongoError as e:
                messagebox.showerror("Error", f"Error al agregar el comentario: {e}")
        else:
            messagebox.showwarning("¡Aguas!", "Por favor llena todos los campos.") 


    def delete_comment(self):
        # Verificar si hay un comentario seleccionado
        selection = self.comment_data_frame.winfo_children()[0].curselection()
        if not selection:
            messagebox.showwarning("¡Aguas!", "Por favor selecciona un comentario para eliminarlo.")
            return

        # Confirmar la eliminación del comentario
        response = messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres eliminar el comentario seleccionado?")
        if response:
            # Obtener el ID del comentario seleccionado
            selected_comment = self.comment_data_frame.winfo_children()[0].get(selection[0])
            comment_id = selected_comment.split(",")[0].split(":")[1].strip()

            try:
                # Eliminar el comentario
                result = self.comments_collection.delete_one({"_id": ObjectId(comment_id)})
                if result.deleted_count:
                    messagebox.showinfo("Éxito", "Comentario eliminado correctamente.")
                else:
                    messagebox.showwarning("Error", "El comentario no pudo ser eliminado.")

                # Actualizar la lista de comentarios
                self.display_comment_data(self.comment_data_frame)

            except errors.PyMongoError as e:
                messagebox.showerror("Error", f"Error al eliminar el comentario: {e}")

    def edit_comment(self):
        # Verificar si hay un comentario seleccionado
        selection = self.comment_data_frame.winfo_children()[0].curselection()
        if not selection:
            messagebox.showwarning("¡Aguas!", "Por favor selecciona un comentario para editarlo.")
            return

        # Obtener el ID del comentario seleccionado
        selected_comment_info = self.comment_data_frame.winfo_children()[0].get(selection[0])
        comment_id = selected_comment_info.split(",")[0].split(":")[1].strip()

        try:
            # Buscar los datos del comentario
            comment_data = self.comments_collection.find_one({"_id": ObjectId(comment_id)})
            if not comment_data:
                messagebox.showwarning("Error", "El comentario no pudo ser encontrado.")
                return

            # Abrir una nueva ventana de diálogo con los campos del comentario
            edit_comment_dialog = tk.Toplevel(self.master)
            edit_comment_dialog.title("Editar Comentario")

            # Lista de correos electrónicos
            tk.Label(edit_comment_dialog, text="Correo Electrónico:").grid(row=0, column=0, padx=10, pady=5)
            user_emails = [user['email'] for user in self.users_collection.find()]
            selected_user_email = tk.StringVar(edit_comment_dialog, value=comment_data.get('user_email', ''))
            user_email_menu = tk.OptionMenu(edit_comment_dialog, selected_user_email, *user_emails)
            user_email_menu.grid(row=0, column=1, padx=10, pady=5)

            # Campo de texto para el comentario
            tk.Label(edit_comment_dialog, text="Comentario:").grid(row=1, column=0, padx=10, pady=5)
            text_entry = tk.Entry(edit_comment_dialog)
            text_entry.grid(row=1, column=1, padx=10, pady=5)
            text_entry.insert(0, comment_data.get('text', ''))

            # Lista de títulos de artículos
            tk.Label(edit_comment_dialog, text="En el Articulo:").grid(row=2, column=0, padx=10, pady=5)
            article_titles = [article['title'] for article in self.articles_collection.find()]
            selected_article_title = tk.StringVar(edit_comment_dialog, value=comment_data.get('article_title', ''))
            article_title_menu = tk.OptionMenu(edit_comment_dialog, selected_article_title, *article_titles)
            article_title_menu.grid(row=2, column=1, padx=10, pady=5)

            tk.Button(edit_comment_dialog, text="Guardar Cambios",
                    command=lambda: self.update_comment(comment_id, selected_user_email.get(), text_entry.get(), selected_article_title.get(), edit_comment_dialog)).grid(row=3, column=0, columnspan=2, pady=10)

        except errors.PyMongoError as e:
            messagebox.showerror("Error", f"Error al recuperar el comentario para editar: {e}")


    def update_comment(self, comment_id, user_email, text, article_title, edit_comment_dialog):
        # Verificar que los campos no estén vacíos
        if not user_email or not text:
            messagebox.showwarning("¡Aguas!", "El correo del usuario y el texto del comentario no pueden estar vacíos.")
            return

        try:
            # Obtener datos antiguos del comentario
            old_comment_data = self.comments_collection.find_one({"_id": ObjectId(comment_id)})

            # Buscar el ID del usuario asociado al correo electrónico
            user = self.users_collection.find_one({"email": user_email})
            if not user:
                messagebox.showerror("Error", "Usuario no encontrado.")
                return

            user_id = user['_id']
            user_name = user['name']

            # Buscar el artículo por título
            article = self.articles_collection.find_one({"title": article_title})
            if not article:
                messagebox.showerror("Error", "Artículo no encontrado.")
                return

            article_id = article['_id']

            # Actualizar los datos del comentario
            self.comments_collection.update_one(
                {"_id": ObjectId(comment_id)},
                {"$set": {"user_id": user_id, "user_name": user_name, "user_email": user_email, "text": text, "article_id": article_id, "article_title": article_title}}
            )
            messagebox.showinfo("Éxito", "Comentario actualizado correctamente.")

            # Actualizar la lista de comentarios y cerrar la ventana de diálogo
            self.display_comment_data(self.comment_data_frame)
            edit_comment_dialog.destroy()

        except errors.PyMongoError as e:
            messagebox.showerror("Error", f"Error al actualizar el comentario: {e}")

    def search_comment_logic(self, comment_id, search_comment_dialog):
        if comment_id:
            try:
                comment_data = self.comments_collection.find_one({"_id": ObjectId(comment_id)})
                if comment_data:
                    messagebox.showinfo("Resultado de la Búsqueda", f"Usuario: {comment_data.get('user_name', 'N/A')}\nComentario: {comment_data.get('text', 'N/A')}\nEn el Articulo: {comment_data.get('article_title', 'N/A')}")
                else:
                    messagebox.showinfo("Resultado de la Búsqueda", "Comentario no encontrado.")

                search_comment_dialog.destroy()
            except errors.PyMongoError as e:
                messagebox.showerror("Error", f"Error al buscar el comentario: {e}")
        else:
            messagebox.showwarning("¡Aguas!", "Por favor ingresa el ID del comentario para buscarlo.")

#Tags
    def show_tag_options(self):
        tag_options_window = tk.Toplevel(self.master)
        tag_options_window.title("Opciones para Etiqueta")

        options_frame = tk.Frame(tag_options_window)
        options_frame.pack(side=tk.RIGHT, padx=10)

        data_frame = tk.Frame(tag_options_window)
        data_frame.pack(side=tk.LEFT, padx=10)

        tk.Button(options_frame, text="Agregar Etiqueta", command=self.add_tag_dialog).pack(pady=10)
        tk.Button(options_frame, text="Eliminar Etiqueta", command=self.delete_tag).pack(pady=10)
        tk.Button(options_frame, text="Editar Etiqueta", command=self.edit_tag).pack(pady=10)
        tk.Button(options_frame, text="Mostrar Artículos con Etiqueta", command=self.show_articles_with_tag).pack(pady=10)
        self.display_tag_data(data_frame)


    def display_tag_data(self, frame):
        tags = self.tags_collection.find()
        tag_list = []

        for tag in tags:
            tag_name = tag.get('name', 'N/A')
            tag_info = f"ID: {tag['_id']}, Name: {tag_name}"

            tag_list.append(tag_info)

        # Limpiar el contenido anterior
        for widget in frame.winfo_children():
            widget.destroy()

        listbox = tk.Listbox(frame, selectmode=tk.SINGLE, width=50, height=10)
        listbox.pack()

        if tag_list:
            for tag_info in tag_list:
                listbox.insert(tk.END, tag_info)
        else:
            listbox.insert(tk.END, "No tags found.")

        # Guardar frame como atributo de instancia
        self.tag_data_frame = frame


    def add_tag_dialog(self):
        add_tag_dialog = tk.Toplevel(self.master)
        add_tag_dialog.title("Agregar Etiqueta")

        tk.Label(add_tag_dialog, text="Nombre:").grid(row=0, column=0, padx=10, pady=5)
        name_entry = tk.Entry(add_tag_dialog)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Button(add_tag_dialog, text="Agregar Etiqueta", command=lambda: self.add_tag(name_entry.get(), add_tag_dialog)).grid(row=1, column=0, columnspan=2, pady=10)


    def add_tag(self, name, add_tag_dialog):
        if name:
            try:
                tag_data = {"name": name}
                result = self.tags_collection.insert_one(tag_data)
                messagebox.showinfo("Éxito", f"Etiqueta {name} añadida con un ID: {result.inserted_id}")

                # Llamada a la función para mostrar la información actualizada
                self.display_tag_data(self.tag_data_frame)

                add_tag_dialog.destroy()
            except errors.PyMongoError as e:
                messagebox.showerror("Error", f"Error al añadir la etiqueta: {e}")
        else:
            messagebox.showwarning("¡Aguas!", "Por favor llena el nombre de la etiqueta.")


    def delete_tag(self):
        # Verificar si hay una etiqueta seleccionada
        selection = self.tag_data_frame.winfo_children()[0].curselection()
        if not selection:
            messagebox.showwarning("¡Aguas!", "Por favor selecciona una etiqueta para eliminarla.")
            return

        # Confirmar la eliminación de la etiqueta
        response = messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres eliminar la etiqueta seleccionada?")
        if response:
            # Obtener el ID de la etiqueta seleccionada
            selected_tag_info = self.tag_data_frame.winfo_children()[0].get(selection[0])
            tag_id = selected_tag_info.split(",")[0].split(":")[1].strip()

            try:
                # Eliminar la etiqueta
                result = self.tags_collection.delete_one({"_id": ObjectId(tag_id)})
                if result.deleted_count:
                    messagebox.showinfo("Éxito", "Etiqueta eliminada correctamente.")

                    # Actualizar la colección de artículos para eliminar la referencia a la etiqueta
                    updated_articles = self.articles_collection.update_many(
                        {"tags": ObjectId(tag_id)},
                        {"$pull": {"tags": ObjectId(tag_id)}}
                    )

                    # Mostrar el mensaje de actualización
                    messagebox.showinfo("Éxito", f"Se han actualizado {updated_articles.modified_count} artículos para eliminar la referencia a la etiqueta eliminada.")
                else:
                    messagebox.showwarning("Error", "La etiqueta no pudo ser eliminada.")

                # Actualizar la lista de etiquetas
                self.display_tag_data(self.tag_data_frame)

            except errors.PyMongoError as e:
                messagebox.showerror("Error", f"Error al eliminar la etiqueta: {e}")


    def edit_tag(self):
        # Verificar si hay una etiqueta seleccionada
        selection = self.tag_data_frame.winfo_children()[0].curselection()
        if not selection:
            messagebox.showwarning("¡Aguas!", "Por favor selecciona una etiqueta para editar.")
            return

        # Obtener el ID de la etiqueta seleccionada
        selected_tag_info = self.tag_data_frame.winfo_children()[0].get(selection[0])
        tag_id = selected_tag_info.split(",")[0].split(":")[1].strip()

        try:
            # Buscar los datos de la etiqueta
            tag_data = self.tags_collection.find_one({"_id": ObjectId(tag_id)})
            if not tag_data:
                messagebox.showwarning("Error", "La etiqueta no pudo ser encontrada.")
                return

            # Abrir una nueva ventana de diálogo con los campos de la etiqueta
            edit_tag_dialog = tk.Toplevel(self.master)
            edit_tag_dialog.title("Editar Etiqueta")

            # Nombre
            tk.Label(edit_tag_dialog, text="Nombre:").grid(row=0, column=0, padx=10, pady=5)
            name_entry = tk.Entry(edit_tag_dialog)
            name_entry.grid(row=0, column=1, padx=10, pady=5)
            name_entry.insert(0, tag_data.get('name', ''))

            # Botón para guardar los cambios
            tk.Button(edit_tag_dialog, text="Guardar Cambios",
                    command=lambda: self.update_tag(tag_id, name_entry.get(), edit_tag_dialog)).grid(row=1, column=0, columnspan=2, pady=10)

        except errors.PyMongoError as e:
            messagebox.showerror("Error", f"Error al recuperar la etiqueta para editar: {e}")


    def update_tag(self, tag_id, name, edit_tag_dialog):
    # Verificar que los campos no estén vacíos
        if not name:
            messagebox.showwarning("¡Aguas!", "El nombre de la etiqueta no puede estar vacío.")
            return

        try:
            # Obtener datos antiguos de la etiqueta
            old_tag_data = self.tags_collection.find_one({"_id": ObjectId(tag_id)})

            # Actualizar los datos de la etiqueta
            self.tags_collection.update_one({"_id": ObjectId(tag_id)}, {"$set": {"name": name}})
            messagebox.showinfo("Éxito", "Etiqueta actualizada correctamente.")

            # Actualizar la lista de etiquetas y cerrar la ventana de diálogo
            self.display_tag_data(self.tag_data_frame)
            edit_tag_dialog.destroy()

            # Actualizar la etiqueta en los artículos
            articles_with_tag = self.articles_collection.find({"tags": tag_id})
            for article in articles_with_tag:
                updated_tags = [tag_id if tag_id != tag_id else str(old_tag_data["_id"]) for tag_id in article['tags']]
                self.articles_collection.update_one(
                    {"_id": article["_id"]},
                    {"$set": {"tags": updated_tags}}
                )

        except errors.PyMongoError as e:
            messagebox.showerror("Error", f"Error al actualizar la etiqueta: {e}")

    def show_articles_with_tag(self):
        # Verificar si hay una etiqueta seleccionada
        selection = self.tag_data_frame.winfo_children()[0].curselection()
        if not selection:
            messagebox.showwarning("¡Aguas!", "Por favor selecciona una etiqueta para eliminarla.")
            return
        try:
            # Obtener el ID de la etiqueta seleccionada
            selected_tag_info = self.tag_data_frame.winfo_children()[0].get(selection[0])
            tag_id = selected_tag_info.split(",")[0].split(":")[1].strip()
            # Buscar los artículos con la etiqueta específica
            articles_with_tag = self.articles_collection.find({"tags": ObjectId(tag_id)})

            # Crear una nueva ventana para mostrar los artículos con la etiqueta
            articles_with_tag_dialog = tk.Toplevel(self.master)
            articles_with_tag_dialog.title("Artículos con Etiqueta")

            # Crear un widget para mostrar la lista de artículos con la etiqueta
            articles_listbox = tk.Listbox(articles_with_tag_dialog, width=50, height=10)
            articles_listbox.pack(pady=10)

            # Mostrar los títulos de los artículos en el widget
            for article in articles_with_tag:
                articles_listbox.insert(tk.END, article.get('title', 'N/A'))

        except errors.PyMongoError as e:
            messagebox.showerror("Error", f"Error al recuperar artículos con la etiqueta: {e}")



#Articles
    def show_article_options(self):
        article_options_window = tk.Toplevel(self.master)
        article_options_window.title("Opciones de Artículos")

        options_frame = tk.Frame(article_options_window)
        options_frame.pack(side=tk.RIGHT, padx=10)

        data_frame = tk.Frame(article_options_window)
        data_frame.pack(side=tk.LEFT, padx=10)

        tk.Button(options_frame, text="Ver Artículo", command=self.view_article).pack(pady=10)  
        tk.Button(options_frame, text="Agregar Artículo", command=self.add_article_dialog).pack(pady=10)
        tk.Button(options_frame, text="Eliminar Artículo", command=self.delete_article).pack(pady=10)
        tk.Button(options_frame, text="Editar Artículo", command=self.edit_article).pack(pady=10)
        tk.Button(options_frame, text="Agregar Comentario", command=self.add_comment_to_article).pack(pady=10)
        
        self.display_article_data(data_frame)
    
    def display_article_data(self, frame):
        # Aquí debes obtener la lista de artículos de la base de datos y mostrarla
        articles = self.articles_collection.find()
        article_list = [f"ID: {article['_id']}, Title: {article.get('title', 'N/A')}" for article in articles]

        # Limpiar el contenido anterior
        for widget in frame.winfo_children():
            widget.destroy()

        listbox = tk.Listbox(frame, selectmode=tk.SINGLE, width=90, height=10)
        listbox.pack()

        if article_list:
            for article_info in article_list:
                listbox.insert(tk.END, article_info)
        else:
            listbox.insert(tk.END, "No articles found.")

        # Guardar frame como atributo de instancia
        self.article_data_frame = frame


    def view_article(self):
        # Verificar si hay un artículo seleccionado
        selection = self.article_data_frame.winfo_children()[0].curselection()
        if not selection:
            messagebox.showwarning("¡Aguas!", "Por favor selecciona un artículo para verlo.")
            return

        # Obtener el ID del artículo seleccionado
        selected_article_info = self.article_data_frame.winfo_children()[0].get(selection[0])
        article_id = selected_article_info.split(",")[0].split(":")[1].strip()

        try:
            # Buscar la información del artículo en la base de datos
            article = self.articles_collection.find_one({"_id": ObjectId(article_id)})
            if not article:
                messagebox.showerror("Error", "Artículo no encontrado.")
                return

            # Obtener el nombre del usuario que hizo el artículo
            user = self.users_collection.find_one({"_id": article['user_id']})

            # Crear una nueva ventana para mostrar el artículo
            view_article_dialog = tk.Toplevel(self.master)
            view_article_dialog.title("Ver Artículo")

            # Mostrar título y autor del artículo
            tk.Label(view_article_dialog, text="Título:").grid(row=0, column=0, sticky="w")
            tk.Label(view_article_dialog, text=article['title']).grid(row=0, column=1, sticky="w")

            tk.Label(view_article_dialog, text="Autor:").grid(row=1, column=0, sticky="w")
            tk.Label(view_article_dialog, text=article['user_name']).grid(row=1, column=1, sticky="w")

            # Mostrar contenido del artículo
            tk.Label(view_article_dialog, text="Contenido:").grid(row=2, column=0, sticky="w")
            content_text = tk.Text(view_article_dialog, wrap="word", height=5, width=25)
            content_text.grid(row=3, column=0, columnspan=2, sticky="w")
            content_text.insert(tk.END, article['text'])
            content_text.config(state=tk.DISABLED)

            # Mostrar comentarios asociados al artículo
            tk.Label(view_article_dialog, text="Comentarios:").grid(row=2, column=1, sticky="w", pady=(10, 0))
            comments_frame = tk.Frame(view_article_dialog)
            comments_frame.grid(row=3, column=1, columnspan=2, sticky="w")

            comments_scrollbar = tk.Scrollbar(comments_frame, orient="vertical")
            comments_listbox = tk.Listbox(comments_frame, yscrollcommand=comments_scrollbar.set, height=4, width=50)
            comments_scrollbar.config(command=comments_listbox.yview)
            comments_scrollbar.pack(side="right", fill="y")
            comments_listbox.pack(side="left", fill="both", expand=True)

            comments = self.comments_collection.find({"article_id": ObjectId(article_id)})
            for comment in comments:
                comments_listbox.insert(tk.END, f"{comment['user_name']}: {comment['text']}")

            # Mostrar tags asociadas al artículo
            tk.Label(view_article_dialog, text="Tags:").grid(row=4, column=0, sticky="w", pady=(10, 0))
            tags_text = tk.Text(view_article_dialog, wrap="word", height=2, width=50)
            tags_text.grid(row=5, column=0, sticky="w", pady=(0, 10))

            # Obtener los nombres de las tags asociadas al artículo
            tag_names = []
            for tag_id in article.get('tags', []):
                tag = self.tags_collection.find_one({"_id": tag_id})
                if tag:
                    tag_names.append(tag.get('name', ''))
            tags_text.insert(tk.END, ', '.join(tag_names))
            tags_text.config(state=tk.DISABLED)

            # Mostrar categorías asociadas al artículo
            tk.Label(view_article_dialog, text="Categorías:").grid(row=4, column=1, sticky="w", pady=(10, 0))
            categories_text = tk.Text(view_article_dialog, wrap="word", height=2, width=50)
            categories_text.grid(row=5, column=1, sticky="w", pady=(0, 10))


            # Obtener los nombres de las categorías asociadas al artículo
            category_names = []
            for category_id in article.get('categories', []):
                category = self.categories_collection.find_one({"_id": category_id})
                if category:
                    category_names.append(category.get('name', ''))
            categories_text.insert(tk.END, ', '.join(category_names))
            categories_text.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Error", f"Error al recuperar la información del artículo: {e}")



    def add_article_dialog(self):
        # Crear la ventana de diálogo
        add_article_dialog = tk.Toplevel(self.master)
        add_article_dialog.title("Agregar Artículo")

        # Entrada para el título del artículo
        tk.Label(add_article_dialog, text="Título:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        title_entry = tk.Entry(add_article_dialog)
        title_entry.grid(row=0, column=1, padx=5, pady=5)

        # Entrada para el contenido del artículo
        tk.Label(add_article_dialog, text="Contenido:").grid(row=1, column=0, sticky="ne", padx=5, pady=5)
        text_entry = tk.Text(add_article_dialog, height=10, width=50)
        text_entry.grid(row=1, column=1, padx=5, pady=5)

        # Entrada para los tags
        tk.Label(add_article_dialog, text="Tags (separados por comas):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        tags_entry = tk.Entry(add_article_dialog)
        tags_entry.grid(row=2, column=1, padx=5, pady=5)

        # Entrada para las categorías
        tk.Label(add_article_dialog, text="Categorías (separadas por comas):").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        categories_entry = tk.Entry(add_article_dialog)
        categories_entry.grid(row=3, column=1, padx=5, pady=5)

        # Lista de usuarios
        tk.Label(add_article_dialog, text="Seleccione el usuario:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        users_listbox = tk.Listbox(add_article_dialog, height=4)
        users_listbox.grid(row=4, column=1, sticky="e", padx=5, pady=5)

        # Rellenar la lista de usuarios
        users = self.users_collection.find()
        for user in users:
            users_listbox.insert(tk.END, f"{user['_id']}: {user['name']}")

        # Botón para guardar el artículo
        tk.Button(add_article_dialog, text="Guardar Artículo",
                  command=lambda: self.save_article(title_entry.get(), text_entry.get("1.0", tk.END), tags_entry.get(),
                                                    categories_entry.get(), users_listbox, add_article_dialog)).grid(row=5, column=0, columnspan=2, pady=10)

    def save_article(self, title, text, tags, categories, users_listbox, dialog):
        # Validar que se haya seleccionado un usuario
        selected_idx = users_listbox.curselection()
        if not selected_idx:
            messagebox.showwarning("¡Aguas!", "Debes seleccionar un usuario.")
            return

        # Obtener el usuario seleccionado
        selected_user = users_listbox.get(selected_idx[0])
        user_id = ObjectId(selected_user.split(":")[0])
        user_name = selected_user.split(":")[1].strip()

        # Preparar tags y categorías
        tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        categories_list = [category.strip() for category in categories.split(",") if category.strip()]

        # Convertir tags y categorías a ObjectIds, creándolos si no existen
        tags_ids = self.process_tags(tags_list)
        categories_ids = self.process_categories(categories_list)

        # Fecha actual
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")

        # Crear el artículo
        article_data = {
            "title": title,
            "date": current_date,
            "text": text,
            "user_id": user_id,
            "user_name": user_name,
            "comments": [],
            "tags": tags_ids,
            "categories": categories_ids
        }
        article_result = self.articles_collection.insert_one(article_data)

        # Actualizar usuario, tags y categorías con la referencia del artículo
        self.users_collection.update_one({"_id": user_id}, {"$push": {"articles": article_result.inserted_id}})
        self.update_references(tags_ids, categories_ids, article_result.inserted_id)
        

        messagebox.showinfo("Éxito", "Artículo agregado correctamente.")
        self.display_article_data(self.article_data_frame)

        dialog.destroy()

    def process_tags(self, tags_list):
        tags_ids = []
        for tag_name in tags_list:
            tag = self.tags_collection.find_one({"name": tag_name})
            if tag:
                tags_ids.append(tag['_id'])
            else:
                result = self.tags_collection.insert_one({"name": tag_name, "urls": []})
                tags_ids.append(result.inserted_id)
        return tags_ids

    def process_categories(self, categories_list):
        categories_ids = []
        for category_name in categories_list:
            category = self.categories_collection.find_one({"name": category_name})
            if category:
                categories_ids.append(category['_id'])
            else:
                result = self.categories_collection.insert_one({"name": category_name, "urls": []})
                categories_ids.append(result.inserted_id)
        return categories_ids

    def update_references(self, tags_ids, categories_ids, article_id):
    # Actualizar tags: agregar referencia al artículo si no existe
        for tag_id in tags_ids:
            self.tags_collection.update_one(
                {"_id": tag_id, "urls": {"$ne": article_id}},
                {"$addToSet": {"urls": article_id}}
            )

        # Actualizar categorías: agregar referencia al artículo si no existe
        for category_id in categories_ids:
            self.categories_collection.update_one(
                {"_id": category_id, "urls": {"$ne": article_id}},
                {"$addToSet": {"urls": article_id}}
            )

        # Eliminar las referencias antiguas de tags y categorías que ya no están asociadas con el artículo
        self.tags_collection.update_many(
            {"urls": article_id, "_id": {"$nin": tags_ids}},
            {"$pull": {"urls": article_id}}
        )
        self.categories_collection.update_many(
            {"urls": article_id, "_id": {"$nin": categories_ids}},
            {"$pull": {"urls": article_id}}
        )

    def delete_article(self):
      
        # Verificar si hay un artículo seleccionado
        selection = self.article_data_frame.winfo_children()[0].curselection()
        if not selection:
            messagebox.showwarning("¡Aguas!", "Por favor selecciona un artículo para eliminarlo.")
            return
        # Confirmar la eliminación del artículo
        response = messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres eliminar el artículo seleccionado?")
        if response:
            # Obtener el ID del artículo seleccionado
            selected_article_info = self.article_data_frame.winfo_children()[0].get(selection[0])
            article_id = ObjectId(selected_article_info.split(",")[0].split(":")[1].strip())
            
            try:
                # Eliminar el artículo
                self.articles_collection.delete_one({"_id": article_id})

                # Eliminar todas las referencias del artículo en la colección de comentarios
                self.comments_collection.delete_many({"article_id": article_id})

                # Eliminar las referencias del artículo en la colección de tags y categorías
                self.tags_collection.update_many({}, {"$pull": {"urls": article_id}})
                self.categories_collection.update_many({}, {"$pull": {"urls": article_id}})

                messagebox.showinfo("Éxito", "Artículo eliminado correctamente.")
                
                # Actualizar la lista de artículos en la interfaz
                self.display_article_data(self.article_data_frame)

            except errors.PyMongoError as e:
                messagebox.showerror("Error", f"Ocurrió un error al eliminar el artículo: {e}")

    def edit_article(self):
        # Verificar si hay un artículo seleccionado
        selection = self.article_data_frame.winfo_children()[0].curselection()
        if not selection:
            messagebox.showwarning("¡Aguas!", "Por favor selecciona un artículo para editarlo.")
            return

        # Obtener el ID del artículo seleccionado
        selected_article_info = self.article_data_frame.winfo_children()[0].get(selection[0])
        article_id = ObjectId(selected_article_info.split(",")[0].split(":")[1].strip())

        # Buscar la información del artículo en la base de datos
        article = self.articles_collection.find_one({"_id": article_id})
        if not article:
            messagebox.showerror("Error", "Artículo no encontrado.")
            return

        # Crear una nueva ventana para editar artículo
        edit_article_dialog = tk.Toplevel(self.master)
        edit_article_dialog.title("Editar Artículo")

        # Entrada para el título del artículo
        tk.Label(edit_article_dialog, text="Título:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        title_entry = tk.Entry(edit_article_dialog)
        title_entry.grid(row=0, column=1, padx=5, pady=5)
        title_entry.insert(0, article['title'])

        # Entrada para el contenido del artículo
        tk.Label(edit_article_dialog, text="Contenido:").grid(row=1, column=0, sticky="ne", padx=5, pady=5)
        text_entry = tk.Text(edit_article_dialog, height=10, width=50)
        text_entry.grid(row=1, column=1, padx=5, pady=5)
        text_entry.insert(tk.END, article['text'])

        # Entrada para los tags
        existing_tags = ', '.join([self.tags_collection.find_one({'_id': tag_id})['name'] for tag_id in article['tags']])
        tk.Label(edit_article_dialog, text="Tags (separados por comas):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        tags_entry = tk.Entry(edit_article_dialog)
        tags_entry.grid(row=2, column=1, padx=5, pady=5)
        tags_entry.insert(0, existing_tags)

        # Entrada para las categorías
        existing_categories = ', '.join([self.categories_collection.find_one({'_id': category_id})['name'] for category_id in article['categories']])
        tk.Label(edit_article_dialog, text="Categorías (separadas por comas):").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        categories_entry = tk.Entry(edit_article_dialog)
        categories_entry.grid(row=3, column=1, padx=5, pady=5)
        categories_entry.insert(0, existing_categories)

        # Botón para guardar los cambios del artículo
        tk.Button(edit_article_dialog, text="Guardar Cambios",
                  command=lambda: self.update_article(article_id, title_entry.get(), text_entry.get("1.0", tk.END),
                                                      tags_entry.get(), categories_entry.get(), edit_article_dialog)).grid(row=4, column=0, columnspan=2, pady=10)

    def update_article(self, article_id, title, text, tags_str, categories_str, dialog):
        # Convertir tags y categorías de string a listas
        tags_list = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
        categories_list = [category.strip() for category in categories_str.split(",") if category.strip()]

        # Actualizar o crear tags y categorías
        tags_ids = self.process_tags(tags_list)
        categories_ids = self.process_categories(categories_list)

        # Actualizar el artículo en la base de datos
        try:
            self.articles_collection.update_one(
                {"_id": article_id},
                {"$set": {"title": title, "text": text, "tags": tags_ids, "categories": categories_ids}}
            )

            # Actualizar tags y categorías con nuevas referencias
            self.update_references(tags_ids, categories_ids, article_id)

            messagebox.showinfo("Éxito", "Artículo actualizado correctamente.")
            self.display_article_data(self.article_data_frame)
            dialog.destroy()

        except errors.PyMongoError as e:
            messagebox.showerror("Error", f"Error al actualizar el artículo: {e}")

    def add_comment_to_article(self):
        selection = self.article_data_frame.winfo_children()[0].curselection()
        if not selection:
            messagebox.showwarning("¡Aguas!", "Por favor selecciona un artículo para comentar.")
            return

        # Obtener el ID del artículo seleccionado
        selected_article_info = self.article_data_frame.winfo_children()[0].get(selection[0])
        article_id = ObjectId(selected_article_info.split(",")[0].split(":")[1].strip())

        # Crear ventana de diálogo para añadir comentario
        add_comment_dialog = tk.Toplevel(self.master)
        add_comment_dialog.title("Agregar Comentario")

        # Selección de usuario
        tk.Label(add_comment_dialog, text="Seleccione el usuario:").grid(row=0, column=0, sticky="w")
        users_listbox = tk.Listbox(add_comment_dialog, width=45)
        users_listbox.grid(row=0, column=1, pady=5)
        # Rellenar la lista de usuarios
        users = self.users_collection.find()
        for user in users:
            users_listbox.insert(tk.END, f"{user['_id']}: {user['name']}")

        # Campo de texto para el comentario
        tk.Label(add_comment_dialog, text="Comentario:").grid(row=1, column=0, sticky="nw", padx=5)
        comment_text = tk.Text(add_comment_dialog, height=6, width=40)
        comment_text.grid(row=1, column=1, padx=5)

        # Botón para guardar el comentario
        tk.Button(add_comment_dialog, text="Guardar Comentario",
                command=lambda: self.save_comment(article_id, users_listbox, comment_text, add_comment_dialog)).grid(row=2, column=0, columnspan=2, pady=5)

    def save_comment(self, article_id, users_listbox, comment_text_widget, dialog):
        user_selection = users_listbox.curselection()
        if not user_selection:
            messagebox.showwarning("¡Aguas!", "Debes seleccionar un usuario.")
            return

        # Obtener el ID del usuario seleccionado y el comentario
        selected_user_info = users_listbox.get(user_selection[0])
        user_id = ObjectId(selected_user_info.split(":")[0])
        user_name = selected_user_info.split(":")[1].strip()
        comment_text = comment_text_widget.get("1.0", tk.END).strip()

        if not comment_text:
            messagebox.showwarning("¡Aguas!", "El comentario no puede estar vacío.")
            return

        # Buscar la información del artículo en la base de datos para obtener el título
        article = self.articles_collection.find_one({"_id": article_id})
        if not article:
            messagebox.showerror("Error", "Artículo no encontrado.")
            return
        article_title = article['title']

        # Crear el comentario
        comment_data = {
            "article_id": article_id,
            "article_title": article_title,
            "user_id": user_id,
            "user_name": user_name,
            "text": comment_text
        }

        # Insertar el comentario en la base de datos
        try:
            result = self.comments_collection.insert_one(comment_data)

            # Actualizar la colección de artículos con la referencia del nuevo comentario
            self.articles_collection.update_one(
                {"_id": article_id},
                {"$push": {"comments": result.inserted_id}}
            )

            # Actualizar la colección de usuarios con la referencia del nuevo comentario
            self.users_collection.update_one(
                {"_id": user_id},
                {"$push": {"comments": result.inserted_id}}
            )

            messagebox.showinfo("Éxito", "Comentario agregado correctamente.")
            dialog.destroy()

        except errors.PyMongoError as e:
            messagebox.showerror("Error", f"Error al agregar el comentario: {e}")

    


if __name__ == "__main__":
    root = tk.Tk()
    app = BlogInterface(root)
    root.mainloop()
