import requests


class Weather:

    client: requests.Session

    def __init__(self, session: requests.Session, base_url: str) -> None:
        self.client = session
        self.base_url = f"{base_url}/weather"

    def forecast(self, phone: int, locations: str = None) -> tuple[list[dict], str]:
        params: dict[str, str | int] = (
            {"phonenumber": phone} if locations is None else {"phonenumber": phone, "location": locations}
        )
        response = self.client.get(f"{self.base_url}/forecast", params=params)
        return response.json()["locations"], response.json()["reslovedAddress"]

    def history(self, phone: int, locations: str = None) -> list[dict]:
        params: dict[str, str | int] = (
            {"phonenumber": phone} if locations is None else {"phonenumber": phone, "location": locations}
        )
        response: dict[str, list[dict]] = self.client.get(f"{self.base_url}/history", params=params).json()
        return response["locations"]

    def cumulative(self, phone: int, locations: str = None) -> tuple[list[dict], str]:
        data1, info1 = self.forecast(phone, locations)
        data2 = self.history(phone, locations)
        return data2 + data1[1:], info1

    def timeline(self, phone: int, locations: str = None) -> dict[str, list[dict]]:
        params: dict[str, str | int] = (
            {"phonenumber": phone} if locations is None else {"phonenumber": phone, "location": locations}
        )
        response = self.client.get(f"{self.base_url}/timeline", params=params)
        data = response.json()["locations"]
        return {"description": data["description"], "timeline": data["hours"], "alerts": data["alerts"]}

    def daily(self, phone: int, location: str | None = None, day: str | None = None) -> dict:
        params: dict[str, str | int] = (
            {"phonenumber": phone} if location is None else {"phonenumber": phone, "location": location}
        )
        params = params if day is None else {**params, "date": day}
        response: dict = self.client.get(f"{self.base_url}/daily", params=params).json()
        return response


def add_ext(session: requests.Session, base_url: str) -> Weather:
    return Weather(session, base_url)
