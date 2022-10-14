from dataclasses import dataclass
from typing import NamedTuple

__all__: tuple[str, ...] = (
    "User",
    "Plant",
    "Prices",
    "Production",
)


class Value(NamedTuple):
    YEAR: int
    PRODUCE: int | float


@dataclass
class Production:
    ID: int
    CROP: str
    FREQUENCY: str
    UNIT: str
    VALUES: list[Value]

    def __init__(self, _id: int, crop: str, freq: str, unit: str, val: list[dict[str, float]]):
        self.ID = _id
        self.CROP = crop
        self.FREQUENCY = freq
        self.UNIT = unit
        self.VALUES = [Value(**value) for value in val]  # type: ignore


@dataclass(frozen=True)
class Prices:
    ID: int
    STATE: str
    DISTRICT: str
    MARKET: str
    COMMODITY: str
    VARIETY: str
    ARRIVAL_DATE: str
    MIN_PRICE: int
    MAX_PRICE: int
    MODAL_PRICE: int


@dataclass(frozen=True)
class User:
    phone: int
    name: str
    password: str
    state: str
    district: str
    message: list[str]
    created_at: float


@dataclass(frozen=True)
class Plant:
    common_name: str | None
    scientific_name: str | None
    author: str | None
    description: str | None
    rank: str | None
    family: str | None
    genus: str | None
    image: str | None
