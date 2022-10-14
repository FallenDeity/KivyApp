from typing import Literal

import requests

from .models import Production


class Produce:

    client: requests.Session

    def __init__(self, session: requests.Session, base_url: str) -> None:
        self.client = session
        self.base_url = f"{base_url}/produce"

    def get_produce(
        self, crop: str | None = None, frequency: Literal["Rabi", "Kharif"] | None = None, avg: float | None = None
    ) -> list[Production]:
        response = self.client.get(
            f"{self.base_url}/filter",
            params={  # type: ignore
                "crop": crop or None,
                "frequency": frequency or None,
                "avg": avg or None,
            },
        )
        try:
            items = [Production(*list(res.values())) for res in response.json()]
            return sorted(items, key=lambda x: sum([value.PRODUCE for value in x.VALUES]), reverse=True)
        except AttributeError:
            return []


def add_ext(session: requests.Session, base_url: str) -> Produce:
    return Produce(session, base_url)
