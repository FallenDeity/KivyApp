import textwrap
from threading import Thread
from typing import TYPE_CHECKING, Any

from kivy.clock import mainthread
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, WipeTransition
from kivymd.uix.menu import MDDropdownMenu

from app.api import User
from app.utils import STATES, BlockLabel

if TYPE_CHECKING:
    from app import AgroIndia


class LoginWindow(Screen):

    popup: Popup
    response: bool
    data: dict | str

    def run_thread(self, app: "AgroIndia") -> None:
        app.loader("Logging in...")
        thread = Thread(target=self.check_creds, args=(app,))
        thread.start()
        return None

    def check_creds(self, app: "AgroIndia") -> Any:
        phone = self.ids.phone.text
        password = self.ids.password.text
        response, data = app.api.users.login(phone, password)
        return self.set_vars(response, data, app)

    @mainthread  # type: ignore
    def set_vars(self, response: bool, data: dict | str, app: "AgroIndia") -> None:
        self.response = response
        self.data = data
        return app.deload(self.login, self.response, self.data, app)

    def login(self, response: bool, data: User, app: "AgroIndia") -> None:
        if not response and isinstance(data, str):
            text1, text2 = app.translate("Invalid Login"), app.translate(f"{textwrap.fill(data, 50)}")
            return self.display_invalid_login(text1, text2, app)
        app.user = data
        app.data["user"] = f"{app.user.phone}"
        app.data["password"] = f"{app.user.password}"
        self.manager.transition = WipeTransition()
        self.manager.current = "home"
        return None

    def display_invalid_login(self, title: str, message: str, app: "AgroIndia") -> None:
        font = app.font_regular
        layout = Label(text=message, font_name=font, font_size=20)
        self.popup = Popup(title=title, content=layout, size_hint=(None, None), size=(400, 400), title_font=font)
        self.popup.open()
        return None


class SignupWindow(Screen):

    popup: Popup
    state_menu: MDDropdownMenu
    district_menu: MDDropdownMenu
    states: dict[str, list[str]] = STATES

    def signup(self, app: "AgroIndia") -> None:
        username = self.ids.username.text
        password = self.ids.password.text
        phone = self.ids.phone.text
        state = self.ids.state.text
        district = self.ids.district.text
        if state not in self.states:
            return self.display_invalid_signup(
                app.translate("Invalid State"), app.translate("Invalid state selected"), app
            )
        if district not in self.states[state]:
            return self.display_invalid_signup(
                app.translate("Invalid District"), app.translate("Invalid district selected"), app
            )
        if len(password) < 8:
            return self.display_invalid_signup(
                app.translate("Invalid Signup"), app.translate("Password must be atleast 8 characters long"), app
            )
        response, data = app.api.users.register(phone, username, password, state, district)
        if not response and isinstance(data, str):
            text1, text2 = app.translate("Invalid Signup"), app.translate(f"{textwrap.fill(data, 50)}")
            return self.display_invalid_signup(text1, text2, app)
        self.manager.current = "login"
        return None

    def prepare(self) -> None:
        self.state_menu = MDDropdownMenu(
            items=[
                {
                    "viewclass": "OneLineListItem",
                    "text": state,
                    "on_release": lambda x=state: self.set_state(x),
                }
                for state in self.states
            ],
            width_mult=4,
            caller=self.ids.state,
            position="auto",
        )
        self.district_menu = MDDropdownMenu(
            items=[{"viewclass": "OneLineListItem", "text": "Select a state first"}],
            width_mult=4,
            caller=self.ids.district,
            position="auto",
        )
        return None

    def set_state(self, state: str) -> None:
        self.ids.state.text = state
        self.district_menu = MDDropdownMenu(
            items=[
                {
                    "viewclass": "OneLineListItem",
                    "text": district,
                    "on_release": lambda x=district: self.set_district(x),
                }
                for district in self.states[self.ids.state.text]
            ],
            width_mult=4,
            caller=self.ids.district,
            position="auto",
        )
        self.state_menu.dismiss()
        return None

    def set_district(self, district: str) -> None:
        self.ids.district.text = district
        self.district_menu.dismiss()
        return None

    def display_invalid_signup(self, title: str, message: str, app: "AgroIndia") -> None:
        font = app.font_regular
        layout = BlockLabel(text=message, font_name=font, font_size=20)
        self.popup = Popup(title=title, content=layout, size_hint=(None, None), size=(400, 400), title_font=font)
        self.popup.open()
        return None
