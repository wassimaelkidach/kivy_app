from kivy.app import App
from mysql.connector import Error
import re
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import AsyncImage
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from database import create_connection, validate_login, check_email_exists, create_user

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
    app.current_popup = Popup(title="Database Error",
                            content=content,
                            size_hint=(0.8, 0.4),
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
        if not all([self.email.text, self.pwd.text]):
            show_error("Email and password are required!")
            return

        if not is_valid_email(self.email.text):
            show_error("Please enter a valid email adress")
            return
            
        if validate_login(self.email.text, self.pwd.text):
            self.manager.current = 'logdata'
            self.email.text = ""
            self.pwd.text = ""
        else:
            show_error("Invalid email or password")

class SignupWindow(Screen):
    name2 = ObjectProperty(None)
    email = ObjectProperty(None)
    pwd = ObjectProperty(None)
    
    def signupbtn(self):
        if not all([self.name2.text, self.email.text, self.pwd.text]):
            show_error("All fields are required!")
            return

        if not is_valid_email(self.email.text):
            show_error("Please enter a valid email address")
            return
            
        is_valid, error_msg = is_valid_password(self.pwd.text)
        if not is_valid:
            show_error(error_msg)
            return
    
        if check_email_exists(self.email.text):
            show_error("Email already registered!")
            return
            
        if create_user(self.name2.text, self.email.text, self.pwd.text):
            self.clear_fields()
            self.manager.current = 'login'
        else:
            show_error("Registration failed. Please try again.")

    def clear_fields(self):
        self.name2.text = ""
        self.email.text = ""
        self.pwd.text = ""

class LogDataWindow(Screen):
    project_container = ObjectProperty(None)
    
    def on_enter(self):
        self.load_projects()
    
    def load_projects(self):
        """Load projects with centered cards"""
        self.project_container.clear_widgets()
        
        conn = create_connection()
        if not conn:
            show_error("Database connection failed")
            return
        
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT nom_projet, image_path FROM projets")
            projects = cursor.fetchall()

            # Main container
            main_layout = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=max(dp(350) * len(projects), self.height),
                spacing=dp(20),
                padding=dp(20)            
            )
                        
            for (project_name, image_path) in projects:
                
                # Project card
                card = BoxLayout(
                    orientation='vertical',
                    size_hint=(None, None),
                    size=(dp(300), dp(350)),
                    spacing=dp(5),
                    pos_hint={'center_x': 0.5}
                )
                
                img = AsyncImage(
                    source=image_path if image_path else 'images/default_project.jpg',
                    size_hint=(1, 0.8),
                    fit_mode='contain'
                )
                
                name_label = Label(
                    text=project_name,
                    size_hint=(1, 0.2),
                    font_size='16sp',
                    halign='center'
                )
                
                card.add_widget(img)
                card.add_widget(name_label)
                main_layout.add_widget(card)
            
            self.project_container.add_widget(main_layout)
            
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

class WindowManager(ScreenManager):
    pass

Builder.load_file('login.kv')
sm = WindowManager()

# Adding screens
sm.add_widget(LoginWindow(name='login'))
sm.add_widget(SignupWindow(name='signup'))
sm.add_widget(LogDataWindow(name='logdata'))

class LoginApp(App):
    current_popup = None
    
    def dismiss_popup(self):
        """Safely dismiss the current popup"""
        if self.current_popup:
            self.current_popup.dismiss()
            self.current_popup = None
    
    def build(self):
        Window.size = (400, 600)
        self.current_popup = None
        
        sm.current = 'login'
        return sm

if __name__ == "__main__":
    LoginApp().run()