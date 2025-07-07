from kivy.app import App
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
    pass

class WindowManager(ScreenManager):
    pass

Builder.load_file('login.kv')
sm = WindowManager()

# Adding screens
sm.add_widget(LoginWindow(name='login'))
sm.add_widget(SignupWindow(name='signup'))
sm.add_widget(LogDataWindow(name='logdata'))

class LoginApp(App):
    current_popup = None  # Add this to store popup reference
    
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