import re
import requests
import base64
import os
from functools import partial
from io import BytesIO
from kivy.app import App
from kivy.graphics import Color, Line, Rectangle
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.metrics import dp
from kivy.core.image import Image as CoreImage
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.lang import Builder

class SwipeScreen(Screen):
    def on_touch_move(self, touch):
        dx = touch.dx
        dy = touch.dy

        if abs(dx) > abs(dy):
            if dx > 50:
                self.on_swipe_right()
            elif dx < -50:
                self.on_swipe_left()
        return super().on_touch_move(touch)

    def on_swipe_left(self):
        pass

    def on_swipe_right(self):
        pass

BASE_URL = os.environ.get("BASE_URL", "http://64.226.107.144:8000")

Window.size = (400, 700)

# -------------------- UTILS --------------------
class DatabasePopup(FloatLayout):
    error_label = ObjectProperty(None)

def show_error(message):
    app = App.get_running_app()
    app.dismiss_popup()
    content = DatabasePopup()
    content.error_label.text = message
    app.current_popup = Popup(title="INFO", content=content, size_hint=(0.8, 0.4), auto_dismiss=False)
    app.current_popup.open()

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_password(password):
    if len(password) < 10:
        return False, "Password must be at least 10 characters"
    if not any(char.isupper() for char in password):
        return False, "Must contain at least one uppercase letter"
    if not any(char.isdigit() for char in password):
        return False, "Must contain at least one digit"
    if not any(char in '!@#$%^&*()_+-=[]{};:\"\\|,.<>/?' for char in password):
        return False, "Must contain at least one special character"
    return True, ""

class ClickableLabel(ButtonBehavior, Label):
    pass

class TableCell(Label):
    """Custom Label avec bordures pour une cellule"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = (10, 10)
        self.halign = 'center'
        self.valign = 'middle'
        self.markup = True
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 0.5)
            Rectangle(pos=self.pos, size=self.size)
            # Bordure noire fine
            Color(1, 1, 1, 1)
            Line(rectangle=(self.x, self.y, self.width, self.height), width=1)

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

# API Functions
def create_user(name, email, password):
    try:
        response = requests.post(
            f"{BASE_URL}/signup",
            json={"name": name, "email": email, "password": password}
        )
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def validate_login(email, password):
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            return response.json().get("user_id")
        return None
    except requests.exceptions.RequestException:
        return None

def check_email_exists(email):
    try:
        response = requests.post(
            f"{BASE_URL}/check-email",
            json={"email": email}
        )
        if response.status_code == 200:
            return response.json().get("exists")
        return False
    except requests.exceptions.RequestException:
        return False

def fetch_projects():
    try:
        response = requests.get(f"{BASE_URL}/projects")
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.RequestException:
        return []

def fetch_profile(user_id):
    try:
        response = requests.get(f"{BASE_URL}/profile/{user_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None

# -------------------- SCREENS --------------------
class LoginWindow(SwipeScreen):
    email = ObjectProperty(None)
    pwd = ObjectProperty(None)

    def validate(self):
        email = self.email.text.strip()
        password = self.pwd.text

        if not email or not password:
            show_error("Email and password are required")
            return

        if not is_valid_email(email):
            show_error("Invalid email format")
            return

        try:
            response = requests.post(f"{BASE_URL}/login", json={"email": email, "password": password})
            if response.status_code == 200:
                App.get_running_app().current_user_id = response.json().get("user_id")
                self.manager.current = "logdata"
                self.email.text = ""
                self.pwd.text = ""
            else:
                show_error("Invalid email or password")
        except Exception:
            show_error("Server error")

    def reset_form(self):
        self.email.text = ""
        self.pwd.text = ""

class SignupWindow(SwipeScreen):
    name2 = ObjectProperty(None)
    email = ObjectProperty(None)
    pwd = ObjectProperty(None)
    phone = ObjectProperty(None)

    def signupbtn(self):
        name = self.name2.text.strip()
        email = self.email.text.strip()
        password = self.pwd.text
        phone = self.phone.text.strip()

        if not all([name, email, password, phone]):
            show_error("All fields are required")
            return

        if not is_valid_email(email):
            show_error("Invalid email format")
            return

        is_valid, msg = is_valid_password(password)
        if not is_valid:
            show_error(msg)
            return

        if not phone.isdigit() or len(phone) < 10:
            show_error("Invalid phone number")
            return

        try:
            res = requests.post(f"{BASE_URL}/check-email", json={"email": email})
            if res.json().get("exists"):
                show_error("Email already registered")
                return
        except:
            show_error("Server error")
            return

        try:
            response = requests.post(f"{BASE_URL}/signup", json={
                "name": name,
                "email": email,
                "password": password,
                "telephone": phone
            })
            if response.status_code == 200:
                self.clear_fields()
                self.manager.current = 'login'
            else:
                show_error("Signup failed")
        except:
            show_error("Server error")

    def clear_fields(self):
        self.name2.text = ""
        self.email.text = ""
        self.pwd.text = ""
        self.phone.text = ""

class LogDataWindow(SwipeScreen):
    project_container = ObjectProperty(None)

    def on_swipe_left(self):
        self.manager.current = 'favorites'

    def on_swipe_right(self):
        self.manager.current = 'profile'

    def on_enter(self):
        self.load_projects()

    def search_action(self):
        print("Search clicked")

    def logout_action(self):
        self.manager.current = 'login'

    def open_project_details(self, project_id, code_projet):
        print(f"[DEBUG] open_project_details called with ID: {project_id}, Code: {code_projet}")
        
        if not project_id:
            show_error("Aucun ID de projet transmis.")
            return
        
        app = App.get_running_app()
        app.current_project_id = project_id
        app.current_code_projet = code_projet

        self.manager.current = 'project_details'
        details_screen = self.manager.get_screen('project_details')
        details_screen.load_project_data(project_id, code_projet)

    def make_label_callback(self, pid, cp):
        def callback(instance):
            self.open_project_details(pid, cp)
        return callback

    def load_projects(self):
        self.project_container.clear_widgets()
        projects = fetch_projects()

        for proj in projects:
            project_id = proj.get("id")
            code_projet = proj.get("code_projet")
            name = proj.get("nom_projet", "")
            img_base64 = proj.get("image_base64", None)

            card = BoxLayout(
                orientation='vertical',
                size_hint=(None, None),
                size=(dp(300), dp(350)),
                spacing=dp(5),
                pos_hint={'center_x': 0.5}
            )

            if img_base64:
                try:
                    img_data = base64.b64decode(img_base64)
                    data = BytesIO(img_data)
                    core_img = CoreImage(data, ext='png')
                    img = Image(texture=core_img.texture, size_hint=(1, None), height=dp(320))
                except Exception as e:
                    print(f"Image error: {e}")
                    img = Image(source='images/default.png', size_hint=(1, None), height=dp(320))
            else:
                img = Image(source='images/default.png', size_hint=(1, None), height=dp(320))

            label = ClickableLabel(
                text=name,
                size_hint=(1, None),
                height=dp(30),
                font_size='16sp'
            )

            label.bind(on_release=self.make_label_callback(project_id, code_projet))

            card.add_widget(img)
            card.add_widget(label)
            self.project_container.add_widget(card)

class ProjectDetailsWindow(SwipeScreen):
    project_name = ObjectProperty(None)
    project_code = ObjectProperty(None)
    dispos_container = ObjectProperty(None)
    project_id = None
    favori_btn = None

    def on_pre_enter(self):
        app = App.get_running_app()
        self.load_project_data(app.current_project_id, app.current_code_projet)

    def load_project_data(self, project_id, code_projet):
        """Charge les données du projet depuis l'API FastAPI"""
        self.project_id = project_id

        try:
            res = requests.get(f"{BASE_URL}/project-details/{project_id}")
            if res.status_code == 200:
                data = res.json()
                self.project_name.text = data['nom_projet']
                self.project_code.text = f"Code: {data['code_projet']}"
                self.display_dispos(data['dispos'])

                app = App.get_running_app()

                fav_response = requests.get(
                    f"{BASE_URL}/favorites/check/{app.current_user_id}/{project_id}"
                )
                is_fav = fav_response.json().get('is_favorite', False)
                self.add_favorite_button(project_id, is_fav)
        except Exception as e:
                show_error(f"API Error: {str(e)}")

    def add_favorite_button(self, project_id, is_fav):
        """Ajoute le bouton favori"""
        app = App.get_running_app()
        user_id = app.current_user_id

        btn_layout = BoxLayout(size_hint=(1, None), height=dp(50))

        try:
            res = requests.get(f"{BASE_URL}/favorites/{user_id}")
            is_fav = project_id in [p['id'] for p in res.json()]
        except:
            is_fav = False

        self.favori_btn = FavoriButton(
            is_favori=is_fav,
            size_hint=(None, None),
            size=(dp(200), dp(40)),
            pos_hint={'center_x': 0.5}
        )
        self.favori_btn.bind(on_release=lambda btn: self.toggle_favori(project_id))
        btn_layout.add_widget(self.favori_btn)
        self.dispos_container.add_widget(btn_layout)

    def toggle_favori(self, project_id):
        app = App.get_running_app()
        user_id = app.current_user_id

        try:
            res = requests.post(f"{BASE_URL}/favorites/check", json={
                "user_id": user_id,
                "projet_id": project_id
                })
            
            is_fav = res.json().get("is_favorite", False)

            if is_fav:
                res = requests.post(f"{BASE_URL}/favorites/remove", json={
                "user_id": user_id,
                "projet_id": project_id
                })
                if res.status_code == 200:
                    show_error("Supprimé des favoris")
                    self.favori_btn.is_favori = False
            else:
                res = requests.post(f"{BASE_URL}/favorites/add", json={
                "user_id": user_id,
                "projet_id": project_id
                })
                if res.status_code == 200:
                    show_error("Ajouté aux favoris")
                    self.favori_btn.is_favori = True

        except Exception:
            show_error("Erreur de connexion")

    def display_dispos(self, dispos):
        """Affiche les disponibilités dans une grille"""
        self.dispos_container.clear_widgets()

        # Header
        header = GridLayout(cols=4, size_hint_y=None, height=dp(40), spacing=1)
        header.add_widget(TableCell(text="[b]Type[/b]", markup=True))
        header.add_widget(TableCell(text="[b]Surface[/b]", markup=True))
        header.add_widget(TableCell(text="[b]Prix[/b]", markup=True))
        header.add_widget(TableCell(text="[b]Dispo[/b]", markup=True, size_hint_x=0.5))
        self.dispos_container.add_widget(header)

        # Data rows
        for dispo in dispos:
            row = BoxLayout(size_hint=(1, None), height=dp(40))
            row.add_widget(TableCell(text=dispo['type_lg']))
            row.add_widget(TableCell(text=f"{dispo['superfide_min']}-{dispo['superfide_max']} m²"))
            row.add_widget(TableCell(text=f"{dispo['prix']} MAD"))
            row.add_widget(TableCell(
                text=str(dispo['nombre_disponible']),
                color=(0, 0.7, 0, 1) if dispo['nombre_disponible'] > 0 else (0.8, 0, 0, 1),
                size_hint_x=0.5
            ))
            self.dispos_container.add_widget(row)

class FavoritesScreen(SwipeScreen):
    project_container = ObjectProperty(None)

    def on_enter(self):
        self.load_favorites()

    def open_project_details(self, project_id, code_projet):
        self.manager.current = 'project_details'
        details_screen = self.manager.get_screen('project_details')
        details_screen.load_project_data(project_id, code_projet)

    def load_favorites(self):
        self.project_container.clear_widgets()
        app = App.get_running_app()
        user_id = app.current_user_id

        if not user_id:
            show_error("Connectez-vous pour voir vos favoris")
            return

        try:
            res = requests.get(f"{BASE_URL}/favorites/{user_id}")
            if res.status_code != 200:
                show_error("Erreur lors du chargement des favoris")
                return

            projects = res.json()

            if not projects:
                self.project_container.add_widget(Label(
                    text="You have no favorite Projects for the moment !",
                    size_hint=(1, None),
                    height=dp(50)
                ))
                return

            for project in projects:
                project_id = project['id']
                code_projet = project['code_projet']
                project_name = project['nom_projet']
                image_base64 = project.get('image_base64')

                card = BoxLayout(
                    orientation='vertical',
                    size_hint=(None, None),
                    size=(dp(300), dp(400)),
                    spacing=dp(5),
                    pos_hint={'center_x': 0.5}
                )

                # Image handling
                if image_base64:
                    try:
                        image_data = BytesIO(base64.b64decode(image_base64))
                        img = Image(
                            texture=CoreImage(image_data, ext="jpg").texture,
                            size_hint=(1, None),
                            height=dp(320),
                            fit_mode='contain'
                        )
                    except Exception:
                        img = Image(source='images/default.png')
                else:
                    img = Image(source='images/default.png')

                # Clickable label
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

        except requests.RequestException as e:
            show_error(f"Erreur réseau: {e}")

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

class ProfileScreen(SwipeScreen):
    username_label = ObjectProperty(None)
    email_label = ObjectProperty(None)

    def on_swipe_left(self):
        self.manager.current = 'logdata'

    def on_swipe_right(self):
        self.manager.current = 'favorites'


    def edit_profile(self):
        print("✅ Bouton Edit Profile cliqué")
        self.manager.current = 'edit_profile'

    def on_pre_enter(self):
        user_id = App.get_running_app().current_user_id
        if not user_id:
            self.manager.current = 'login'
            return
        
        try:
            res = requests.get(f"{BASE_URL}/profile/{user_id}")
            if res.status_code == 200:
                data = res.json()
                self.ids.username_label.text = data.get("name", "Unknown")
                self.ids.email_label.text = data.get("email", "")
            else:
                self.ids.username_label.text = "Unknown user"
                self.ids.email_label.text = ""  
        except:
            show_error("Profile error")

class EditProfileScreen(SwipeScreen):
    name_input = ObjectProperty(None)
    phone_input = ObjectProperty(None)
    email_input = ObjectProperty(None)
    password_input = ObjectProperty(None)

    def on_pre_enter(self):
        app = App.get_running_app()
        if not app:
            return
    
        user_id = app.current_user_id
        if not user_id:
            self.manager.current = 'login'
            return

        try:
            res = requests.get(f"{BASE_URL}/profile/{user_id}")
            if res.status_code == 200:
                data = res.json()
                self.ids.name_input.text = data['name']
                self.ids.phone_input.text = data['telephone']
                self.ids.email_input.text = data['email']
            else:
                show_error("Utilisateur non trouvé")
        except Exception as e:
            show_error("Erreur lors du chargement")
            print(e)

    def save_changes(self):
        app = App.get_running_app()
        user_id = app.current_user_id

        name = self.ids.name_input.text.strip()
        phone = self.ids.phone_input.text.strip()
        email = self.ids.email_input.text.strip()
        password = self.ids.password_input.text.strip()

        if not all([name, phone, email]):
            show_error("Tous les champs sauf le mot de passe sont obligatoires")
            return

        if not is_valid_email(email):
            show_error("Email invalide")
            return

        if phone and (not phone.isdigit() or len(phone) < 10):
            show_error("Numéro de téléphone invalide")
            return

        if password:
            is_valid, msg = is_valid_password(password)
            if not is_valid:
                show_error(msg)
                return

        payload = {
            "user_id": user_id,
            "name": name,
            "telephone": phone,
            "email": email,
            "password": password if password else None
        }

        try:
            res = requests.post(f"{BASE_URL}/profile/update", json=payload)
            if res.status_code == 200:
                show_error("Profil mis à jour avec succès")
            else:
                show_error("Erreur de mise à jour")
                print(res.text)
        except Exception as e:
            show_error("Erreur réseau")
            print(e)

class WindowManager(ScreenManager):
    pass

Builder.load_file('login.kv')

sm = WindowManager()
sm.add_widget(LoginWindow(name='login'))
sm.add_widget(SignupWindow(name='signup'))
sm.add_widget(LogDataWindow(name='logdata'))
sm.add_widget(ProjectDetailsWindow(name='project_details'))
sm.add_widget(FavoritesScreen(name='favorites'))
sm.add_widget(ProfileScreen(name='profile'))
sm.add_widget(EditProfileScreen(name='edit_profile'))

class LoginApp(App):
    current_user_id = None
    current_project_id = None
    current_popup = None
    current_code_projet = None

    def dismiss_popup(self):
        if self.current_popup:
            self.current_popup.dismiss()
            self.current_popup = None

    def build(self):
        sm.current = 'login'
        return sm

if __name__ == '__main__':
    try:
        LoginApp().run()
    except KeyboardInterrupt:
        pass
