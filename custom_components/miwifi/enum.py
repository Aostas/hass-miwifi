"""Enums."""

from __future__ import annotations

from enum import IntEnum, Enum
from .const import (
    ATTR_SWITCH_WIFI_2_4,
    ATTR_SWITCH_WIFI_5_0,
    ATTR_SWITCH_WIFI_5_0_GAME,
)


class Mode(IntEnum):
    def __new__(cls, value: int, phrase: str = "undefined") -> "Mode":
        """New mode.

        :param value: int: mode
        :param phrase: str: phrase
        :return Mode
        """

        obj = int.__new__(cls, value)  # type: ignore
        obj._value_ = value

        obj.phrase = phrase  # type: ignore

        return obj

    def __str__(self) -> str:
        """Serialize to string.

        :return str
        """

        return str(self.value)

    DEFAULT = 0, "default"
    REPEATER = 1, "repeater"
    ACCESS_POINT = 2, "access_point"
    MESH = 9, "mesh"


class Connection(IntEnum):
    def __new__(cls, value: int, phrase: str = "undefined") -> "Connection":
        """New connection.

        :param value: int: mode
        :param phrase: str: phrase
        :return Connection
        """

        obj = int.__new__(cls, value)  # type: ignore
        obj._value_ = value

        obj.phrase = phrase  # type: ignore

        return obj

    def __str__(self) -> str:
        """Serialize to string.

        :return str
        """

        return str(self.value)

    LAN = 0, "Lan"
    WIFI_2_4 = 1, "2.4G"
    WIFI_5_0 = 2, "5G"
    GUEST = 3, "Guest"
    WIFI_5_0_GAME = 6, "5G Game"


class IfName(str, Enum):
    def __new__(cls, value: str, phrase: str = "undefined") -> "IfName":
        """New ifname.

        :param value: str: ifname
        :param phrase: str: phrase
        :return IfName
        """

        obj = str.__new__(cls, value)  # type: ignore
        obj._value_ = value

        obj.phrase = phrase  # type: ignore

        return obj

    def __str__(self) -> str:
        """Serialize to string.

        :return str
        """

        return str(self.value)

    WL0 = "wl0", ATTR_SWITCH_WIFI_5_0
    WL1 = "wl1", ATTR_SWITCH_WIFI_2_4
    WL2 = "wl2", ATTR_SWITCH_WIFI_5_0_GAME


class DeviceAction(IntEnum):
    def __new__(cls, value: int, phrase: str = "undefined") -> "DeviceAction":
        """New device action.

        :param value: int: action
        :param phrase: str: phrase
        :return DeviceAction
        """

        obj = int.__new__(cls, value)  # type: ignore
        obj._value_ = value

        obj.phrase = phrase  # type: ignore

        return obj

    def __str__(self) -> str:
        """Serialize to string.

        :return str
        """

        return str(self.value)

    ADD = 0, "Add"
    MOVE = 1, "Move"
    SKIP = 2, "Skip"