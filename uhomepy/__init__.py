"""Simple Python API wrapper for Uhome Protocol.

This module provides an abstract base class `UhomeOpenAPI` to interact with the Uhome API.
It includes methods to authenticate and make requests to the API, such as discovering,
querying, locking, and unlocking devices.

Classes:
    UhomeOpenAPI: Abstract class to make authenticated requests to the Uhome API.

Constants:
    AUTHORIZE_ENDPOINT (str): The endpoint for authorization.
    TOKEN_ENDPOINT (str): The endpoint for token retrieval.
    API_ENDPOINT (str): The base endpoint for the Uhome API.
    API_SCOPE (str): The scope for the API.
"""

import abc
import uuid
import aiohttp

AUTHORIZE_ENDPOINT = "https://oauth.u-tec.com/authorize"
TOKEN_ENDPOINT = "https://oauth.u-tec.com/token"
API_ENDPOINT = "https://api.u-tec.com"
API_SCOPE = "openapi"

class UhomeOpenAPI(abc.ABC):
    """Abstract class to make authenticated requests to the Uhome API.

    Attributes:
        _session (aiohttp.ClientSession): The HTTP session for making requests.
        _version (str): The API version to use.
    """

    def __init__(self, session: aiohttp.ClientSession, version: str = "1") -> None:
        """Initialize the object.

        Args:
            session (aiohttp.ClientSession): The HTTP session for making requests.
            version (str): The API version to use. Defaults to "1".
        """
        self._session = session
        self._version = version

    @abc.abstractmethod
    async def async_get_access_token(self) -> str:
        """Return a valid access token.

        Returns:
            str: The access token.
        """

    async def _async_uhome_openapi_request(
        self, namespace: str, name: str, payload: dict
    ) -> dict:
        """Call the Uhome OpenAPI.

        Args:
            namespace (str): The namespace of the API.
            name (str): The name of the API action.
            payload (dict): The payload for the API request.

        Returns:
            dict: The response from the API.

        Raises:
            ValueError: If the response from the API is invalid.
        """
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
        """Call the discovery API and return the payload as a dictionary.

        Returns:
            dict: The response payload from the discovery API.
        """
        return await self._async_uhome_openapi_request(
            "Uhome.Device", "Discovery", {}
        )

    async def async_query_devices(self, device_ids: list[str]) -> dict:
        """Call the query API and return the payload as a dictionary.

        Args:
            device_ids (list[str]): The list of device IDs to query.

        Returns:
            dict: The response payload from the query API.
        """
        payload = {"devices": [{"id": device_id} for device_id in device_ids]}
        return await self._async_uhome_openapi_request(
            "Uhome.Device", "Query", payload
        )

    async def async_lock_devices(self, device_ids: list[str]) -> dict:
        """Call the lock command API and return the payload as a dictionary.

        Args:
            device_ids (list[str]): The list of device IDs to lock.

        Returns:
            dict: The response payload from the lock command API.
        """
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
        """Call the unlock command API and return the payload as a dictionary.

        Args:
            device_ids (list[str]): The list of device IDs to unlock.

        Returns:
            dict: The response payload from the unlock command API.
        """
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