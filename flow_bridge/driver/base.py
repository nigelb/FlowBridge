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

"""The Super class of drivers."""

from typing import Any, ClassVar


class BaseStationDriver:
    """Abstract Base class for station driver classes.

    Provides drive registration.
    """

    name: ClassVar[str]

    _DRIVER_MAP: ClassVar[dict[str, type["BaseStationDriver"]]] = {}


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

    def station_on(self, station_id: int, time_on_ms: int | None = None) -> bool:
        """Turn the station station_id on, optionally for time_on_ms milliseconds."""
        raise NotImplementedError

    def station_off(self, station_id: int) -> bool:
        """Turn the station station_id off."""
        raise NotImplementedError

    @staticmethod
    def load(config: dict[str, Any]) -> "BaseStationDriver":
        """Construct a configuration object from thr provided config."""
        raise NotImplementedError

    @classmethod
    def lookup(cls, driver_id: str) -> type["BaseStationDriver"]:
        """Return the driver class for the given ID.

        :raises ValueError: If the driver ID is unknown.
        """
        try:
            return cls._DRIVER_MAP[driver_id]
        except KeyError as e:
            msg = f"Unknown driver: {driver_id}"
            raise ValueError(msg) from e
