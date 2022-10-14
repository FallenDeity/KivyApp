from threading import Thread
from typing import TYPE_CHECKING

from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.transition import MDSlideTransition

from app.utils import STATES, BlockLabel

if TYPE_CHECKING:
    from app import AgroIndia


class SliverToolbar(MDTopAppBar):
    @staticmethod
    def home(app: "AgroIndia") -> None:
        app.root.current = "home"
        return None

    def __init__(self, name: str, app: "AgroIndia", **kwargs: str):
        super().__init__(**kwargs)
        self.app = app
        self.type_height = "medium"
        self.title = name
        self.left_action_items = [["arrow-left", lambda x: self.home(self.app)]]
        self.md_bg_color = app.theme_cls.accent_color
        self.elevation = 10


class SwitchPassword(MDBoxLayout):
    ...


class SwitchLocation(MDBoxLayout):
    def __init__(self) -> None:
        super(SwitchLocation, self).__init__()
        self.state_menu = MDDropdownMenu(
            items=[
                {
                    "viewclass": "OneLineListItem",
                    "text": state,
                    "on_release": lambda x=state: self.set_state(x),
                }
                for state in STATES
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

    def set_state(self, state: str) -> None:
        self.state_menu.dismiss()
        self.ids.state.text = state
        self.district_menu.items = [
            {
                "viewclass": "OneLineListItem",
                "text": district,
                "on_release": lambda x=district: self.set_district(x),
            }
            for district in STATES[state]
        ]
        return None

    def set_district(self, district: str) -> None:
        self.district_menu.dismiss()
        self.ids.district.text = district
        return None


class Settings(Screen):

    langs: MDDropdownMenu
    popup: Popup
    dialog: MDDialog
    state_menu: MDDropdownMenu
    distric_menu: MDDropdownMenu

    def set_lang(self, app: "AgroIndia") -> None:
        self.langs = MDDropdownMenu(
            caller=self.ids.language,
            items=[
                {
                    "viewclass": "OneLineListItem",
                    "text": lang,
                    "on_release": lambda x=lang: self.set_language(x, app),
                }
                for lang in app.langs
            ],
            width_mult=4,
            position="auto",
        )
        self.langs.open()
        return None

    def set_location(self, app: "AgroIndia") -> None:
        state = self.dialog.content_cls.ids.state.text
        district = self.dialog.content_cls.ids.district.text
        self.dialog.dismiss()
        if state not in STATES:
            self.display_invalid_signup("Invalid State", "Invalid state selected", app)
            return None
        if district not in STATES[state]:
            self.display_invalid_signup("Invalid District", "Invalid district selected", app)
            return None
        self.display_invalid_signup("Location Changed", "Restart app to apply changes", app)
        Thread(target=app.api.users.update_location, args=(app.user.phone, state, district)).start()
        return None

    def change_location(self, app: "AgroIndia") -> None:
        self.dialog = MDDialog(
            title="Change location",
            type="custom",
            content_cls=SwitchLocation(),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.dialog.dismiss(),
                ),
                MDFlatButton(
                    text="CHANGE",
                    on_release=lambda x: self.set_location(app),
                ),
            ],
        )
        self.dialog.open()
        return None

    def set_password(self, app: "AgroIndia") -> None:
        old = self.ids.old_password.text
        new = self.ids.new_password.text
        if app.user.password != old:
            self.display_invalid_signup("Incorrect Password", "Incorrect old password", app)
            return None
        if len(new) < 8:
            self.display_invalid_signup("Invalid Password", "Password must be at least 8 characters long", app)
            return None
        Thread(target=app.api.users.update_password, args=(app.user.phone, old, new)).start()
        self.display_invalid_signup("Password Changed", "Your password has been changed", app)
        return None

    def change_password(self, app: "AgroIndia") -> None:
        dialog: MDDialog = MDDialog(
            title="Change Password",
            type="custom",
            content_cls=SwitchPassword(),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: dialog.dismiss(),
                ),
                MDFlatButton(
                    text="CHANGE",
                    on_release=lambda x: self.set_password(app),
                ),
            ],
        )
        dialog.open()
        return None

    def set_language(self, lang: str, app: "AgroIndia") -> None:
        self.langs.dismiss()
        if lang not in app.langs:
            self.display_invalid_signup("Invalid Language", "Invalid language selected", app)
            return None
        self.ids.language.text = lang
        app.data["language"] = app.langs[lang]
        self.display_invalid_signup("Language Changed", f"Restart the app to apply changes", app)
        return None

    def delacc(self, app: "AgroIndia") -> None:
        app.api.users.delete_user(app.user.phone)
        self.manager.transition = MDSlideTransition(direction="right")
        self.manager.current = "login"
        self.display_invalid_signup("Account Deleted", "Your account has been deleted", app)
        return None

    def delete_account(self, app: "AgroIndia") -> None:
        dialog: MDDialog = MDDialog(
            title="Delete Account",
            text="Are you sure you want to delete your account?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: dialog.dismiss(),
                ),
                MDFlatButton(
                    text="DELETE",
                    on_release=lambda x: self.delacc(app),
                ),
            ],
        )
        dialog.open()
        return None

    def display_invalid_signup(self, title: str, message: str, app: "AgroIndia") -> None:
        font = app.font_regular
        layout = BlockLabel(text=app.translate(message), font_name=font, font_size=20)
        self.popup = Popup(
            title=app.translate(title), content=layout, size_hint=(None, None), size=(400, 400), title_font=font
        )
        self.popup.open()
        return None

    def set_rating(self, num: int) -> None:
        self.ids.experience.secondary_text = f"Thank you for rating us {num} stars."
        self.dialog.dismiss()
        return None

    def rate_us(self) -> None:
        icons = [
            "emoticon-devil-outline",
            "emoticon-sad-outline",
            "emoticon-neutral-outline",
            "emoticon-happy-outline",
            "emoticon-excited-outline",
        ]
        stars = [
            MDIconButton(
                id=f"star{i}",
                icon=icon,
                opacity=0.5,
                theme_text_color="Custom",
                text_color=(3 / 255, 252 / 255, 232 / 255, 1),
                pos_hint={"center_x": 0.2 * (i + 1), "center_y": 0.5},
                on_release=lambda x, num=i + 1: self.set_rating(num),
            )
            for i, icon in enumerate(icons)
        ]
        self.dialog = MDDialog(
            title="Rate Us",
            text="Please rate us based on your experience",
            buttons=[
                *stars,
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.dialog.dismiss(),
                ),
                MDFlatButton(
                    text="RATE",
                    on_release=lambda x: self.dialog.dismiss(),
                ),
            ],
        )
        self.dialog.open()
        return None
