import os

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

from .helpers import Settings
from .home import Encyclopedia, Home, Lens, Price, Production, Weather
from .login import LoginWindow, SignupWindow


class Render:

    templates: str = "app/templates"

    def __init__(self) -> None:
        self.screens = ScreenManager()
        self.setup()

    def render(self) -> ScreenManager:
        self.screens.add_widget(LoginWindow(name="login"))
        self.screens.add_widget(SignupWindow(name="signup"))
        self.screens.add_widget(Settings(name="settings"))
        self.screens.add_widget(Home(name="home"))
        self.screens.add_widget(Weather(name="weather"))
        self.screens.add_widget(Lens(name="lens"))
        self.screens.add_widget(Encyclopedia(name="info"))
        self.screens.add_widget(Price(name="prices"))
        self.screens.add_widget(Production(name="production"))
        return self.screens

    def setup(self) -> None:
        for file in os.listdir(self.templates):
            if file.endswith(".kv"):
                Builder.load_file(os.path.join(self.templates, file))
                print(f"✅ Loaded {os.path.join(self.templates, file)}")
        return None
