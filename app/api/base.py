import pathlib

import requests

from .encyclopedia import Encyclopedia
from .lens import Lens
from .prices import Price
from .production import Produce
from .users import Members
from .weather import Weather


class Base:

    users: Members
    weather: Weather
    lens: Lens
    encyclopedia: Encyclopedia
    prices: Price
    production: Produce
    EXTS: list[str] = ["users", "weather", "lens", "prices", "encyclopedia", "production"]
    PATH: pathlib.Path = pathlib.Path(__file__).parent

    def __init__(self) -> None:
        self.client = requests.Session()
        self.base_url = "https://agroindia.herokuapp.com/api/v1"

    def load_extension(self, extension: str) -> None:
        self.__dict__[extension.split(".")[-1]] = __import__(extension, fromlist=["add_ext"]).add_ext(
            self.client, self.base_url
        )
        print(f"🔃 Loaded extension {extension.split('.')[-1]}")
        return

    def _load_extension(self) -> None:
        for ext in self.PATH.iterdir():
            if ext.name[:-3] in self.EXTS:
                self.load_extension(f"app.api.{ext.name[:-3]}")

    def run(self) -> None:
        self._load_extension()
        return None
