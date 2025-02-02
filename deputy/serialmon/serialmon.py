import serial
import serial.tools.list_ports

class SerialPort:

    def __init__(self, port_obj):
        self.handle = port_obj

    def __repr__(self):
        return f"Port: {self.handle[0]} - Desc: {self.handle[1]} - HWID: {self.handle[2]}"

    @property
    def path(self):
        """Returns the serial port's port path/description (i.e. COMx, /dev/ttyx)"""
        return self.handle[0]

    @property
    def description(self):
        """Returns the serial port's description string"""
        return self.handle[1]

    @property
    def hwid(self):
        """Returns the serial port's HW ID string"""
        return self.handle[2]

    def is_available(self):
        """
        Returns True if the serial port is available (i.e. not already open)
        """
        try:
            p = serial.Serial(self.path)
            p.close()
            return True
        except serial.SerialException:
            return False
        
    def is_usb(self):
        """Returns True if the serial port is a USB device (i.e connected via USB)"""
        return True if "USB" in self.handle[2] else False
    
    @classmethod
    def get_port_list(cls):
        """Returns a list of all available serial ports on this machine"""
        port_list = []
        sp = serial.tools.list_ports.comports()
        for p in sp:
            port_list.append(SerialPort(p))
        return port_list

    @classmethod
    def validate_port_string(cls, port_str):
        """
        Checks if the provided port string is valid and returns the validated/expanded
        string, which can then be used directly to get a serial port handle.
        If the port is not valid or can't be found, None will be returned.

        Using this functions allows the use of incomplete serial device identifier strings
        such as 'ttyACM0' instead of the full '/dev/ttyACM0'
        """
        pl = cls.get_port_list()
        port_paths = [p.path for p in pl]
        path = [s for s in port_paths if port_str in s]
        if len(path) == 0:
            # No match found!
            return None
        if (len(path)> 1):
            # Multiple matches found. Raise exception
            raise Exception("Multiple matches found")
        return path[0]


class SerialMonitor:

    def __init__(self, *kwargs):
        pass

