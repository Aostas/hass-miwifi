"""Self check."""

from __future__ import annotations

import logging
from typing import Final
import urllib.parse

from homeassistant.core import HomeAssistant
import homeassistant.components.persistent_notification as pn
from homeassistant.loader import async_get_integration

from .luci import LuciClient
from .const import DOMAIN, NAME
from .exceptions import LuciError

SELF_CHECK_METHODS: Final = (
    ("xqsystem/login", "🟢"),
    ("xqsystem/init_info", "🟢"),
    ("misystem/status", "status"),
    ("xqnetwork/mode", "mode"),
    ("misystem/topo_graph", "topo_graph"),
    ("xqsystem/check_rom_update", "rom_update"),
    ("xqnetwork/wan_info", "wan_info"),
    ("misystem/led", "led"),
    ("xqnetwork/wifi_detail_all", "wifi_detail_all"),
    ("xqnetwork/wifi_diag_detail_all", "wifi_diag_detail_all"),
    ("xqnetwork/avaliable_channels", "avaliable_channels"),
    ("xqnetwork/wifi_connect_devices", "wifi_connect_devices"),
    ("misystem/devicelist", "device_list"),
    ("xqnetwork/wifiap_signal", "wifi_ap_signal"),
    ("misystem/newstatus", "new_status"),
    ("xqsystem/reboot", "⚪"),
    ("xqsystem/upgrade_rom", "⚪"),
    ("xqsystem/flash_permission", "⚪"),
    ("xqnetwork/set_wifi", "⚪"),
    ("xqnetwork/set_wifi_without_restart", "⚪"),
)

_LOGGER = logging.getLogger(__name__)


async def async_self_check(hass: HomeAssistant, client: LuciClient, model: str) -> None:
    """Self check

    :param hass: HomeAssistant: HomeAssistant object
    :param client: LuciClient: Luci Client
    :param model: str: Router model
    """

    data: dict = {}

    for code, method in SELF_CHECK_METHODS:
        if method in ["🟢", "🔴", "⚪"]:
            data[code] = method

            continue

        action = getattr(client, method)

        if action:
            try:
                await action()
                data[code] = "🟢"
            except LuciError:
                data[code] = "🔴"

    title: str = f"Router {client.ip} not supported.\n\nModel: {model}"

    message: str = "Check list:"

    for method, value in data.items():
        message += f"\n * {method}: {value}"

    integration = await async_get_integration(hass, DOMAIN)

    # fmt: off
    link: str = f"{integration.issue_tracker}/new?title=" \
        + urllib.parse.quote_plus(f"Add supports {model}") \
        + "&body=" \
        + urllib.parse.quote_plus(message)
    # fmt: on

    message = f"{title}\n\n{message}\n\n"

    # fmt: off
    # pylint: disable=line-too-long
    message += \
        f'<a href="{link}" target="_blank">Create an issue with the data from this post to add support</a>'
    # fmt: on

    pn.async_create(hass, message, NAME)
