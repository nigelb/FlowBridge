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

"""Contains many of the required configuration objects."""

from dataclasses import dataclass, field
from typing import Any

from argparseutils.helpers.mqtt import MQTTConnectModel

from flow_bridge.driver.base import BaseStationDriver
from flow_bridge.driver.lookup import lookup_driver
from flow_bridge.event.base import BaseEventDispatcher
from flow_bridge.event.lookup import lookup_dispatcher


@dataclass
class DriverConfig:
    """Define configuration for a station driver.

    Specify the driver implementation by name and provide the
    driver-specific configuration payload.
    """

    name: str
    config: dict[str, Any]

    _class: type[BaseStationDriver] = field(init=False)
    impl: BaseStationDriver = field(init=False)

    def __post_init__(self) -> "DriverConfig":
        """Create the driver class and instance from the configuration.

        Resolve the driver by name and initialize it using the provided
        configuration payload.
        """
        self._class = lookup_driver(self.name)
        self.impl = self._class.load(self.config)
        return self


    @staticmethod
    def load(load_from: dict[str, Any]) -> "DriverConfig":
        """Create a `DriverConfig` object from the config dict.

        :param config: The parameters used to create a `DriverConfig`
        :return: a `DriverConfig` object
        """
        return DriverConfig(
            name=load_from["name"],
            config=load_from["config"],
        )


@dataclass
class BridgeConfig:
    """Define configuration for the FlowBridge.

    Control how MQTT messages are consumed and mapped to a
    configured station driver.
    """

    driver: DriverConfig

    @staticmethod
    def load(load_from: dict[str, Any]) -> "BridgeConfig":
        """Create a `BridgeConfig` object from the config dict.

        :param config: The parameters used to create a `BridgeConfig`
        :return: a `BridgeConfig` object
        """
        return BridgeConfig(
            driver=DriverConfig.load(load_from["driver"]),
        )


@dataclass
class DispatcherConfig:
    """Define configuration for a station driver.

    Specify the driver implementation by name and provide the
    driver-specific configuration payload.
    """

    name: str
    config: dict[str, Any]

    _class: type[BaseEventDispatcher] = field(init=False)
    impl: BaseEventDispatcher = field(init=False)

    def __post_init__(self) -> "DispatcherConfig":
        """Create the driver class and instance from the configuration.

        Resolve the driver by name and initialize it using the provided
        configuration payload.
        """
        self._class = lookup_dispatcher(self.name)
        self.impl = self._class.load(self.config)
        return self

    @staticmethod
    def load(load_from: dict[str, Any]) -> "DispatcherConfig":
        """Create a DispatcherConfig instance from a mapping.

        :param load_from: Mapping containing dispatcher configuration values.
        :return: Initialized DispatcherConfig instance.
        """
        return DispatcherConfig(
            name=load_from["name"],
            config=load_from["config"],
        )


@dataclass
class EventDispatch:
    """Define configuration for event dispatching.

    Specify MQTT subscription topics, connection settings, and the
    dispatcher configuration used to process incoming events.
    """

    subscribe: list[str]
    mqtt: MQTTConnectModel
    dispatcher: DispatcherConfig

    @staticmethod
    def load(load_from: dict[str, Any]) -> "EventDispatch":
        """Create an EventDispatch configuration from a mapping.

        :param load_from: Mapping containing event dispatch configuration.
        :return: Initialized EventDispatch instance.
        """
        return EventDispatch(
            subscribe=load_from.get("subscribe", ["#"]),
            mqtt=MQTTConnectModel.load(load_from["mqtt"]),
            dispatcher=DispatcherConfig.load(load_from["dispatcher"]),
        )

@dataclass
class Configuration:
    """Application configuration for the FlowBridge."""

    event: EventDispatch
    bridge: BridgeConfig

    @staticmethod
    def load(load_from: dict[str, Any]) -> "Configuration":
        """Create a `Configuration` object from the config dict.

        :param config: The parameters used to create a `Configuration`
        :return: a `Configuration` object
        """
        return Configuration(
            event=EventDispatch.load(load_from["event"]),
            bridge=BridgeConfig.load(load_from["bridge"]),
        )
