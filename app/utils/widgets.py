from typing import TYPE_CHECKING, Any, Callable

from kivy.core.window import Window
from kivy.factory import Factory
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, ObjectProperty
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFillRoundFlatIconButton, MDRectangleFlatIconButton, MDRoundFlatButton, MDFloatingActionButton
from kivymd.uix.card import MDCard
from kivymd.uix.fitimage import FitImage
from kivymd.uix.label import MDIcon, MDLabel
from kivymd.uix.swiper import MDSwiperItem
from kivy.garden.matplotlib import FigureCanvasKivyAgg


if TYPE_CHECKING:
    from app import AgroIndia


class Plot(FigureCanvasKivyAgg, MDSwiperItem):
    """Plot widget for matplotlib plots."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.size_hint = (0.9, 0.9)


class BlockLabel(Label):
    scale_factor = 0.9
    factor: list[float] = ListProperty()
    dimension: int = NumericProperty()
    font_size: float

    def on_texture_size(self, *_: str) -> None:
        if not self.factor:
            self.factor = [
                self.font_size / self.texture_size[0],
                self.font_size / self.texture_size[1],
            ]
        if not self.dimension:
            self.dimension = 1 if self.texture_size[0] * self.size[1] < self.texture_size[1] * self.size[0] else 0
        self.font_size = self.size[self.dimension] * self.scale_factor * self.factor[self.dimension]
        return None


class HoverBehavior(object):
    hovered = BooleanProperty(False)
    border_point = ObjectProperty(None)

    def __init__(self, **kwargs: str) -> None:
        self.register_event_type("on_enter")  # type: ignore
        self.register_event_type("on_leave")  # type: ignore
        Window.bind(mouse_pos=self.on_mouse_pos)
        super(HoverBehavior, self).__init__(**kwargs)

    def on_mouse_pos(self, *args: tuple[str]) -> None:
        if not self.get_root_window():  # type: ignore
            return
        pos = args[1]
        inside = self.collide_point(*self.to_widget(*pos))  # type: ignore
        if self.hovered == inside:
            return
        self.border_point = pos
        self.hovered = inside
        match inside:
            case True:
                self.dispatch("on_enter")  # type: ignore
            case _:
                self.dispatch("on_leave")  # type: ignore

    def on_enter(self) -> None:
        pass

    def on_leave(self) -> None:
        pass


Factory.register("HoverBehavior", HoverBehavior)


class BaseShadowWidget(Widget):
    pass


class DeprecatedShadowWidget(MDCard, BaseShadowWidget):
    radius = ListProperty([20, 20, 20, 20])
    pass


class NewShadowWidget(RoundedRectangularElevationBehavior, BaseShadowWidget, MDBoxLayout):
    radius = ListProperty([20, 20, 20, 20])
    pass


class HoverButton(MDRoundFlatButton, HoverBehavior):
    font_name: str
    on_release: Callable[[Any], Any]
    text: str

    def on_enter(self) -> None:
        self.md_bg_color = self.theme_cls.primary_color
        self.text_color = self.theme_cls.bg_dark

    def on_leave(self) -> None:
        self.md_bg_color = self.theme_cls.accent_color
        self.text_color = self.theme_cls.primary_color


class HoverIconButton(MDFloatingActionButton, HoverBehavior):
    pos_hint: dict[str, float]
    pass


class HoverRectangle(MDRectangleFlatIconButton, HoverBehavior):
    pos_hint: dict[str, float]
    pass


class ShadowCard(MDCard, RoundedRectangularElevationBehavior):
    radius = ListProperty([20, 20, 20, 20])
    pass


class Report(MDSwiperItem, NewShadowWidget):
    def __init__(self, data: dict[str, Any], app: "AgroIndia", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.app = app
        self.data = data
        self.elevation = 10
        self.orientation = "vertical"
        self.size_hint = (None, None)
        self.size = (300, 420)
        self.shadow_radius = 10
        self.soft_shadow_cl = self.app.theme_cls.accent_color
        self.hard_shadow_cl = self.app.theme_cls.accent_color
        self.md_bg_color = self.app.theme_cls.accent_color
        self.set_card()

    def stringify(self) -> None:
        self.data = {k: str(v) for k, v in self.data.items()}

    def set_card(self) -> None:
        self.stringify()
        box = MDBoxLayout(orientation="vertical", size_hint=(None, None), size=(300, 420))
        smol_box = MDBoxLayout(orientation="horizontal", size_hint=(None, None), spacing=10, padding=10)
        smol_box.add_widget(MDIcon(icon="clock", size_hint=(None, None), size=(30, 30), pos_hint={"top": 1}))
        smol_box.add_widget(
            MDLabel(
                text=self.data["datetime"],
                font_style="H4",
                bold=True,
                pos_hint={"top": 1},
                size_hint=(None, None),
                size=(200, 30),
            )
        )
        box.add_widget(smol_box)
        box.add_widget(
            FitImage(
                source=f"app/assets/images/icons/{self.data['icon']}.png",
                size_hint=(None, None),
                pos_hint={"top": 1},
                size=(75, 75),
            )
        )
        box.add_widget(
            MDLabel(
                text=self.data.get("description", self.data["conditions"]),
                pos_hint={"top": 1},
                halign="center",
                font_style="H6",
                valign="top",
                italic=True,
                font_size=20,
            )
        )
        smol_box = MDBoxLayout(orientation="horizontal", size_hint=(None, None), spacing=10, padding=10)
        smol_box.add_widget(
            MDFillRoundFlatIconButton(
                text=f"{self.app.translate('Temperature')}:\n {self.data['temp']}°C",
                font_style="H6",
                pos_hint={"top": 1, "left": 1},
                icon="thermometer-lines",
                font_name=self.app.font_regular,
            )
        )
        smol_box.add_widget(
            MDFillRoundFlatIconButton(
                text=f"{self.app.translate('Humidity')}:\n {self.data['humidity']} %",
                font_style="H6",
                pos_hint={"top": 1, "left": 1},
                icon="water-percent",
                font_name=self.app.font_regular,
            )
        )
        box.add_widget(smol_box)
        smol_box = MDBoxLayout(orientation="horizontal", size_hint=(None, None), spacing=10, padding=10)
        smol_box.add_widget(
            MDFillRoundFlatIconButton(
                text=f"{self.app.translate('Wind')}\n{self.app.translate('Speed')}:\n {self.data['windspeed']} km/h",
                font_style="H6",
                pos_hint={"top": 1, "left": 1},
                icon="weather-windy",
                font_name=self.app.font_regular,
            )
        )
        smol_box.add_widget(
            MDFillRoundFlatIconButton(
                text=f"{self.app.translate('Pressure')}:\n {self.data['pressure']} hPa",
                font_style="H6",
                pos_hint={"top": 1, "left": 1},
                icon="gauge",
                font_name=self.app.font_regular,
            )
        )
        box.add_widget(smol_box)
        self.add_widget(box)
        return None
