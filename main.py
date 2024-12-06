import sqlite3
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle

# Funções para manipulação do banco de dados
def create_connection():
    conn = sqlite3.connect('movies.db')
    return conn

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        genre TEXT NOT NULL,
        rating REAL,
        user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    conn.commit()
    conn.close()

create_tables()

# Definição das telas
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        with self.canvas.before:
            Color(0, 0, 0, 1)  
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Bem-vindo ao CinePedia', font_size=35))
        layout.add_widget(Button(text='Registrar', font_size=28, background_color=(1, 0, 0, 1), on_press=lambda x: app.change_to_register()))  
        layout.add_widget(Button(text='Login', font_size=28, background_color=(1, 0, 0, 1), on_press=lambda x: app.change_to_login()))  
        self.add_widget(layout)

    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super(RegisterScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Registrar Usuário', font_size=35))
        
        self.username_input = TextInput(hint_text='Nome de Usuário')
        self.password_input = TextInput(hint_text='Senha', password=True)
        
        layout.add_widget(self.username_input)
        layout.add_widget(self.password_input)
        layout.add_widget(Button(text='Registrar', font_size=28, background_color=(1, 0, 0, 1), on_press=self.register_user))
        layout.add_widget(Button(text='Voltar', font_size=28, background_color=(1, 0, 0, 1), on_press=lambda x: app.change_to_main()))
        
        self.add_widget(layout)

    def register_user(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        
        conn = create_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            popup = Popup(title='Sucesso', content=Label(text='Usuário registrado com sucesso!'), size_hint=(None, None), size=(400, 200))
            popup.open()
        except sqlite3.IntegrityError:
            popup = Popup(title='Erro', content=Label(text='Nome de usuário já existe!'), size_hint=(None, None), size=(400, 200))
            popup.open()
        finally:
            conn.close()

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Login', font_size=35))
        
        self.username_input = TextInput(hint_text='Nome de Usuário')
        self.password_input = TextInput(hint_text='Senha', password=True)
        
        layout.add_widget(self.username_input)
        layout.add_widget(self.password_input)
        layout.add_widget(Button(text='Login', font_size=28, background_color=(1, 0, 0, 1), on_press=self.login_user))
        layout.add_widget(Button(text='Menu', font_size=28, background_color=(1, 0, 0, 1), on_press=lambda x: app.change_to_main()))
        
        self.add_widget(layout)

    def login_user(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        
        if user:
            app.current_user = user  # Armazena o usuário atual
            app.change_to_movies()
        else:
            popup = Popup(title='Erro', content=Label(text='Nome de usuário ou senha incorretos!'), size_hint=(None, None), size=(400, 200))
            popup.open()
        
        conn.close()

class MovieScreen(Screen):
    def __init__(self, **kwargs):
        super(MovieScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Biblioteca de Filmes', font_size=35))
        layout.add_widget(Button(text='Adicionar Filme', font_size=28, background_color=(1, 0, 0, 1), on_press=lambda x: app.change_to_add_movie()))
        layout.add_widget(Button(text='Visualizar Avaliações', font_size=28,background_color=(1, 0, 0, 1), on_press=lambda x: app.change_to_view_movies()))
        layout.add_widget(Button(text='Voltar', font_size=28,background_color=(1, 0, 0, 1), on_press=lambda x: app.change_to_main()))
        self.add_widget(layout)

class AddMovieScreen(Screen):
    def __init__(self, **kwargs):
        super(AddMovieScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Adicionar Filme', font_size=35))
        
        self.title_input = TextInput(hint_text='Título do Filme')
        self.genre_input = TextInput(hint_text='Gênero')
        self.rating_input = TextInput(hint_text='Classificação (0-10)', input_filter='float')

        add_button = Button(text='Adicionar Filme', font_size=28,background_color=(1, 0, 0, 1), on_press=self.add_movie)
        layout.add_widget(self.title_input)
        layout.add_widget(self.genre_input)
        layout.add_widget(self.rating_input)
        layout.add_widget(add_button)
        layout.add_widget(Button(text='Voltar', font_size=28,background_color=(1, 0, 0, 1), on_press=lambda x: app.change_to_movies()))
        
        self.add_widget(layout)

    def add_movie(self, instance):
        title = self.title_input.text
        genre = self.genre_input.text
        rating = self.rating_input.text
        user_id = app.current_user[0]  # ID do usuário atual

        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO movies (title, genre, rating, user_id) VALUES (?, ?, ?, ?)", (title, genre, rating, user_id))
        conn.commit()
        conn.close()

        self.title_input.text = ''
        self.genre_input.text = ''
        self.rating_input.text = ''
        
        popup = Popup(title='Sucesso', content=Label(text='Filme adicionado com sucesso!'), size_hint=(None, None), size=(400, 200))
        popup.open()

class ViewMoviesScreen(Screen):
    def __init__(self, **kwargs):
        super(ViewMoviesScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.layout.add_widget(Label(text='Avaliações dos Filmes', font_size=24))

        self.scroll_view = ScrollView()
        self.grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))

        self.scroll_view.add_widget(self.grid)
        self.layout.add_widget(self.scroll_view)
        self.layout.add_widget(Button(text='Voltar', background_color=(1, 0, 0, 1),on_press=lambda x: app.change_to_movies()))
        self.add_widget(self.layout)

    def on_pre_enter(self):
        # Limpar a grade de filmes antes de adicionar novos itens
        self.grid.clear_widgets()

        if app.current_user is not None:
            user_id = app.current_user[0]
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT title, genre, rating FROM movies WHERE user_id=?", (user_id,))
            movies = cursor.fetchall()
            conn.close()
            
            for movie in movies:
                title, genre, rating = movie
                movie_info = f"Título: {title}\nGênero: {genre}\nClassificação: {rating}"
                self.grid.add_widget(Label(text=movie_info, size_hint_y=None, height=100))
        else:
            popup = Popup(title='Erro', content=Label(text='Você precisa fazer login para visualizar filmes!'), size_hint=(None, None), size=(400, 200))
            popup.open()
            app.change_to_login()


class MovieApp(App):
    current_user = None  # Armazena o usuário atual

    def build(self):
        self.manager = ScreenManager()
        self.manager.add_widget(MainScreen(name='main'))
        self.manager.add_widget(RegisterScreen(name='register'))
        self.manager.add_widget(LoginScreen(name='login'))
        self.manager.add_widget(MovieScreen(name='movies'))
        self.manager.add_widget(AddMovieScreen(name='add_movie'))
        self.manager.add_widget(ViewMoviesScreen(name='view_movies'))
        return self.manager

    def change_to_register(self):
        self.manager.current = 'register'

    def change_to_login(self):
        self.manager.current = 'login'

    def change_to_movies(self):
        self.manager.current = 'movies'

    def change_to_add_movie(self):
        self.manager.current = 'add_movie'

    def change_to_view_movies(self):
        self.manager.current = 'view_movies'
    
    def change_to_main(self):
        self.manager.current = 'main'

if __name__ == '__main__':
    app = MovieApp()
    app.run()
