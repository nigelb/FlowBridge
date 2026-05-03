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

"""Command-line entrypoint for the FlowBridge.

Parses CLI arguments, loads configuration, and starts the MQTT bridge
to connect OpenSprinkler events with station drivers.
"""

import logging
from argparse import ArgumentParser
from copy import deepcopy
from pathlib import Path
from typing import Any

from argparseutils.helpers.mqtt import MQTTClientHelper
from argparseutils.helpers.pythonlogging import LoggingHelper
from argparseutils.helpers.utils import add_option
from paho.mqtt.client import Client as MQTTClient
from paho.mqtt.client import ConnectFlags, MQTTMessage, ReasonCode
from paho.mqtt.properties import Properties
from yaml import SafeLoader
from yaml import load as yaml_loader

from flow_bridge.config import Configuration


class OpenSprinklerMQTTBridge:
    """Bridge OpenSprinkler MQTT events to a station driver.

    Subscribe to OpenSprinkler topics and translate incoming messages
    into driver actions via the configured bridge.
    """

    def __init__(self, mqtt_client: MQTTClient, config: Configuration) -> None:
        """Initialize the relay with an MQTT client and bridge configuration.

        :param mqtt_client: Configured MQTT client instance.
        :param bridge: Bridge configuration defining topics and driver.
        """
        self.mqtt_client = mqtt_client
        self.config = config
        self.topics = config.event.subscribe
        self.logger = logging.getLogger(__name__)

    def run(self) -> None:
        """Start the relay and process MQTT messages indefinitely.

        Configure MQTT callbacks, establish the connection, and enter
        the client loop.
        """
        self.logger.info("Starting...")
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_subscribe = self.on_subscribe
        self.mqtt_client.on_message = self.on_message

        MQTTClientHelper.connect(self.mqtt_client)

        self.mqtt_client.loop_forever()

    def on_connect(self, client: MQTTClient, userdata: Any, flags: ConnectFlags, reason: ReasonCode, properties: Properties | None) -> None:  # noqa: ANN401, ARG002
        """MQTT client event handler for connect events."""
        for topic in self.topics:
            client.subscribe(topic)
            self.logger.info("Subscribing to topic: %s", topic)

    def on_subscribe(self, client: MQTTClient, userdata: Any, mid: int, reason: ReasonCode, properties:  Properties | None) -> None:  # noqa: ANN401, ARG002
        """MQTT client event handler for subscribe events."""
        self.logger.info("Subscribed: %s, %s, %s, %s", userdata, mid, reason, properties)

    def on_message(self, client: MQTTClient, userdata: Any, message: MQTTMessage) -> None:  # noqa: ANN401, ARG002
        """MQTT client event handler for messages."""
        self.logger.info("Recieved Message: %s, %s, %s: %s", message.timestamp, userdata, message.topic, message.payload)
        try:
            self.config.event.dispatcher.impl.handle_event(
                route=message.topic,
                payload=message.payload,
            )
        except Exception:
            self.logger.exception("Failed to handle payload: %s", message.payload)




def main() -> None:
    """Entrypoint for Open Sprinkler Bridge."""
    logger = logging.getLogger("Main")
    parser = ArgumentParser("Open Sprinkler Bridge")

    add_option(parser, {}, shard="", name="config", type=Path, help="The path to the configuration file", required=True)
    LoggingHelper.add_parser_options(parser)

    args = parser.parse_args()

    LoggingHelper.init_logging(args)
    logger.critical("Starting FlowBridge Service")

    with args.config.open("r") as reg_in:
        config = yaml_loader(reg_in, Loader=SafeLoader)

    config = Configuration.load(config)
    config.event.dispatcher.impl.set_bridge(config.bridge.driver.impl)

    mqtt_client = MQTTClientHelper.create_client_from_model(config.event.mqtt)
    config.event.mqtt = deepcopy(config.event.mqtt)
    config.event.mqtt.username = "<REDACTED>"
    config.event.mqtt.password = "<REDACTED>"  # noqa: S105 - redacting for logging
    logger.info(config)

    OpenSprinklerMQTTBridge(mqtt_client, config).run()


if __name__ == "__main__":
    main()
