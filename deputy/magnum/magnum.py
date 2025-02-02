
from enum import IntEnum
import struct

from recom import RecomDevice
from recom.util import get_serial_port_list
from recom.exceptions import RecomDeviceException


class MagnumCtrlOpcode(IntEnum):
    POWER_STATE         = 0
    POWER_CTRL          = 1
    TARGET_VOLTAGE      = 2
    TARGET_CURRENT      = 3
    TARGET_PRESENCE     = 4
    TARGET_REFERENCE    = 5
    FUSB303_REGS        = 0xF0

class MagnumPowerCtrl(IntEnum):
    AUTOMATIC   = 0
    FORCE_ON    = 1
    FORCE_OFF   = 2

class MagnumTargetPresence(IntEnum):
    NONE            = 0
    DEBUG_HEADER    = 1
    USB             = 2

class MagnumProbe():
    
    KNOWN_VID_PID = ["2e8a:db60"]
    ITF_ID = 0xDB
    ITF_PROT = 0x00

    def __init__(self):
        try:
            self.device = RecomDevice(id=self.KNOWN_VID_PID[0])
        except RecomDeviceException.AccessDenied:
            raise Exception("Access denied!")
        except Exception as e:
            raise e
        if self.device is None:
            raise Exception("No Magnum device found!")
        self.interface = self.device.getInterfaceHandleFromID((self.ITF_ID, self.ITF_PROT))
        if self.interface is None:
            raise Exception("No Magnum control interface found!")
        
    def get_target_serial_port(self):
        serial_ports = get_serial_port_list(self.device)
        if len(serial_ports) == 1:
            return serial_ports[0]
        elif len(serial_ports) > 1:
            return None
        else:
            return None

    def get_power_state(self) -> bool:
        data = self.interface.controlRead(request=MagnumCtrlOpcode.POWER_STATE)
        power_state, = struct.unpack("<B", data)
        return power_state

    def get_power_ctrl(self) -> MagnumPowerCtrl:
        data = self.interface.controlRead(request=MagnumCtrlOpcode.POWER_CTRL)
        power_ctrl, = struct.unpack("<B", data)
        return power_ctrl

    def set_power_ctrl(self, power_ctrl: MagnumPowerCtrl):
        data = struct.pack("<B", power_ctrl)
        self.interface.controlWrite(request=MagnumCtrlOpcode.POWER_CTRL, data=data)

    def get_target_voltage(self) -> int:
        data = self.interface.controlRead(request=MagnumCtrlOpcode.TARGET_VOLTAGE)
        voltage_mv, = struct.unpack("<H", data)
        return voltage_mv

    def get_target_current(self) -> int:
        data = self.interface.controlRead(request=MagnumCtrlOpcode.TARGET_CURRENT)
        current_ma, = struct.unpack("<H", data)
        return current_ma
    
    def get_target_presence(self) -> MagnumTargetPresence:
        data = self.interface.controlRead(request=MagnumCtrlOpcode.TARGET_PRESENCE)
        presence, = struct.unpack("<B", data)
        return presence
    
    def get_target_reference(self) -> int:
        data = self.interface.controlRead(request=MagnumCtrlOpcode.TARGET_REFERENCE)
        target_vref, = struct.unpack("<H", data)
        return target_vref
    

    def get_fusb303_regs(self):
        return self.interface.controlRead(request=MagnumCtrlOpcode.FUSB303_REGS)

    def set_fusb303_reg(self, reg_addr:int, reg_data:int):
        data = struct.pack("<BB", reg_addr, reg_data)
        self.interface.controlWrite(request=MagnumCtrlOpcode.FUSB303_REGS, data=data)
