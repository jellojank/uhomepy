"""Example of using the Uhome API to dump the list of devices associated with the user."""
import asyncio
import json
import random
import string
import sys
import time
import urllib
import aiohttp
import webbrowser
sys.path.append("..")
import uhomepy

class UhomeOpenAPI(uhomepy.UhomeOpenAPI):
    """Basic Uhome OpenAPI Implemenation."""

    def __init__(self, session: aiohttp.ClientSession, client_id: str, authorization_code: str) -> None:
        super().__init__(session)
        self._token = None
        self._client_id = client_id
        self._authorization_code = authorization_code

    async def async_get_access_token(self):
        """Gets or refreshes the access token."""
        if self._token is not None and self._token["expires_at"] < time.time():
            data = {
                "grant_type": "refresh_token",
                "client_id": self._client_id,
                "refresh_token": self._token["refresh_token"],
            }
        else:
            data = {
                "grant_type": "authorization_code",
                "client_id": self._client_id,
                "code": self._authorization_code,
            }

        if data:
            async with self._session.post(uhomepy.TOKEN_ENDPOINT, data=data) as response:
                response.raise_for_status()
                token = await response.json()
                if "error" in token:
                    raise ValueError(f"Error retrieving access token: {token['error']}")
                self._token = token
                self._token["expires_at"] = time.time() + self._token["expires_in"]

        return self._token["access_token"]


async def main():
    """Collects information from the user and dumps the device list."""

    session = aiohttp.ClientSession()

    print("Enter Client ID:", end=" ")
    client_id = input()

    print("Enter Client Secret:", end=" ")
    client_secret = input()

    print("Enter RedirectUri:", end=" ")
    redirect_uri = input()

    state = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(30))
    autorization_url = f"{uhomepy.AUTHORIZE_ENDPOINT}?response_type=code&client_id={client_id}&client_secret={client_secret}&scope={uhomepy.API_SCOPE}&redirect_uri={redirect_uri}&state={state}"
    webbrowser.open(autorization_url)

    print("Paste full redirect uri:", end=" ")
    authorization_response = input()

    parsed_url = urllib.parse.urlparse(authorization_response)
    if not parsed_url.query:
        raise ValueError("Authorization response does not contain a query string")

    parsed_query_string = urllib.parse.parse_qs(parsed_url.query)
    if "code" not in parsed_query_string or len(parsed_query_string["code"]) != 1:
        raise ValueError("Authorization response has an invalid code query parameter")
    if "state" not in parsed_query_string or len(parsed_query_string["state"]) != 1:
        raise ValueError("Authorization response has an invalid state query parameter")
    if parsed_query_string["state"][0] != state:
        raise ValueError("Authorization response has an inconsistent state value")
    authorization_code = parsed_query_string["code"][0]

    api = UhomeOpenAPI(session, client_id, authorization_code)
    devices = await api.async_discover_devices()

    print()
    print("=== Uhome Devices ===")
    print(json.dumps(devices, indent=4))

    await session.close()

if __name__ == "__main__":
    asyncio.run(main())
