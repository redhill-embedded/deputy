import usb1
import struct

from deputy.devices.pd_probe import PDProbe

class CY4500(PDProbe):
    VID = 0x04B4
    PID = 0xF67E

    EP_OUT_CMD = 0x02
    EP_IN_CC_DATA = 0x81
    EP_IN_MEASURE = 0x83
    EP_IN_CMD_RESP = 0x84

    CMD_START = 16
    CMD_STOP = 3
    CMD_VERSION = 4

    def __init__(self):
        self.usb_ctx = usb1.USBContext().open()
        self.dev = self.usb_ctx.openByVendorIDAndProductID(self.VID, self.PID)
        #dev_list = self.find()
        #if dev_list == []:
        #    raise Exception("No CY4500 device found!")
        #self.dev = dev_list[0]
        self.config = (1 << 0) | (1 << 1) | (1 << 3)
        print(self.config)


    def __del__(self):
        try:
            self.usb_ctx.close()
        except Exception:
            pass


    @classmethod
    def type(self):
        return "CY4500"


    @classmethod
    def find(self, **kwargs) -> list:
        with usb1.USBContext() as ctx:
            dev = ctx.getByVendorIDAndProductID(self.VID, self.PID)
            if dev is not None:
                return [dev]
        return []


    def open(self):
        return
        try:
            self.dev.open()
        except usb1.USBError as e:
            if e.value == -3:
                raise Exception("Access Denied")
            else:
                raise Exception(e)


    def close(self):
        self.dev.close()


    def get_version(self):
        data = struct.pack("<I", self.CMD_VERSION)
        self.dev.bulkWrite(self.EP_OUT_CMD, data, 100)
        return self.dev.bulkRead(self.EP_IN_CMD_RESP, 128, 1000)


    def start(self):
        """Start capturing PD data"""
        data = struct.pack("<II", self.CMD_START, self.config)
        self.dev.bulkWrite(self.EP_OUT_CMD, data, 100)


    def stop(self):
        """Stop capturing PD data"""
        data = struct.pack("<I", self.CMD_STOP)
        self.dev.bulkWrite(self.EP_OUT_CMD, data, 100)


    def get_pd_data(self, timeout=1000):
        """Read PD data from the probe"""
        return self.dev.bulkRead(self.EP_IN_CC_DATA, 512, timeout)
