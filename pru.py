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

    def show_category_options(self):
        category_options_window = tk.Toplevel(self.master)
        category_options_window.title("Opciones de Categorías")

        category_options_window.geometry("300x250+{}+{}".format(
            self.master.winfo_rootx() + self.master.winfo_reqwidth() // 2 - 200,
            self.master.winfo_rooty() + self.master.winfo_reqheight() // 2 - 90))

        frame = tk.Frame(category_options_window)
        frame.pack(expand=True, fill=tk.BOTH)

        tk.Button(frame, text="Agregar Categoría", command=self.add_category).pack(pady=10)
        tk.Button(frame, text="Eliminar Categoría", command=self.delete_category).pack(pady=10)
        tk.Button(frame, text="Editar Categoría", command=self.edit_category).pack(pady=10)
        tk.Button(frame, text="Buscar Categoría", command=self.search_category).pack(pady=10)

    def add_category(self):
        # Lógica para agregar una categoría
        messagebox.showinfo("Agregar Categoría", "Lógica para agregar una categoría")

    def delete_category(self):
        # Lógica para eliminar una categoría
        messagebox.showinfo("Eliminar Categoría", "Lógica para eliminar una categoría")

    def edit_category(self):
        # Lógica para editar una categoría
        messagebox.showinfo("Editar Categoría", "Lógica para editar una categoría")

    def search_category(self):
        # Lógica para buscar una categoría
        messagebox.showinfo("Buscar Categoría", "Lógica para buscar una categoría")

    def show_comment_options(self):
        comment_options_window = tk.Toplevel(self.master)
        comment_options_window.title("Opciones de Comentarios")

        comment_options_window.geometry("300x250+{}+{}".format(
            self.master.winfo_rootx() + self.master.winfo_reqwidth() // 2 - 200,
            self.master.winfo_rooty() + self.master.winfo_reqheight() // 2 - 90))

        frame = tk.Frame(comment_options_window)
        frame.pack(expand=True, fill=tk.BOTH)

        tk.Button(frame, text="Agregar Comentario", command=self.add_comment).pack(pady=10)
        tk.Button(frame, text="Eliminar Comentario", command=self.delete_comment).pack(pady=10)
        tk.Button(frame, text="Editar Comentario", command=self.edit_comment).pack(pady=10)
        tk.Button(frame, text="Buscar Comentario", command=self.search_comment).pack(pady=10)

    def add_comment(self):
        # Lógica para agregar un Comentario
        messagebox.showinfo("Agregar Comentario", "Lógica para agregar un Comentario")

    def delete_comment(self):
        # Lógica para eliminar una Comentario
        messagebox.showinfo("Eliminar Comentario", "Lógica para eliminar un Comentario")

    def edit_comment(self):
        # Lógica para editar una Comentario
        messagebox.showinfo("Editar Comentario", "Lógica para editar un Comentario")

    def search_comment(self):
        # Lógica para buscar una Comentario
        messagebox.showinfo("Buscar Comentario", "Lógica para buscar un Comentario")

    def show_tag_options(self):
        tag_options_window = tk.Toplevel(self.master)
        tag_options_window.title("Opciones de Tags")

        tag_options_window.geometry("300x250+{}+{}".format(
            self.master.winfo_rootx() + self.master.winfo_reqwidth() // 2 - 200,
            self.master.winfo_rooty() + self.master.winfo_reqheight() // 2 - 90))

        frame = tk.Frame(tag_options_window)
        frame.pack(expand=True, fill=tk.BOTH)

        tk.Button(frame, text="Agregar Tag", command=self.add_tag).pack(pady=10)
        tk.Button(frame, text="Eliminar Tag", command=self.delete_tag).pack(pady=10)
        tk.Button(frame, text="Editar Tag", command=self.edit_tag).pack(pady=10)
        tk.Button(frame, text="Buscar Tag", command=self.search_tag).pack(pady=10)

    def add_tag(self):
        # Lógica para agregar un Tag
        messagebox.showinfo("Agregar Tag", "Lógica para agregar un tag")

    def delete_tag(self):
        # Lógica para eliminar un tag
        messagebox.showinfo("Eliminar Tag", "Lógica para eliminar un tag")

    def edit_tag(self):
        # Lógica para editar un tag
        messagebox.showinfo("Editar Tag", "Lógica para editar un tag")

    def search_tag(self):
        # Lógica para buscar un tag
        messagebox.showinfo("Buscar Tag", "Lógica para buscar un tag")

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
            
            # Crear una nueva ventana para mostrar el artículo
            view_article_dialog = tk.Toplevel(self.master)
            view_article_dialog.title("Ver Artículo")

            # Mostrar título y contenido del artículo
            tk.Label(view_article_dialog, text="Título:").grid(row=0, column=0, sticky="w")
            tk.Label(view_article_dialog, text=article['title']).grid(row=0, column=1, sticky="w")

            tk.Label(view_article_dialog, text="Contenido:").grid(row=1, column=0, sticky="nw")
            content_text = tk.Text(view_article_dialog, wrap="word", height=10, width=50)
            content_text.grid(row=1, column=1, sticky="w")
            content_text.insert(tk.END, article['text'])
            content_text.config(state=tk.DISABLED)

            # Mostrar comentarios asociados al artículo
            tk.Label(view_article_dialog, text="Comentarios:").grid(row=2, column=0, sticky="nw")
            comments_frame = tk.Frame(view_article_dialog)
            comments_frame.grid(row=2, column=1, sticky="w")

            comments_scrollbar = tk.Scrollbar(comments_frame, orient="vertical")
            comments_listbox = tk.Listbox(comments_frame, yscrollcommand=comments_scrollbar.set, height=6, width=50)
            comments_scrollbar.config(command=comments_listbox.yview)
            comments_scrollbar.pack(side="right", fill="y")
            comments_listbox.pack(side="left", fill="both", expand=True)

            comments = self.comments_collection.find({"article_id": ObjectId(article_id)})
            for comment in comments:
                comments_listbox.insert(tk.END, f"{comment['user_name']}: {comment['text']}")

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
        users_listbox = tk.Listbox(add_comment_dialog)
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
