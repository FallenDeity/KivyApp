import requests

from .models import Plant


class Encyclopedia:

    client: requests.Session
    CATEGORIES: tuple[str, ...] = (
        "kingdoms",
        "divisions",
        "classes",
        "orders",
        "families",
        "genus",
    )

    def __init__(self, session: requests.Session, base_url: str) -> None:
        self.client = session
        self.base_url = f"{base_url}/encyclopedia"

    def get_encyclopedia(self, plant: str) -> Plant | dict:
        response = self.client.get(f"{self.base_url}/search", params={"query": plant}).json()
        res = list(sorted(response, key=lambda x: list(x.values()).count(None)))
        return Plant(**res[0]) if res else {}

    def get_info(self, category: str) -> dict[str, str]:
        response: dict[str, str] = self.client.get(f"{self.base_url}/{category}").json()
        return response


def add_ext(session: requests.Session, base_url: str) -> Encyclopedia:
    return Encyclopedia(session, base_url)
