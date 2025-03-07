import os
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


    @property
    def serialnumber(self):
        """Returns the serial port's serial number"""
        if "SER=" in self.hwid:
            items = self.hwid.split(" ")
            for item in items:
                if "SER=" in item:
                    return item.split("=")[1].strip()
        return None


    def is_available(self) -> bool:
        """
        Returns True if the serial port is available (i.e. not already open)
        """
        if os.name == "posix":
            # Posix systems (i.e. Linux) don't inherently lock serial ports, meaning more than one
            # process could open it. To determine if the port is available (i.e. no process is using
            # it at the moment), we need to check if any processes have opened the port.
            import subprocess
            result = subprocess.run(["lsof", self.path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.returncode != 0  # If return code is 0, something has it open
        else:
            # For all others (i.e. Windows) we simply try to open the port directly. Since the OS
            # locks the port resource when it's in use, opening a port that is already in use will
            # fail.
            try:
                p = serial.Serial(self.path)
                p.close()
                return True
            except serial.SerialException:
                return False


    def is_usb(self) -> bool:
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


    @classmethod
    def get_port_path_from_ID(cls, port_id: int):
        """
        Returns the port path of the specified  serial port in the list of available
        serial ports, where port_id specifies the port.
        """
        pl = cls.get_port_list()
        return pl[port_id].path


    @classmethod
    def get_port_path_from_serialnumber(cls, serialnumber: int):
        """
        Returns the port path of the port with the specified serial number.


        """
        pl = cls.get_port_list()
        p_list = []
        for p in pl:
            if serialnumber in p.serialnumber:
                p_list.append(p)
        if len(p_list) > 1:
            raise Exception("Multiple matches found")
        elif len(p_list) == 0:
            raise Exception("No matches found")
        return p_list[0].path
