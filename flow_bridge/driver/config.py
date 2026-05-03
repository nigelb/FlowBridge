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

"""Configuration objects for the driver package."""

from dataclasses import dataclass
from typing import Any

from argparseutils.helpers.modbushelper import ModbusSerialModel


@dataclass
class ModbusConfig:
    """Define configuration for Modbus communication.

    Provide serial connection parameters and the target device
    address on the Modbus bus.
    """

    serial: ModbusSerialModel
    bus_device_id: int = 1

    @staticmethod
    def load(load_from: dict[str, Any]) -> "ModbusConfig":
        """Create a `ModbusConfig` object from the config dict.

        :param config: The parameters used to create a `ModbusConfig`
        :return: a `ModbusConfig` object
        """
        return ModbusConfig(
            serial=ModbusSerialModel.load(load_from["serial"]),
            bus_device_id=load_from["bus_device_id"],
        )
