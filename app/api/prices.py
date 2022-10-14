import requests

from .models import Prices


class Price:

    client: requests.Session

    def __init__(self, session: requests.Session, base_url: str) -> None:
        self.client = session
        self.base_url = f"{base_url}/prices"

    def get_price(
        self,
        _id: int | None = None,
        state: str | None = None,
        district: str | None = None,
        market: str | None = None,
        commodity: str | None = None,
        initial: int | None = None,
        final: int | None = None,
    ) -> list[Prices]:
        response = self.client.get(
            f"{self.base_url}/filter",
            params={  # type: ignore
                "id": _id if _id else None,
                "state": state if state else None,
                "district": district if district else None,
                "market": market if market else None,
                "commodity": commodity if commodity else None,
                "initial": initial if initial else None,
                "final": final if final else None,
            },
        )
        return list(sorted([Prices(**res) for res in response.json()], key=lambda x: x.MODAL_PRICE))


def add_ext(session: requests.Session, base_url: str) -> Price:
    return Price(session, base_url)
