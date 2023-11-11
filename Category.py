import tkinter as tk
from tkinter import messagebox
from pymongo import MongoClient, errors
from bson.objectid import ObjectId

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


#CATEGORIA
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



#COMENTARIOS
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
        article_options_window.title("Opciones de Articulos")

        article_options_window.geometry("300x250+{}+{}".format(
            self.master.winfo_rootx() + self.master.winfo_reqwidth() // 2 - 200,
            self.master.winfo_rooty() + self.master.winfo_reqheight() // 2 - 90))

        frame = tk.Frame(article_options_window)
        frame.pack(expand=True, fill=tk.BOTH)

        tk.Button(frame, text="Agregar Articulo", command=self.add_article).pack(pady=10)
        tk.Button(frame, text="Eliminar Articulo", command=self.delete_article).pack(pady=10)
        tk.Button(frame, text="Editar Articulo", command=self.edit_article).pack(pady=10)
        tk.Button(frame, text="Buscar Articulo", command=self.search_article).pack(pady=10)

    def add_article(self):
        # Lógica para agregar un artículo
        messagebox.showinfo("Agregar Artículo", "Lógica para agregar un artículo")

    def delete_article(self):
        # Lógica para eliminar un artículo
        messagebox.showinfo("Eliminar Artículo", "Lógica para eliminar un artículo")

    def edit_article(self):
        # Lógica para editar un artículo
        messagebox.showinfo("Editar Artículo", "Lógica para editar un artículo")

    def search_article(self):
        # Lógica para buscar un artículo
        messagebox.showinfo("Buscar Artículo", "Lógica para buscar un artículo")

if __name__ == "__main__":
    root = tk.Tk()
    app = BlogInterface(root)
    root.mainloop()
