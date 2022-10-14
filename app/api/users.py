import json

import requests

from .models import User


class Members:

    client: requests.Session

    def __init__(self, session: requests.Session, base_url: str) -> None:
        self.client = session
        self.base_url = f"{base_url}/register"

    def get_user(self, phone: int) -> User:
        response = self.client.get(f"{self.base_url}/info", params={"phone_number": phone})
        return User(**response.json())

    def get_message(self, phone: int) -> list[str]:
        response: list[str] = self.client.get(f"{self.base_url}/get_messages", params={"phone_number": phone}).json()["messages"]
        return response

    def seen_message(self, phone: int) -> bool:
        response = self.client.get(f"{self.base_url}/seen_message", params={"phone_number": phone})
        return response.status_code == 200

    @staticmethod
    def extract(response: requests.Response) -> str:
        try:
            details = json.loads(response.text)["detail"]
        except json.decoder.JSONDecodeError:
            details = response.text
        return str(details[0]["msg"]) if isinstance(details, list) else str(details)

    def login(self, phone: int, password: str) -> tuple[bool, str | User]:
        response = self.client.get(
            f"{self.base_url}/login", params={"phone_number": phone, "password": password}  # type: ignore
        )
        if response.status_code != 200:
            return False, self.extract(response)
        return True, self.get_user(phone)

    def register(self, phone: int, name: str, password: str, state: str, district: str) -> tuple[bool, str | User]:
        response = self.client.get(
            f"{self.base_url}/register",
            params={
                "phone_number": phone,
                "name": name,
                "password": password,
                "state": state,
                "district": district,
            },  # type: ignore
        )
        if response.status_code != 200:
            return False, self.extract(response)
        return True, User(**response.json())

    def update_password(self, phone: int, old_password: str, new_password: str) -> tuple[bool, str | User]:
        response = self.client.get(
            f"{self.base_url}/update_password",
            params={"phone_number": phone, "old_password": old_password, "new_password": new_password},  # type: ignore
        )
        if response.status_code != 200:
            return False, self.extract(response)
        return True, User(**response.json())

    def update_location(self, phone: int, state: str, district: str) -> tuple[bool, str | User]:
        response = self.client.get(
            f"{self.base_url}/update_location",
            params={"phone_number": phone, "state": state, "district": district},  # type: ignore
        )
        if response.status_code != 200:
            return False, self.extract(response)
        return True, User(**response.json())

    def params(self) -> dict[str, list[str]]:
        res: dict[str, list[str]] = self.client.get(f"{self.base_url}/reigons").json()
        return res

    def markets(self) -> dict[str, list[str]]:
        res: dict[str, list[str]] = self.client.get(f"{self.base_url}/markets").json()
        return res

    def delete_user(self, phone: int) -> bool:
        response = self.client.get(f"{self.base_url}/delete_user", params={"phone_number": phone})
        return response.status_code == 200


def add_ext(session: requests.Session, base_url: str) -> Members:
    return Members(session, base_url)
