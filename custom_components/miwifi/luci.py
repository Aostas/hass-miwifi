"""Luci API Client."""

from __future__ import annotations

import logging

import hashlib
import random
import time
import uuid
import json

from httpx import AsyncClient, Response, HTTPError
from datetime import timedelta

from .exceptions import LuciConnectionException, LuciTokenException
from .const import (
    DEFAULT_TIMEOUT,
    CLIENT_ADDRESS,
    CLIENT_URL,
    CLIENT_USERNAME,
    CLIENT_LOGIN_TYPE,
    CLIENT_NONCE_TYPE,
    CLIENT_PUBLIC_KEY
)

_LOGGER = logging.getLogger(__name__)


class LuciClient(object):
    """Luci API Client."""

    _client: AsyncClient
    _ip: str = CLIENT_ADDRESS
    _password: str | None = None
    _timeout: int = DEFAULT_TIMEOUT

    _token: str | None = None
    _url: str

    def __init__(
        self,
        client: AsyncClient,
        ip: str = CLIENT_ADDRESS,
        password: str | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize API client.

        :param client: AsyncClient: AsyncClient object
        :param ip: str: device ip address
        :param password: str: device password
        :param timeout: int: Query execution timeout
        """

        if ip.endswith("/"):
            ip = ip[:-1]

        self._client = client
        self._ip = ip
        self._password = password
        self._timeout = timeout

        self._url = CLIENT_URL.format(ip=ip)

    async def login(self) -> dict:
        """Login method

        :return dict: dict with login data.
        """

        nonce: str = self.generate_nonce()
        url: str = "{}/api/xqsystem/login".format(self._url)

        try:
            async with self._client as client:
                response: Response = await client.post(
                    url,
                    data={
                        "username": CLIENT_USERNAME,
                        "logtype": str(CLIENT_LOGIN_TYPE),
                        "password": self.generate_password_hash(nonce, self._password),
                        "nonce": nonce,
                    },
                    timeout=self._timeout
                )

            _LOGGER.debug("Successful request %s: %s", url, response.content)

            data: dict = json.loads(response.content)
        except HTTPError as e:
            _LOGGER.debug("Connection error %r", e)

            raise LuciConnectionException()

        if response.status_code != 200 or "token" not in data:
            raise LuciTokenException()

        self._token = data["token"]

        return data

    async def logout(self) -> None:
        """Logout method"""

        if self._token is None:
            return

        url: str = "{}/;stok={}/web/logout".format(self._url, self._token)

        try:
            async with self._client as client:
                response: Response = await client.get(
                    url,
                    timeout=self._timeout
                )

                _LOGGER.debug(
                    "Successful request %s: %s",
                    url,
                    response.content
                )
        except HTTPError as e:
            _LOGGER.debug("Logout error: %r", e)

    async def get(self, path: str, use_stok: bool = True) -> dict:
        """GET method.

        :param path: str: api method
        :param use_stok: bool: is use stack
        :return dict: dict with api data.
        """

        url: str = "{}/{}api/{}".format(
            self._url,
            ";stok={}/".format(self._token) if use_stok else "",
            path
        )

        try:
            async with self._client as client:
                response: Response = await client.get(url, timeout=self._timeout)

            _LOGGER.debug("Successful request %s: %s", url, response.content)

            data: dict = json.loads(response.content)
        except HTTPError as e:
            _LOGGER.debug("Connection error %r", e)

            raise LuciConnectionException()

        if "code" not in data or data["code"] > 0:
            raise LuciTokenException()

        return data

    async def topo_graph(self) -> dict:
        """misystem/topo_graph method.

        :return dict: dict with api data.
        """

        return await self.get("misystem/topo_graph", False)

    async def init_info(self) -> dict:
        """xqsystem/init_info method.

        :return dict: dict with api data.
        """

        return await self.get("xqsystem/init_info")

    async def status(self) -> dict:
        """misystem/status method.

        :return dict: dict with api data.
        """

        return await self.get("misystem/status")

    async def new_status(self) -> dict:
        """misystem/newstatus method.

        :return dict: dict with api data.
        """

        return await self.get("misystem/newstatus")

    async def mode(self) -> dict:
        """xqnetwork/mode method.

        :return dict: dict with api data.
        """

        return await self.get("xqnetwork/mode")

    async def wifi_status(self) -> dict:
        """xqnetwork/wifi_status method.

        :return dict: dict with api data.
        """

        return await self.get("xqnetwork/wifi_status")

    async def wifi_detail_all(self) -> dict:
        """xqnetwork/wifi_detail_all method.

        :return dict: dict with api data.
        """

        return await self.get("xqnetwork/wifi_detail_all")

    async def wan_info(self) -> dict:
        """xqnetwork/wan_info method.

        :return dict: dict with api data.
        """

        return await self.get("xqnetwork/wan_info")

    async def reboot(self) -> dict:
        """xqsystem/reboot method.

        :return dict: dict with api data.
        """

        return await self.get("xqsystem/reboot")

    async def led(self, state: int | None = None) -> dict:
        """misystem/led method.

        :param state: int|None: on/off state
        :return dict: dict with api data.
        """

        return await self.get("misystem/led{}".format(f"?on={state}" if state is not None else ""))

    async def wifi_turn_on(self, index: int) -> dict:
        """xqnetwork/wifi_up method.

        :param index: int|None: Wifi device index
        :return dict: dict with api data.
        """

        return await self.get(f"xqnetwork/wifi_up?index={index}")

    async def wifi_turn_off(self, index: int) -> dict:
        """xqnetwork/wifi_down method.

        :param index: int: Wifi device index
        :return dict: dict with api data.
        """

        return await self.get(f"xqnetwork/wifi_down?index={index}")

    async def device_list(self) -> dict:
        """misystem/devicelist method.

        :return dict: dict with api data.
        """

        return await self.get("misystem/devicelist")

    async def wifi_connect_devices(self) -> dict:
        """xqnetwork/wifi_connect_devices method.

        :return dict: dict with api data.
        """

        return await self.get("xqnetwork/wifi_connect_devices")

    @staticmethod
    def sha1(key: str) -> str:
        """Generate sha1 by key.

        :param key: str: the key from which to get the hash
        :return str: sha1 from key.
        """

        return hashlib.sha1(key.encode()).hexdigest()

    @staticmethod
    def get_mac_address() -> str:
        """Generate fake mac address.

        :return str: mac address.
        """

        as_hex: str = f"{uuid.getnode():012x}"

        return ":".join(
            as_hex[i: i + 2] for i in range(0, 12, 2)
        )

    def generate_nonce(self) -> str:
        """Generate fake nonce.

        :return str: nonce.
        """

        return "{}_{}_{}_{}".format(
            CLIENT_NONCE_TYPE,
            self.get_mac_address(),
            int(time.time()),
            int(random.random() * 1000)
        )

    def generate_password_hash(self, nonce: str, password: str) -> str:
        """Generate password hash.

        :param nonce: str: nonce
        :param password: str: password
        :return str: sha1 from password and nonce.
        """

        return self.sha1(nonce + self.sha1(password + CLIENT_PUBLIC_KEY))