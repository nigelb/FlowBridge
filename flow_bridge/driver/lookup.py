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

"""Driver registration and lookup."""

from flow_bridge.driver.base import BaseStationDriver

# Importing these classes registers them for BaseStationDriver.lookup
from flow_bridge.driver.waveshare import WaveshareRS485  #noqa: F401


def lookup_driver(driver_name: str) -> type[BaseStationDriver]:
    """Look up a driver based on its driver_name."""
    return BaseStationDriver.lookup(driver_name)

