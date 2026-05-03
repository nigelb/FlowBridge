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

"""Driver implementation for Waveshare RS485 relay modules."""

import logging
from typing import Any

from argparseutils.helpers.modbushelper import ModbusSerialHelper
from pymodbus_waveshare_relay.pdu import WaveshareDecoder, WriteFlashOnSingleCoilResponse

from flow_bridge.driver.base import BaseStationDriver
from flow_bridge.driver.config import ModbusConfig

logger = logging.getLogger(__name__)


class WaveshareRS485(BaseStationDriver):
    """Control stations using a Waveshare RS485 relay via Modbus.

    This driver connects to a Waveshare RS485 relay board over a serial
    Modbus connection and exposes station control through the
    BaseStationDriver interface.
    """

    name = "waveshare"

    def __init__(self, config: ModbusConfig) -> None:
        """Initialize the Waveshare RS485 driver.

        Configure the Modbus serial client using the provided configuration
        and install the Waveshare-specific decoder.

        :param config: Modbus configuration, including serial settings and
            device addressing.
        """
        self.config = config
        self.modbus_client = ModbusSerialHelper.create_modbus_serial_from_model(config.serial)
        self.modbus_client.framer.decoder = WaveshareDecoder(is_server=False)

    def station_on(self, station_id: int, time_on_ms: int | None = None) -> bool:
        """Turn the station station_id on, optionally for time_on_ms milliseconds."""
        response = None
        if time_on_ms is None:
            response = self.modbus_client.write_coil(
                address=station_id,
                value=True,
                device_id=self.config.bus_device_id)
        else:
            response = self.modbus_client.execute(
                no_response_expected=False,
                request=WriteFlashOnSingleCoilResponse(
                    dev_id=self.config.bus_device_id,
                    flash_coil=station_id,
                    on_ms=time_on_ms))
        logger.info("Modbus Response: %s", response)
        return response is not None

    def station_off(self, station_id: int) -> bool:
        """Turn the station station_id off."""
        response = self.modbus_client.write_coil(
            address=station_id,
            value=False,
            device_id=self.config.bus_device_id)
        logger.info("Modbus Response: %s", response)
        return response is not None

    @staticmethod
    def load(config: dict[str, Any]) -> "WaveshareRS485":
        """Create a WaveshareRS485 from the config dict.

        :param config: The paramaters used to create a WaveshareRS485
        :return: WaveshareRS485
        """
        return WaveshareRS485(ModbusConfig.load(config))
