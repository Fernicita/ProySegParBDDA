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
        user_options_window= tk.Toplevel(self.master)
        user_options_window.title("Opciones de Usuario")
        
        user_options_window.geometry("300x250+{}+{}".format(
            self.master.winfo_rootx() + self.master.winfo_reqwidth() // 2 - 200,
            self.master.winfo_rooty() + self.master.winfo_reqheight() // 2 - 90))
        
        frame = tk.Frame(user_options_window)
        frame.pack(expand=True, fill=tk.BOTH)
            
        tk.Button(frame, text="Agregar Usuario", command=self.add_user).pack(pady=10)
        tk.Button(frame, text="Eliminar Usuario", command=self.delete_user).pack(pady=10)
        tk.Button(frame, text="Editar Usuario", command=self.edit_user).pack(pady=10)
        tk.Button(frame, text="Buscar Usuario", command=self.search_user).pack(pady=10)
        
    def add_user(self):
        # Lógica para agregar Usuario
        messagebox.showinfo("Agregar Usuario", "Lógica para agregar un Usuario")

    def delete_user(self):
        # Lógica para eliminar una usuario
        messagebox.showinfo("Eliminar usuario", "Lógica para eliminar una usuario")

    def edit_user(self):
        # Lógica para editar una usuario
        messagebox.showinfo("Editar usuario", "Lógica para editar una usuario")

    def search_user(self):
        # Lógica para buscar una usuario
        messagebox.showinfo("Buscar usuario", "Lógica para buscar una usuario")
        
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
