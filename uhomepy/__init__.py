
"""Simple Python API wrapper for Uhome Protocol."""

import abc
import uuid
import aiohttp

AUTHORIZE_ENDPOINT = "https://oauth.u-tec.com/authorize"
TOKEN_ENDPOINT = "https://oauth.u-tec.com/token"
API_ENDPOINT = "https://api.u-tec.com"
API_SCOPE = "openapi"

class UhomeOpenAPI(abc.ABC):
    """Abstract class to make authenticated requests."""

    def __init__(self, session: aiohttp.ClientSession, version: str = "1") -> None:
        """Initialize the object."""
        self._session = session
        self._version = version

    @abc.abstractmethod
    async def async_get_access_token(self) -> str:
        """Return a valid access token."""

    async def _async_uhome_openapi_request(
        self, namespace: str, name: str, payload: dict
    ) -> dict:
        """Call the Uhome OpenAPI."""
        access_token = await self.async_get_access_token()
        message_id = str(uuid.uuid4())
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        data = {
            "header": {
                "namespace": namespace,
                "name": name,
                "messageId": message_id,
                "payloadVersion": self._version,
            },
            "payload": payload,
        }

        response = await self._session.post(
            f"{API_ENDPOINT}/action", headers=headers, json=data
        )
        response.raise_for_status()

        json = await response.json()
        if not "header" in json or not "messageId" in json["header"] or json["header"]["messageId"] != message_id:
            raise ValueError("Invalid response from Uhome API")

        return json

    async def async_discover_devices(self) -> dict:
        """Call the discovery API and return the payload as a dictionary."""
        return await self._async_uhome_openapi_request(
            "Uhome.Device", "Discovery", {}
        )

    async def async_update_devices(self, device_ids: list[str]) -> dict:
        """Call the get API and return the payload as a dictionary."""
        payload = {"devices": [{"id": device_id} for device_id in device_ids]}
        return await self._async_uhome_openapi_request(
            "Uhome.Device", "Query", payload
        )

    async def async_lock_devices(self, device_ids: list[str]) -> dict:
        """Call the get API and return the payload as a dictionary."""
        payload = {
            "devices": [
                {"id": device_id, "command": {"capability": "st.lock", "name": "lock"}}
                for device_id in device_ids
            ]
        }
        return await self._async_uhome_openapi_request(
            "Uhome.Device", "Command", payload
        )

    async def async_unlock_devices(self, device_ids: list[str]) -> dict:
        """Call the get API and return the payload as a dictionary."""
        payload = {
            "devices": [
                {
                    "id": device_id,
                    "command": {"capability": "st.lock", "name": "unlock"},
                }
                for device_id in device_ids
            ]
        }
        return await self._async_uhome_openapi_request(
            "Uhome.Device", "Command", payload
        )
