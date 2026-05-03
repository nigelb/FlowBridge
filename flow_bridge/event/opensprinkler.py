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

"""Event dispatch implementation for Opensprinkler events."""
import json
import logging
from dataclasses import dataclass
from typing import Any

from flow_bridge.event.base import BaseEventDispatcher

logger = logging.getLogger(__name__)


@dataclass
class OpenSprinklerDispatchConfig:
    """Define configuration for the OpenSprinkler event dispatcher.

    Provide settings required to interpret and route OpenSprinkler
    MQTT topics.
    """

    topic_prefix: str

    @staticmethod
    def load(load_from: dict[str, Any]) -> "OpenSprinklerDispatchConfig":
        """Create a configuration instance from a mapping.

        :param load_from: Mapping containing dispatcher configuration values.
        :return: Initialized OpenSprinklerDispatchConfig instance.
        """
        return OpenSprinklerDispatchConfig(
            topic_prefix=load_from["topic_prefix"],
        )


class OpenSprinklerDispatch(BaseEventDispatcher):
    """Dispatch OpenSprinkler events to configured handlers.

    Implement an event dispatcher that interprets OpenSprinkler event
    messages and routes them according to the provided configuration.
    """

    name = "opensprinkler"
    config: OpenSprinklerDispatchConfig

    def __init__(self, config: OpenSprinklerDispatchConfig) -> None:
        """Initialize the OpenSprinkler event dispatcher.

        :param config: Dispatcher configuration defining how events are
            processed and routed.
        """
        super().__init__()
        self.config = config

    def handle_event(self, route: str, payload: bytes) -> None:
        """Handle the opensprinkler event from MQTT."""
        decoded_payload = payload.decode("utf-8")
        topic = self.parse_topic(route)
        if topic.startswith("availability"):
            self.handle_available(topic, decoded_payload)
        elif topic.startswith("station"):
            self.handle_station(topic, decoded_payload)
        else:
            logger.warning("Unknown topic: %s: %s", route, decoded_payload)

    def parse_topic(self, topic: str) -> str:
        """Parse the message topic to know how to route the event."""
        if topic.startswith(self.config.topic_prefix):
            route = topic.replace(self.config.topic_prefix, "")
            if route.startswith("/"):
                route = route[1:]
                logger.info(route)
                return route
        return topic

    def handle_available(self, topic: str, decoded_payload: str) -> None:  # noqa: ARG002
        """Handle the "available" event emitted by Open Sprinkler."""
        logger.info("Station is %s", decoded_payload)

    def handle_station(self, topic: str, decoded_payload: str) -> None:
        """Use the topic to route the decoded_payload to the appropriate station handler."""
        _, station_id = topic.split("/")
        message = json.loads(decoded_payload)
        if message["state"] == 1:
            self.turn_station_on(station_id, message["duration"])
        elif message["state"] == 0:
            self.turn_station_off(station_id, message["duration"])
        else:
            logger.error("Unknown state: %s", message)

    def turn_station_on(self, station_id: str, duration: str) -> None:
        """Pass a turn station on message to the driver implementation."""
        logger.info("Turn station %s on for %i seconds.", station_id, duration)
        self.driver.station_on(int(station_id), int(duration) * 1000)

    def turn_station_off(self, station_id: str, duration: str) -> None:
        """Pass a turn station off message to the driver implementation."""
        logger.info("Turn station %s off. %s", station_id, duration)
        self.driver.station_off(int(station_id))

    @staticmethod
    def load(config: dict[str, Any]) -> "OpenSprinklerDispatch":
        """Create a OpenSprinklerDispatch from the config dict.

        :param config: The paramaters used to create a OpenSprinklerDispatch
        :return: OpenSprinklerDispatch
        """
        return OpenSprinklerDispatch(
            config=OpenSprinklerDispatchConfig.load(config),
        )

