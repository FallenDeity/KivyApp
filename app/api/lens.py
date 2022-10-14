from typing import Any

import requests


class Lens:

    client: requests.Session

    def __init__(self, session: requests.Session, base_url: str) -> None:
        self.client = session
        self.base_url = f"{base_url}/upload"

    def identify(self, stream: bytes) -> dict[str, Any]:
        response: dict[str, Any] = self.client.post(f"{self.base_url}/identify", files={"file": stream}).json()
        return response

    def diagnose(self, stream: bytes) -> dict[str, Any]:
        response: dict[str, Any] = self.client.post(f"{self.base_url}/diagnose", files={"file": stream}).json()
        return response


def add_ext(session: requests.Session, base_url: str) -> Lens:
    return Lens(session, base_url)
