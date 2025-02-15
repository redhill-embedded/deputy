import enum
import struct

class PD_SOP(enum.IntEnum):
    SOP = 0
    SOP_PRIME = 1
    SOP_DPRIME = 2
    SOP_P_DBG = 3
    SOP_DP_DBG = 4
    HARD_RESET = 5
    CABLE_RESET = 6
    INVALID = 7


class PD_CONTROL_MSG(enum.IntEnum):
    RESERVED0 = 0x00
    GOOD_CRC = 0x01
    GOTO_MIN = 0x02
    ACCEPT = 0x03
    REJECT = 0x04
    PING = 0x05
    PS_RDY = 0x06
    GET_SOURCE_CAP = 0x07
    GET_SINK_CAP = 0x08
    DR_SWAP = 0x09
    PR_SWAP = 0x0A
    VCONN_SWAPP = 0x0B
    WAIT = 0x0C
    SOFT_RESET = 0x0D
    DATA_RESET = 0x0E
    DATA_RESET_COMPLETE = 0x0F
    NOT_SUPPORTED = 0x10
    GET_SOURCE_CAP_EXTENDED = 0x11
    GET_STATUS = 0x12
    FR_SWAP = 0x13
    GET_PPS_STATUS = 0x14
    GET_COUNTRY_CODES = 0x15
    GET_SINK_CAP_EXTENDED = 0x16
    GET_SOURCE_INFO = 0x17
    GET_REVISION = 0x18
    RESERVED1 = 0x19
    RESERVED2 = 0x1A
    RESERVED3 = 0x1B
    RESERVED4 = 0x1C
    RESERVED5 = 0x1D
    RESERVED6 = 0x1E
    RESERVED7 = 0x1F

class PD_DATA_MSG(enum.IntEnum):
    SOURCE_CAPABILITIES = 0x01
    REQUEST = 0x02
    BIST = 0x03
    SINK_CAPABILITIES = 0x04
    BATTERY_STATUS = 0x05
    ALERT = 0x06
    GET_COUNTRY_INFO = 0x07
    ENTER_USB = 0x08
    VENDOR_DEFINED = 0x0F
    
    # USB PD 3.0 specific messages
    CERTIFICATE = 0x09
    GET_BATTERY_CAP = 0x0A
    GET_BATTERY_STATUS = 0x0B
    GET_MANUFACTURER_INFO = 0x0C
    SECURITY_REQUEST = 0x0D
    SECURITY_RESPONSE = 0x0E
    
    # Extended data message types (USB PD 3.0)
    PPS_STATUS = 0x10
    COUNTRY_INFO = 0x11
    COUNTRY_CODES = 0x12
    SINK_CAPABILITIES_EXTENDED = 0x13
    SOURCE_CAPABILITIES_EXTENDED = 0x14
    STATUS = 0x15
    BATTERY_CAPABILITIES = 0x16
    GET_STATUS = 0x17
    FR_SWAP_REQUEST = 0x18

class PD_PORT_POWER_ROLE(enum.IntEnum):
    SINK = 0,
    SOURCE = 1,

class PD_CABLE_PLUG(enum.IntEnum):
    DFP_UFP = 0,
    CABLE_PLUG_VPD = 1

class PD_Parser:

    def __init__(self):
        pass

    def parse(self, data):
        data_len = len(data)
        sop_type = data[0]
        header, = struct.unpack("<H", data[1:3])
        num_data_objects = (header >> 12) & 0x07
        msg_type = header & 0x0F
        print(f"Received {data_len} bytes")
        print(f"\tSOP Type = {PD_SOP(sop_type).name}")
        if (num_data_objects == 0):
            print(f"\tControl message: {PD_CONTROL_MSG(msg_type).name}")
        else:
            print(f"\tData message: {PD_DATA_MSG(msg_type).name}")
        if (header >> 5) & 0x01:
            print("\tFrom DFP")
        else:
            print("\tFrom UFP")
        spec_rev = (header >> 6) & 0x03
        print(f"\tSpec rev = {spec_rev}")
        port_power_role = (header >> 8) & 0x01
        if sop_type == PD_SOP.SOP:
            print(f"\tPort power role = {PD_PORT_POWER_ROLE(port_power_role).name}")
        elif sop_type == PD_SOP.SOP_PRIME or sop_type == PD_SOP.SOP_DPRIME:
            print(f"\tCable plug = {PD_CABLE_PLUG(port_power_role).name}")
        
