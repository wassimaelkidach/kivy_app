from kivy.app import App
import mysql.connector
from mysql.connector import Error
import re
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import AsyncImage
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.properties import BooleanProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.utils import get_color_from_hex
from io import BytesIO
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from database import create_connection, validate_login, check_email_exists, create_user
from database import add_favori, remove_favori, is_favori

Window.size = (400, 600)

# Initialize database
create_connection()

class DatabasePopup(FloatLayout):
    """Special popup for database errors"""
    error_label = ObjectProperty(None)

def show_error(message):
    """Show database-related errors"""
    # Get the app instance
    app = App.get_running_app()
    
    # Dismiss any existing popup
    app.dismiss_popup()
    
    # Create new popup
    content = DatabasePopup()
    content.error_label.text = message
    
    # Create and store popup reference
    app.current_popup = Popup(title="UPDATE !",
                            content=content,
                            size_hint=(0.8, 0.4),
                            separator_color=(0.9, 0.6, 0.1, 1),
                            auto_dismiss=False)
    
    app.current_popup.open()

def is_valid_email(email):
    """Check if email has valid format using regex"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_password(password):
    """Check if password meets complexity requirements"""
    if len(password) < 10:
        return False, "Password must be at least 10 characters long"
    
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit"
    
    special_chars = r'!@#$%^&*()_+-=[]{};:"\|,.<>/?'
    if not any(char in special_chars for char in password):
        return False, "Password must contain at least one special character"
    
    return True, ""

class PopupWindow(Widget):
    def btn(self):
        popFun()

class P(FloatLayout):
    pass

def popFun():
    show = P()
    window = Popup(title="popup", content=show,
                  size_hint=(None, None), size=(300, 300))
    window.open()

class LoginWindow(Screen):
    email = ObjectProperty(None)
    pwd = ObjectProperty(None)

    def validate(self):
        try:
            # Validation des entrées
            if not self.email.text.strip():
                show_error("Email is required!")
                return

            if not self.pwd.text:
                show_error("Password is required!")
                return

            email = self.email.text.strip()
            if not is_valid_email(email):
                show_error("Please enter a valid email address")
                return

            # Authentification
            user_id = validate_login(email, self.pwd.text)
            
            if user_id is not None:  # Vérification explicite
                app = App.get_running_app()
                app.current_user_id = user_id
                self.manager.current = 'logdata'
                self.email.text = ""
                self.pwd.text = ""
            else:
                show_error("Invalid email or password")
                
        except Exception as e:
            show_error("An error occurred during login")
            print(f"Error: {e}")

class SignupWindow(Screen):
    name2 = ObjectProperty(None)
    email = ObjectProperty(None)
    pwd = ObjectProperty(None)
    phone = ObjectProperty(None)
    
    def signupbtn(self):
        if not all([self.name2.text, self.email.text, self.pwd.text, self.phone.text]):
            show_error("All fields are required!")
            return

        if not is_valid_email(self.email.text):
            show_error("Please enter a valid email address")
            return
            
        is_valid, error_msg = is_valid_password(self.pwd.text)
        if not is_valid:
            show_error(error_msg)
            return
        
        if not self.phone.text.isdigit() or len(self.phone.text) < 10:
            show_error("Please enter a valid phone number (min 10 characters)")
            return
    
        if check_email_exists(self.email.text):
            show_error("Email already registered!")
            return
            
        if create_user(self.name2.text, self.email.text, self.pwd.text, self.phone.text):
            self.clear_fields()
            self.manager.current = 'login'
        else:
            show_error("Registration failed. Please try again.")

    def clear_fields(self):
        self.name2.text = ""
        self.email.text = ""
        self.pwd.text = ""
        self.phone.text = ""

class ClickableLabel(ButtonBehavior, Label):
    """Label cliquable sans apparence de bouton"""
    pass

class FavoriButton(Button):
    is_favori = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(is_favori=self.update_text)
        self.update_text()
        self.stylize_button()
        self.favori_btn = None

    def stylize_button(self):
        self.font_size = '14sp'
        self.bold = True
        self.color = get_color_from_hex("#ffffff")
        self.background_normal = ''
        self.background_down = ''
        self.border = (16, 16, 16, 16)
        self.size_hint = (None, None)
        self.size = (dp(160), dp(45))
        self.pos_hint = {'center_x': 0.5}
        self.padding = [dp(10), dp(10)]

    def update_text(self, *args):
        if self.is_favori:
            self.text = "Remove Favorite"
            self.background_color = get_color_from_hex("#D9534F")
        else:
            self.text = "Add to Favorite"
            self.background_color = get_color_from_hex("#5CB85C")

class LogDataWindow(Screen):
    project_container = ObjectProperty(None)
    
    def open_project_details(self, project_id, code_projet):
        """Ouvre l'écran des détails du projet"""
        self.manager.current = 'project_details'
        details_screen = self.manager.get_screen('project_details')
        details_screen.load_project_data(project_id, code_projet)

    def on_enter(self):
        self.load_projects()
        
    def search_action(self):
        print("Search action triggered")
    
    def logout_action(self):
        print("Logout action triggered")
        self.manager.current = 'login'
    
    def load_projects(self):
        """Load projects with centered cards"""
        self.project_container.clear_widgets()
        
        app = App.get_running_app()
        conn = create_connection()
        user_id = app.current_user_id
        if not conn:
            show_error("Database connection failed")
            return
        
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, code_projet, nom_projet, images FROM projets")
            projects = cursor.fetchall()
          
            for (project_id, code_projet, project_name, image) in projects:
                # Project card
                card = BoxLayout(
                    orientation='vertical',
                    size_hint=(None, None),
                    size=(dp(300), dp(350)),
                    spacing=dp(5),
                    pos_hint={'center_x': 0.5}
                )
                
                if image:
                    try:
                        # Load image from BLOB using BytesIO
                        data = BytesIO(image)
                        core_img = CoreImage(data, ext='jpg')
                        img = Image(
                            texture=core_img.texture,
                            size_hint=(1, None),
                            height=dp(320),
                            fit_mode='contain',
                        )
                    except Exception as e:
                        print(f"Error loading image: {e}")
                        img = Image(
                            source='images/default.png',
                            size_hint=(1, None),
                            height=dp(320),
                            fit_mode='contain',
                        )
                else:
                    img = Image(
                        source='images/default.',
                        size_hint=(1, None),
                        height=dp(320),
                        fit_mode='contain'
                    )
                
                name_label = ClickableLabel(
                    text=project_name,
                    size_hint=(1, None),
                    height=dp(50),
                    font_size='16sp',
                    halign='center',
                    valign='middle'
                )
                name_label.bind(on_release=lambda instance, pid=project_id, cp=code_projet: 
                    self.open_project_details(pid, cp))
                
                card.add_widget(img)
                card.add_widget(name_label)
                self.project_container.add_widget(card)
            
        except Error as e:
            show_error(f"Database error: {str(e)}")
        finally:
            if cursor:
                try:
                    cursor.fetchall()
                except:
                    pass
                cursor.close()
            if conn:
                conn.close() 

def open_project_details(self, project_id, code_projet):
    """Ouvre l'écran des détails avec l'ID et le code du projet"""
    self.manager.current = 'project_details'
    details_screen = self.manager.get_screen('project_details')
    details_screen.load_project_data(project_id, code_projet)

class ProjectDetailsWindow(Screen):
    project_name = ObjectProperty(None)
    project_code = ObjectProperty(None)
    dispos_container = ObjectProperty(None)
    project_id = None
    favori_btn = None

    def load_project_data(self, project_id, code_projet):
        """Charge les données du projet"""
        self.project_id = project_id
        conn = create_connection()
        if not conn:
            show_error("Database connection failed")
            return
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT nom_projet, code_projet FROM projets WHERE id = %s", (project_id,))
            project = cursor.fetchone()
            
            self.project_name.text = project['nom_projet']
            self.project_code.text = f"Code: {project['code_projet']}"
            
            cursor.execute("""
                SELECT type_lg, 
                       CONCAT(superfide_min, 'm²') as surface_min,
                       CONCAT(superfide_max, 'm²') as surface_max, 
                       CONCAT(prix, ' MAD') as prix_format,
                       nombre_disponible
                FROM dispos 
                WHERE code_projet = %s
                ORDER BY type_lg
            """, (code_projet,))
            
            self.display_dispos(cursor.fetchall())
            self.add_favorite_button(project_id)
            
        except Error as e:
            show_error(f"Database error: {str(e)}")
        finally:
            if conn:
                conn.close()

    def add_favorite_button(self, project_id):
        """Ajoute le bouton favori"""
        app = App.get_running_app()
        user_id = app.current_user_id
        
        btn_layout = BoxLayout(size_hint=(1, None), height=dp(50))
        
        self.favori_btn = FavoriButton(
            is_favori=is_favori(user_id, project_id),
            size_hint=(None, None),
            size=(dp(200), dp(40)),
            pos_hint={'center_x': 0.5}
        )
        self.favori_btn.bind(on_release=lambda btn: self.toggle_favori(project_id))
        
        btn_layout.add_widget(self.favori_btn)
        self.dispos_container.add_widget(btn_layout)

    def toggle_favori(self, project_id):
        """Gère l'ajout/suppression des favoris"""
        app = App.get_running_app()
        user_id = app.current_user_id
        
        if not user_id:
            show_error("Connectez-vous pour gérer les favoris")
            return
        
        if is_favori(user_id, project_id):
            if remove_favori(user_id, project_id):
                show_error("Removed from Favorites")
            else:
                show_error("Error while deleting")
        else:
            if add_favori(user_id, project_id):
                show_error("Added to favorites")
            else:
                show_error("Error while deleting")

        if self.favori_btn:
            self.favori_btn.is_favori = is_favori(user_id, project_id)

    def display_dispos(self, dispos):
        """Affiche les disponibilités"""
        self.dispos_container.clear_widgets()
        
        # Header
        header = BoxLayout(size_hint=(1, None), height=dp(40))
        header.add_widget(Label(text="Type", bold=True))
        header.add_widget(Label(text="Surface", bold=True))
        header.add_widget(Label(text="Prix", bold=True))
        header.add_widget(Label(text="Dispo", bold=True))
        self.dispos_container.add_widget(header)
        
        # Data rows
        for dispo in dispos:
            row = BoxLayout(size_hint=(1, None), height=dp(40))
            row.add_widget(Label(text=dispo['type_lg']))
            row.add_widget(Label(text=f"{dispo['surface_min']}-{dispo['surface_max']}"))
            row.add_widget(Label(text=dispo['prix_format']))
            row.add_widget(Label(
                text=str(dispo['nombre_disponible']),
                color=(0, 0.7, 0, 1) if dispo['nombre_disponible'] > 0 else (0.8, 0, 0, 1)
            ))
            self.dispos_container.add_widget(row)

class FavoritesScreen(Screen):
    project_container = ObjectProperty(None)

    def on_enter(self):
        self.load_favorites()

    def open_project_details(self, project_id, code_projet):
        """Ouvre l'écran des détails du projet"""
        self.manager.current = 'project_details'
        details_screen = self.manager.get_screen('project_details')
        details_screen.load_project_data(project_id, code_projet)

    def load_favorites(self):
        """Charge uniquement les projets favoris"""
        self.project_container.clear_widgets()
        app = App.get_running_app()
        user_id = app.current_user_id
        
        if not user_id:
            show_error("Connectez-vous pour voir vos favoris")
            return
            
        conn = create_connection()
        if not conn:
            show_error("Connexion DB échouée")
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, p.code_projet, p.nom_projet, p.images 
                FROM projets p
                JOIN favoris f ON p.id = f.projet_id
                WHERE f.user_id = %s
            """, (user_id,))
            
            projects = cursor.fetchall()
            
            if not projects:
                self.project_container.add_widget(Label(
                    text="You have no favorite Projects for the moment !",
                    size_hint=(1, None),
                    height=dp(50)
                ))
                return
                
            for (project_id, code_projet, project_name, image) in projects:
                card = BoxLayout(
                    orientation='vertical',
                    size_hint=(None, None),
                    size=(dp(300), dp(400)),
                    spacing=dp(5),
                    pos_hint={'center_x': 0.5}
                )
                
                # Image handling
                if image:
                    try:
                        data = BytesIO(image)
                        img = Image(
                            texture=CoreImage(data, ext='jpg').texture,
                            size_hint=(1, None),
                            height=dp(320),
                            fit_mode='contain'
                        )
                    except Exception as e:
                        img = Image(source='images/default.png')
                else:
                    img = Image(source='images/default.png')
                
                # Project name
                name_label = ClickableLabel(
                    text=project_name,
                    size_hint=(1, None),
                    height=dp(50),
                    font_size='16sp',
                    halign='center',
                    valign='middle'
                )
                name_label.bind(
                    on_release=lambda instance, pid=project_id, cp=code_projet: 
                    self.open_project_details(pid, cp)
                )
                
                card.add_widget(img)
                card.add_widget(name_label)
                self.project_container.add_widget(card)
                
        except Error as e:
            show_error(f"Erreur DB: {str(e)}")
        finally:
            if conn:
                conn.close()

class ProfileScreen(Screen):
    username_label = ObjectProperty(None)
    email_label = ObjectProperty(None)

    def show_favorites(self):
        # Redirige vers l'écran logdata et affiche les favoris
        logdata_screen = self.manager.get_screen('logdata')
        self.manager.current = 'logdata'
        logdata_screen.show_favorites()

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        user_id = app.current_user_id

        if not user_id:
            self.manager.current = 'login'
            return

        print("Chargement du profil pour l'utilisateur :", user_id)

        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT name, email FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            name, email = result
            self.ids.username_label.text = name
            self.ids.email_label.text = email
        else:
            self.ids.username_label.text = "Utilisateur inconnu"
            self.ids.email_label.text = ""
            
class WindowManager(ScreenManager):
    pass

Builder.load_file('login.kv')
sm = WindowManager()

# Adding screens
sm.add_widget(LoginWindow(name='login'))
sm.add_widget(SignupWindow(name='signup'))
sm.add_widget(LogDataWindow(name='logdata'))
sm.add_widget(ProfileScreen(name='profile'))
sm.add_widget(FavoritesScreen(name='favorites'))
sm.add_widget(ProjectDetailsWindow(name='project_details')) 

class LoginApp(App):
    current_popup = None
    
    def dismiss_popup(self):
        """Safely dismiss the current popup"""
        if self.current_popup:
            self.current_popup.dismiss()
            self.current_popup = None
    
    def build(self):
        from database import initialize_database
        initialize_database()
        Window.size = (400, 700)
        self.current_popup = None
        
        sm.current = 'login'
        return sm

if __name__ == "__main__":
    try:
        LoginApp().run()
    except KeyboardInterrupt:
        pass