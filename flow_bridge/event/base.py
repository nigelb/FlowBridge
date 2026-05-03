# FlowBridge: A flexible bridge between OpenSprinkler MQTT
# and external control interfaces.
# Copyright (C) 2026 NigelB
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License ONLY.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""The Super class of event dispatchers."""

from dataclasses import field
from typing import Any, ClassVar

from flow_bridge.driver.base import BaseStationDriver


class BaseEventDispatcher:
    """Abstract Base class for station driver classes.

    Provides drive registration.
    """

    name: ClassVar[str]

    _DRIVER_MAP: ClassVar[dict[str, type["BaseEventDispatcher"]]] = {}

    driver: BaseStationDriver = field(init=False)


    def __init_subclass__(cls, **kwargs: Any) -> None:  # noqa: ANN401
        """Register subclasses by their declared name."""
        super().__init_subclass__(**kwargs)

        # Skip abstract/base classes without a name
        if not hasattr(cls, "name") or not cls.name:
            return

        if cls.name in cls._DRIVER_MAP:
            msg = f"Duplicate driver name: {cls.name}"
            raise ValueError(msg)

        cls._DRIVER_MAP[cls.name] = cls

    def handle_event(self, route: str, payload: bytes) -> None:
        """Handle an event."""
        raise NotImplementedError

    def set_bridge(self, driver: BaseStationDriver) -> None:
        """Handle an event."""
        self.driver = driver

    @staticmethod
    def load(config: dict[str, Any]) -> "BaseEventDispatcher":
        """Construct a configuration object from thr provided config."""
        raise NotImplementedError

    @classmethod
    def lookup(cls, driver_id: str) -> type["BaseEventDispatcher"]:
        """Return the driver class for the given ID.

        :raises ValueError: If the driver ID is unknown.
        """
        try:
            return cls._DRIVER_MAP[driver_id]
        except KeyError as e:
            msg = f"Unknown driver: {driver_id}"
            raise ValueError(msg) from e
