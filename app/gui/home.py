import csv
import os
import typing
from datetime import datetime, timedelta
from threading import Thread
from typing import TYPE_CHECKING, Any

from kivy.clock import Clock, mainthread
from kivy.metrics import dp
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import Screen
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker
from matplotlib import pyplot as plt

from app.api import Plant, Prices
from app.api import Production as ProductionModel
from app.utils import CROPS, MARKETS, STATES, HoverButton, HoverRectangle, Report, Plot

if TYPE_CHECKING:
    from app import AgroIndia


class Production(Screen):
    data: list[ProductionModel]
    crops: MDDropdownMenu
    seasons: MDDropdownMenu

    def draw_graphs(self) -> None:
        for i in range(len(self.ids.swiper.get_items())):
            self.ids.swiper.remove_widget(self.ids.swiper.get_items()[0])
        plt.style.use("seaborn")
        for num, crop in enumerate(self.data):
            years = {value.YEAR: value.PRODUCE for value in crop.VALUES if value.PRODUCE}
            plt.bar(years.keys(), years.values(), color="yellow", edgecolor="black")
            plt.plot(years.keys(), years.values(), color="red", marker="o")
            plt.title(f"{crop.CROP}")
            plt.xlabel("Years")
            plt.ylabel(f"Production in {crop.UNIT}")
            plt.legend(["Production", "Trend"])
            self.ids.swiper.add_widget(Plot(plt.gcf()))
            plt.close()
            if num == 10:
                break

    def vars(self) -> bool:
        crop = self.ids.crop.text if self.ids.crop.text else None
        if not crop:
            toast("Please select a crop")
            return False
        season = self.ids.frequency.text if self.ids.frequency.text else None
        if season and season not in ["Rabi", "Kharif"]:
            toast("Please select a valid season")
            return False
        avg = self.ids.quantity.text if self.ids.quantity.text else None
        if avg:
            try:
                float(avg)
            except ValueError:
                return False
        return True

    @mainthread  # type: ignore
    def set_data(self, data: list[ProductionModel], app: "AgroIndia") -> None:
        app.loading.dismiss()
        if not data:
            toast("No data found")
            return None
        self.data = data
        self.draw_graphs()
        return None

    def fetch_data(self, app: "AgroIndia") -> typing.Any:
        crop = self.ids.crop.text if self.ids.crop.text else None
        season = self.ids.frequency.text if self.ids.frequency.text else None
        avg = self.ids.quantity.text if self.ids.quantity.text else None
        data = app.api.production.get_produce(crop, season, avg)
        return self.set_data(data, app)

    def run_thread(self, app: "AgroIndia") -> None:
        check = self.vars()
        if not check:
            return None
        app.loader("Loading data...")
        Thread(target=self.fetch_data, args=(app,)).start()
        return None

    def set_crop(self, crop: str) -> None:
        self.ids.crop.text = crop
        self.crops.dismiss()

    def prepare(self) -> None:
        self.crops = MDDropdownMenu(
            caller=self.ids.crop,
            items=[
                {"viewclass": "OneLineListItem", "text": crop, "on_release": lambda x=crop: self.set_crop(x)}
                for crop in CROPS["crops"]
            ],
            width_mult=4,
            position="auto",
        )
        self.seasons = MDDropdownMenu(
            caller=self.ids.frequency,
            items=[
                {"viewclass": "OneLineListItem", "text": season, "on_release": lambda x=season: self.set_season(x)}
                for season in ["Rabi", "Kharif"]
            ],
            width_mult=4,
            position="auto",
        )


class Price(Screen):
    markets: MDDropdownMenu
    crops: MDDropdownMenu
    state_menu: MDDropdownMenu
    district_menu: MDDropdownMenu
    data: list[Prices]
    states: dict[str, list[str]] = STATES
    table: MDDataTable

    def export_data(self) -> None:
        with open(
            f"app/.data/{self.ids.state.text}_{self.ids.district.text}_{self.ids.market.text}_{self.ids.crop.text}.csv",
            "w",
            newline="",
        ) as file:
            writer = csv.DictWriter(file, fieldnames=list(self.data[0].__dict__.keys()))
            writer.writeheader()
            writer.writerows([i.__dict__ for i in self.data])
            toast(f"Exported to {file.name}")
        return None

    @property
    def base_table(self) -> MDDataTable:
        table = MDDataTable(
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            background_color_header="#242629",
            background_color_cell="#5a5c62",
            background_color_selected_cell="#53648f",
            size_hint=(0.9, 0.6),
            use_pagination=True,
            column_data=[
                ("ID", dp(20)),
                ("State", dp(20)),
                ("District", dp(20)),
                ("Market", dp(20)),
                ("Crop", dp(20)),
                ("Variety", dp(20)),
                ("Arrival Date", dp(20)),
                ("Min Price", dp(20)),
                ("Max Price", dp(20)),
                ("Modal Price", dp(20)),
            ],
            row_data=[],
            elevation=5,
        )
        button_box = MDBoxLayout(
            orientation="horizontal", spacing=dp(10), padding=dp(10), size_hint=(1, 1), pos_hint={"right": 1, "top": 0}
        )
        button_box.add_widget(
            HoverRectangle(
                text="Export",
                on_release=lambda x: self.export_data(),  # type: ignore
                pos_hint={"center_x": 0.5},  # type: ignore
                icon="file-export",
            )
        )
        button_box.add_widget(
            HoverRectangle(
                text="Clear",
                on_release=lambda x: self.remove_widget(table),  # type: ignore
                pos_hint={"center_x": 0.5},  # type: ignore
                icon="cancel",
            )
        )
        table.add_widget(button_box)
        return table

    def prepare(self, app: "AgroIndia") -> None:
        self.ids.state.text = app.user.state
        self.ids.district.text = app.user.district
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
            items=[
                {
                    "viewclass": "OneLineListItem",
                    "text": "Select a state first",
                    "on_release": lambda x: None,
                }
            ],
            width_mult=4,
            caller=self.ids.district,
            position="auto",
        )
        return None

    def set_state(self, state: str) -> None:
        self.ids.state.text = state
        self.state_menu.dismiss()
        self.district_menu = MDDropdownMenu(
            caller=self.ids.district,
            items=[
                {
                    "viewclass": "OneLineListItem",
                    "text": district,
                    "on_release": lambda x=district: self.set_district(x),
                }
                for district in self.states[state]
            ],
            width_mult=4,
            position="auto",
        )
        return None

    def set_district(self, district: str) -> None:
        self.ids.district.text = district
        self.district_menu.dismiss()
        self.markets = MDDropdownMenu(
            caller=self.ids.market,
            items=[
                {"viewclass": "OneLineListItem", "text": market, "on_release": lambda x=market: self.set_market(x)}
                for market in MARKETS.get(self.ids.district.text, ["No markets found"])
            ],
            width_mult=4,
            position="auto",
        )
        return None

    def set_market(self, market: str) -> None:
        self.ids.market.text = market
        self.markets.dismiss()
        return None

    def get_crops(self) -> None:
        self.markets = MDDropdownMenu(
            items=[{"viewclass": "OneLineListItem", "text": "Pick your district first", "on_release": lambda x: None}],
            width_mult=4,
            position="auto",
        )
        self.crops = MDDropdownMenu(
            caller=self.ids.crop,
            items=[
                {"viewclass": "OneLineListItem", "text": crop, "on_release": lambda x=crop: self.set_crop(x)}
                for crop in CROPS["crops"]
            ],
            width_mult=4,
            position="auto",
        )
        return None

    def set_crop(self, crop: str) -> None:
        self.ids.crop.text = crop
        self.crops.dismiss()
        return None

    @staticmethod
    def int_check(text: str) -> bool:
        try:
            int(text)
            return True
        except ValueError:
            toast("Invalid input enter valid number")
            return False

    def get_vars(self) -> tuple:
        _id = self.ids._id.text
        state = self.ids.state.text
        district = self.ids.district.text
        market = self.ids.market.text
        crop = self.ids.crop.text
        initial = self.ids.initial.text
        final = self.ids.final.text
        return _id, state, district, market, crop, initial, final

    def check(self) -> bool:
        _id, state, district, market, crop, initial, final = self.get_vars()
        if state and state not in self.states:
            toast("Invalid state")
            return False
        if district and district not in self.states[state]:
            toast("Invalid district")
            return False
        if market and market not in MARKETS.get(district, []):
            toast("Invalid market")
            return False
        if crop and crop not in CROPS["crops"]:
            toast("Invalid crop")
            return False
        if initial and not self.int_check(initial):
            return False
        if final and not self.int_check(final):
            return False
        if _id and not self.int_check(_id):
            return False
        if _id and not (1 <= int(_id) <= 8478):
            toast("Invalid ID")
            return False
        return True

    def get_data(self, app: "AgroIndia") -> typing.Any:
        _id, state, district, market, crop, initial, final = self.get_vars()
        data = app.api.prices.get_price(_id, state, district, market, crop, initial, final)
        return self.set_vars(data, app)

    @mainthread  # type: ignore
    def set_vars(self, data: list[Prices], app: "AgroIndia") -> None:
        app.loading.dismiss()
        self.data = data
        table = self.base_table
        for record in data:
            table.add_row(tuple(map(str, record.__dict__.values())))
        self.add_widget(table)
        return None

    def run_thread(self, app: "AgroIndia") -> None:
        if not self.check():
            return None
        app.loader("Fetching data")
        Thread(target=self.get_data, args=(app,)).start()
        return None


class Encyclopedia(Screen):

    plant: Plant

    def display_info(self) -> None:
        card = self.ids.results
        card.clear_widgets()
        card.add_widget(MDLabel(text=self.plant.common_name, halign="center", font_style="H5"))
        card.add_widget(MDLabel(text=self.plant.scientific_name, halign="center", font_style="H6"))
        card.add_widget(
            AsyncImage(
                source=self.plant.image, size_hint=(None, None), size=(100, 100), pos_hint={"top": 1}
            )
        )
        step = f"{self.plant.rank} {self.plant.family}, {self.plant.genus}"
        card.add_widget(MDLabel(text=step, halign="center", font_style="Subtitle1"))
        url = self.plant.description.split()[-1].replace("[", "").replace("]", "")
        card.add_widget(
            HoverButton(text="More Info", on_release=lambda x: __import__("webbrowser").open(url))  # type: ignore
        )
        card.add_widget(MDLabel(text=self.plant.author, pos_hint={"bottom": 1, "left": 0}, font_style="Caption"))
        return None

    def search(self, app: "AgroIndia") -> None:
        app.loader("Searching...")
        thread = Thread(target=self.get_info, args=(app,))
        thread.start()
        return None

    def get_info(self, app: "AgroIndia") -> Any:
        query = self.ids.search.text
        data = app.api.encyclopedia.get_encyclopedia(query)
        return self.set_vars(data, app)

    @mainthread  # type: ignore
    def set_vars(self, data: Plant, app: "AgroIndia") -> None:
        if not data:
            return app.deload(self.display_error, app)
        self.plant = data
        return app.deload(self.display_info)

    @staticmethod
    def display_error(app: "AgroIndia") -> None:
        toast(app.translate("No results found"))
        return None


class NewLocation(MDBoxLayout):
    pass


class Home(Screen):
    pass


class Lens(Screen):
    images: bytes = None
    files: MDFileManager
    show: bool
    idata: dict
    ddata: dict

    def set_diag_card(self, app: "AgroIndia") -> None:
        data = self.ddata["health_assessment"]
        if not self.ddata["is_plant"]:
            toast(app.translate("No plant found"))
            return None
        if data["is_healthy"]:
            toast(app.translate("Plant is healthy"))
            return None
        diseases = data["diseases"]
        card = self.ids.diag
        card.clear_widgets()
        card.add_widget(
            MDLabel(text=f"Plant is sick", halign="center", font_name=app.font_regular, font_size=30, font_style="H6")
        )
        card.add_widget(
            MDLabel(
                text="Possible diseases:", halign="center", font_name=app.font_regular, font_size=30, font_style="H6"
            )
        )
        for disease in diseases[:3]:
            card.add_widget(
                MDLabel(
                    text=f"Name: {disease['name']}",
                    halign="center",
                    font_name=app.font_regular,
                    font_size=30,
                    font_style="H6",
                )
            )
            card.add_widget(
                MDLabel(
                    text=f"Probability: {disease['probability']}",
                    halign="center",
                    font_name=app.font_regular,
                    font_size=30,
                    font_style="H6",
                )
            )

    def set_info_card(self, app: "AgroIndia") -> None:
        data = self.idata["suggestions"][0]
        detail = data["plant_details"]
        if not data["probability"] > 0.4:
            toast(app.translate("No plant found"))
            return None
        card = self.ids.info
        card.clear_widgets()
        name = detail["common_names"][0] if detail["common_names"] != "None" else ""
        edible = ", ".join(detail["edible_parts"]) if detail["edible_parts"] != "None" else []
        link = (
            detail["wiki_description"]["citation"]
            if detail["wiki_description"] != "None"
            else detail["wiki_image"]["citation"]
        )
        card.add_widget(
            MDLabel(
                text=f"Name: {data['plant_name']} | {name}",
                halign="center",
                font_name=app.font_regular,
                font_size=30,
                font_style="H6",
            )
        )
        card.add_widget(
            MDLabel(
                text=f"Edible: {edible}",
                halign="center",
                font_name=app.font_regular,
                font_size=30,
                font_style="H6",
            )
        )
        card.add_widget(AsyncImage(source=detail["wiki_image"]["value"]))
        link = link if "http" in link else f"https://google.com/search?q={link}"
        card.add_widget(
            HoverButton(
                text=app.translate("More Info"),
                on_release=lambda y: __import__("webbrowser").open(link),  # type: ignore
                font_name=app.font_regular,
                md_bg_color=app.theme_cls.accent_color,
            )
        )
        return None

    def diag(self, app: "AgroIndia") -> None:
        if not self.images:
            toast(app.translate("No image selected"))
            return None
        app.loader("Starting analysis")
        Thread(target=self._diag, args=(app,)).start()
        return None

    def info(self, app: "AgroIndia") -> None:
        if not self.images:
            toast(app.translate("No image selected"))
            return None
        app.loader("Starting analysis")
        Thread(target=self._info, args=(app,)).start()
        return None

    def _info(self, app: "AgroIndia") -> None:
        res = app.api.lens.identify(self.images)
        self.set_info(res, app)
        return None

    def _diag(self, app: "AgroIndia") -> None:
        res = app.api.lens.diagnose(self.images)
        self.set_diag(res, app)
        return None

    @mainthread  # type: ignore
    def set_diag(self, data: dict, app: "AgroIndia") -> None:
        self.ddata = data
        app.deload(self.set_diag_card, app)
        return None

    @mainthread  # type: ignore
    def set_info(self, data: dict, app: "AgroIndia") -> None:
        self.idata = data
        app.deload(self.set_info_card, app)
        return None

    def stream(self) -> None:
        camera = self.ids.capture
        camera.play = True
        Clock.schedule_interval(self.update, 1 / 30)
        return None

    def update(self, *_args: str) -> None:
        frame = self.ids.image
        camera = self.ids.capture
        if camera.texture:
            frame.texture = camera.texture
        return None

    def capture(self, app: "AgroIndia") -> None:
        camera = self.ids.capture
        path = f"app/.data/{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        camera.export_to_png(path)
        self.ids.fit_image.source = path
        with open(path, "rb") as f:
            self.images = f.read()
        toast(app.translate("Image captured"))
        return None

    def open_manager(self) -> None:
        self.files = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            ext=[".jpg", ".jpeg", ".png"],
            show_hidden_files=True,
        )
        self.files.show(os.path.expanduser("~"))
        self.show = True

    def select_path(self, path: str) -> None:
        with open(path, "rb") as f:
            self.images = f.read()
        self.ids.fit_image.source = path
        self.exit_manager()
        toast(path)
        return None

    def exit_manager(self, *_args: Any) -> None:
        self.files.close()
        self.show = False
        return None


class Weather(Screen):
    location: str = None
    weather: dict = None
    dialog: MDDialog
    app: "AgroIndia"

    def go_home(self) -> None:
        self.manager.current = "home"

    def update_widgets(self, app: "AgroIndia") -> None:
        swiper = self.ids.swiper
        for i in range(len(swiper.get_items())):
            swiper.remove_widget(swiper.get_items()[0])
        days = self.weather["days"][0]
        hours = days["hours"]
        swiper.add_widget(Report(days, app))
        for hour in hours:
            swiper.add_widget(Report(hour, app))
        return None

    def run_thread(self, app: "AgroIndia", day: str = None, reset: bool = False) -> None:
        self.app = app
        if self.weather and not reset:
            return None
        app.loader("Loading weather...")
        thread = Thread(target=self.get_weather, args=(app, day))
        thread.start()
        return None

    @mainthread  # type: ignore
    def set_vars(self, data: dict, app: "AgroIndia") -> None:
        self.weather = data
        app.deload(self.update_widgets, app)
        return None

    def get_weather(self, app: "AgroIndia", day: str | None = None) -> Any:
        times = app.api.weather.daily(
            app.user.phone, self.location or f"{app.user.state}, {app.user.district}", day or None
        )
        return self.set_vars(times, app)

    def set_location(self, app: "AgroIndia") -> None:
        self.location = self.dialog.content_cls.ids.location.text
        self.ids.locationbutton.text = self.location
        self.dialog.dismiss()
        return self.run_thread(app)

    def set_new_location(self, app: "AgroIndia") -> None:
        self.dialog = MDDialog(
            title="Set Location",
            text="Enter the location you want to set",
            size_hint=(0.8, 0.3),
            type="custom",
            content_cls=NewLocation(),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    text_color=app.theme_cls.primary_color,
                    on_release=lambda x: self.dialog.dismiss(),
                ),
                MDFlatButton(
                    text="SET",
                    text_color=app.theme_cls.primary_color,
                    on_release=lambda x: self.set_location(app),
                ),
            ],
        )
        self.dialog.open()
        return None

    def on_save(self, _instance: MDDatePicker, value: str, _date_range: list[datetime]) -> None:
        self.run_thread(self.app, day=value, reset=True)
        return None

    def on_date(self) -> None:
        date_dialog = MDDatePicker(
            min_date=datetime.date(datetime.now() - timedelta(days=365)),
            max_date=datetime.date(datetime.now() + timedelta(days=15)),
        )
        date_dialog.bind(on_save=self.on_save, on_cancel=lambda *x: None)
        date_dialog.open()
        return None
