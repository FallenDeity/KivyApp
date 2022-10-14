import json
import pathlib
import random
from functools import cache
from typing import Any, Callable

from deep_translator import GoogleTranslator
from kivy.base import ExceptionHandler, ExceptionManager, Logger
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.spinner import MDSpinner

from app.api import Base, User
from app.gui import Render
from app.utils import COLORS, LANGUAGES, PALETTE


class AgroIndiaExceptionHandler(ExceptionHandler):
    def handle_exception(self, exception: Exception) -> int:
        print(exception)
        Logger.exception(exception)
        return 1


class AgroIndia(MDApp):

    render: Render
    api: Base
    data: dict[str, str]
    user: User
    loading: MDDialog
    translator: GoogleTranslator
    theme_color: tuple
    about_dialog: MDDialog
    player: Any
    translations: dict[str, dict[str, str]]
    langs: dict[str, str] = LANGUAGES
    path: pathlib.Path = pathlib.Path(__file__).parent / ".data"

    def __init__(self, **kwargs: str) -> None:
        super().__init__(**kwargs)
        self.render = Render()
        self.api = Base()
        self.setup()
        self.lang = self.data["language"]
        self.translator = GoogleTranslator(source="auto", target=self.lang)
        self.sound = True

    def change_lang(self, lang: str) -> None:
        self.lang = lang
        self.translator = GoogleTranslator(source="auto", target=self.lang)
        return None

    @cache
    def translate(self, text: str, dest: str = None) -> str:
        dest = dest or self.lang
        if self.translations.get(dest, {}).get(text):
            return self.translations[dest][text]
        translated: str = self.translator.translate(text, target=dest) if dest != "en" else text
        self.translations.setdefault(dest, {})[text] = translated
        return translated

    def setup(self) -> None:
        if not self.path.exists():
            self.path.mkdir()
        if not (self.path / "users.json").exists():
            (self.path / "users.json").write_text('{"language": "en"}')
        if not (self.path / "translation.json").exists():
            (self.path / "translation.json").write_text("{}")
        self.translations = json.loads((self.path / "translation.json").read_text())
        self.data = json.loads((self.path / "users.json").read_text())
        self.api.run()
        ExceptionManager.add_handler(AgroIndiaExceptionHandler())
        return None

    def generate_theme(self) -> None:
        self.theme_cls.material_style = random.choice(["M2", "M3"])
        self.theme_cls.theme_style = random.choice(["Light", "Dark"])
        c1, c2 = random.sample(COLORS, 2)
        self.theme_cls.primary_palette = c1
        self.theme_cls.accent_palette = c2
        self.theme_color = (0, 0, 0, 1) if self.theme_cls.theme_style == "Dark" else (1, 1, 1, 1)
        return None

    def loader(self, text: str) -> None:
        spinner = MDSpinner(
            size=(30, 30),
            size_hint=(None, None),
            palette=PALETTE,
            determinate_time=0.5,
            active=True,
        )
        self.loading = MDDialog(
            title=text,
            auto_dismiss=False,
            content_cls=spinner,
            radius=[20, 7, 20, 7],
            type="custom",
            size_hint=(0.4, 0.1),
        )
        self.loading.open()
        return None

    def deload(self, callback: Callable = None, *args: Any) -> None:
        if callback:
            callback(*args)
        self.loading.dismiss()
        return None

    def on_stop(self) -> None:
        with open(self.path / "users.json", "w") as f:
            json.dump(self.data, f, indent=4)
        with open(self.path / "translation.json", "w") as f:
            json.dump(self.translations, f, indent=4)
        return None

    def close_dialog(self) -> None:
        self.about_dialog.dismiss()
        return None

    def show_about_dialog(self) -> None:
        self.about_dialog = MDDialog(
            title="About",
            text="AgroIndia is a free and open source app for farmers to get information about"
            " crops, weather, and more.",
            buttons=[
                MDFlatButton(
                    text="Close",
                    on_release=lambda x: self.close_dialog(),
                ),
            ],
        )
        self.about_dialog.open()
        return None

    def random_sound(self) -> None:
        path = pathlib.Path(__file__).parent / "assets" / "audio"
        self.player = SoundLoader.load(str(random.choice(list(path.glob("*.mp3")))))
        self.player.play()
        return None

    def randomize(self) -> None:
        self.random_sound()
        Clock.schedule_once(lambda x: self.randomize(), self.player.length)

    def set_volume(self, volume: float) -> None:
        self.player.volume = volume / 100
        return None

    def set_sound(self) -> None:
        self.sound = not self.sound
        self.music()
        return None

    def music(self) -> None:
        match self.sound:
            case True:
                self.player.play()
            case False:
                self.player.stop()
        return None

    def build(self) -> ScreenManager:
        self.icon = "app/assets/icon.png"
        self.generate_theme()
        self.randomize()
        return self.render.render()

    @property
    def font_black(self) -> str:
        return f"app/assets/fonts/{self.lang}-Black.ttf"

    @property
    def font_regular(self) -> str:
        return f"app/assets/fonts/{self.lang}-Regular.ttf"
