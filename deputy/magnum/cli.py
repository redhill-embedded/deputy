import argparse
import os
import platform
import shutil
import sys
import traceback
from time import sleep

from deputy.magnum.magnum import MagnumProbe, MagnumPowerCtrl, MagnumTargetPresence
from deputy.powermon.plot import run_plot
from deputy.serialmon.term import Term
from deputy.util import find_udev_rule
from deputy import __version__
from recom import RecomDevice, RecomDeviceException
from recom.backend.usb import get_vid_pid_on_port

if platform.system() != 'Windows':
    from recom.util import get_drive_mount_point_from_usb_port_path

def __print_udev_instructions__():
    print("A Magnum device was found, but access was denied. This could be because the device is only available to root.")
    print("To solve this, follow these instructions to add a device rule allowing a user to access the Magnum device without root privileges:")
    print("")
    print("1. Create a file called `99-redhill-magnum.rules")
    print("2. Copy the following into this file:")
    print("")
    print("\t# Redhill USB Device Rules for the Magnum probe")
    print("\t# This file should be installed to /etc/udev/rules.d so that you can access the Magnum hardware without being root")
    print("")
    print("\tSUBSYSTEM==\"usb\", ENV{DEVTYPE}==\"usb_device\", ATTR{idVendor}==\"2e8a\", ATTR{idProduct}==\"db60\", MODE=\"0666")
    print("")
    print("3. Copy the file to /etc/udev/rules.d. For example: \"sudo cp 99-redhill-magnum.rules /etc/udev/rules.d\"")
    print("4. Reload the udev rules using \"sudo udevadm control --reload-rules && udevadm trigger\" or reboot your computer")

def probe_info(args):
    try:
        probe = MagnumProbe()
    except Exception as e:
        if "Access denied!" in e.args:
            if not find_udev_rule("2e8a", "db60"):
                __print_udev_instructions__()
            else:
                print("No access despite having a udev rule for Magnum device...")
        else:
            print(e)
    else:
        print(f"HW ID: {probe.device.getHwID()}")
        print(f"HW Version: {probe.device.getHwRev()}")
        print(f"FW Version: {probe.device.getFwRev()}")


def power_ctrl(args):
    probe = MagnumProbe()
    if len(args) == 0:
        power_state = "ON" if probe.get_power_state() else "OFF"
        power_ctrl = probe.get_power_ctrl()
        print(f"Target power: {power_state}")
        print(f"Power control: {MagnumPowerCtrl(power_ctrl).name}")
        print(f"Target voltage: {probe.get_target_voltage()}mV")
        print(f"Target current: {probe.get_target_current()}mA")
        target_presence = probe.get_target_presence()
        print(f"Target presence: {MagnumTargetPresence(target_presence).name}")
        print(f"Target VREF: {probe.get_target_reference()}mV")
    else:
        if isinstance(args[0], int):
            power_ctrl = int(args[0])
        else:
            if args[0] == "off":
                power_ctrl = MagnumPowerCtrl.FORCE_OFF
            elif args[0] == "on":
                power_ctrl = MagnumPowerCtrl.FORCE_ON
            elif args[0] == "auto":
                power_ctrl = MagnumPowerCtrl.AUTOMATIC
            else:
                print(f"Invalid option {args[0]}. Valid options are: off, on, auto")
                return
        try:
            probe.set_power_ctrl(power_ctrl)
        except Exception as exp:
            print(f"Unable to set power control to {args[0]}: {exp}")


def power_plot(args):
    probe = MagnumProbe()
    run_plot(probe)


def serial_monitor(args):
    probe = MagnumProbe()
    probe_serial_port = probe.get_target_serial_port()
    if probe_serial_port != None:
        print(f"Opening serial port {probe_serial_port}")
        term = Term(probe_serial_port, 115200)
        return term.start()
    else:
        print("ERROR: Unable to find probe serial port!")


def update_fw(args):
    if args is None:
        print("Missing binary file paramter")
    binary_file = args[0]

    board = MagnumProbe()
    print(f"Found Magnum probe {board.device.get_serial()}")
    print(f"Current FW Rev = {board.device.getFwRev()}")

    # Check if the passed file is a valid file (does exist)
    file_ref = os.path.join(os.getcwd(), binary_file)
    if not os.path.exists(file_ref):
        print(f"ERROR: Cannot find the file/path {file_ref}")

    # Get port path and reset board
    port_path = board.device._comsBackend.get_device_path()
    old_vp = get_vid_pid_on_port(port_path)

    # Reset board
    print("Rebooting to bootloader... ", end='')
    board.device.reset(2)
    sleep(0.5)

    while True:
        new_vp = get_vid_pid_on_port(port_path)
        if new_vp is not None:
            if new_vp[0] != old_vp[0] or new_vp[1] != old_vp[1]:
                print("DONE")
                print("Found device with VID=%04X, PID=%04X" % (new_vp[0], new_vp[1]))
                break
        sleep(0.1)

    if platform.system() != 'Windows':
        print("Looking for mass storage device... ", end='')
        for i in range(10):
            mp = get_drive_mount_point_from_usb_port_path(port_path, new_vp)
            if mp is not None:
                break
            sleep(1)
        if mp == None:
            print("\nERROR: Bootloader not found")
            return False
        else:
            print(mp)
        print(f"Updating device with {binary_file}")
        if not os.path.exists(mp):
            print(f"ERROR: Bootloader path does not exist ({mp})")
            return False
        dest_ref = os.path.join(mp, binary_file)
        try:
            shutil.copy(file_ref, dest_ref)
        except IOError as exp:
            print(f"ERROR: Failed to copy file {binary_file} ({exp})")
            return False
        print("DONE")
        return True
    else:
        print(f"Please manually copy {binary_file} to the flash driver that just showd up!")
        return True

def fusb303_diag(args):
    probe = MagnumProbe()
    if args is None or len(args) == 0:
        fusb303_regs = probe.get_fusb303_regs()
        if len(fusb303_regs) != 14:
            print(f"ERROR: Expected 14 values, got {len(fusb303_regs)} instead")
            print(f"{fusb303_regs}")
            return
        print("DEVICE_ID:\t0x%02X" % fusb303_regs[0])
        print("DEVICE_TYPE:\t0x%02X" % fusb303_regs[1])
        print("PORT ROLE:\t0x%02X" % fusb303_regs[2])
        print("CONTROL:\t0x%02X" % fusb303_regs[3])
        print("CONTROL1:\t0x%02X" % fusb303_regs[4])
        print("MANUAL:\t\t0x%02X" % fusb303_regs[5])
        print("RESET:\t\t0x%02X" % fusb303_regs[6])
        print("MASK:\t\t0x%02X" % fusb303_regs[7])
        print("MASK1:\t\t0x%02X" % fusb303_regs[8])
        print("STATUS:\t\t0x%02X" % fusb303_regs[9])
        print("STATUS1:\t0x%02X" % fusb303_regs[10])
        print("TYPE:\t\t0x%02X" % fusb303_regs[11])
        print("INTERRUPT:\t0x%02X" % fusb303_regs[12])
        print("INTERRUPT1:\t0x%02X" % fusb303_regs[13])
    else:
        if len(args) != 2:
            print(f"ERROR: Need 2 paramgeters (register address, register data) or nothing (read)")
            return
        probe.set_fusb303_reg(int(args[0], 0), int(args[1], 0))

def cli(argv):
    parser = argparse.ArgumentParser(description="Magnum CLI to interract with debug probe.")
    parser.add_argument("cmd", type=str, help="Command/Action")
    parser.add_argument('--version', action='version', version=__version__,
                                                help="Print package version")
    parser.add_argument('-S', '--serial', help='Serial number to search for')

    args, remaining_args = parser.parse_known_args(argv)

    if args.cmd == "info":
        probe_info(remaining_args)
    elif args.cmd == "power":
        power_ctrl(remaining_args)
    elif args.cmd == "powermon":
        power_plot(remaining_args)
    elif args.cmd == "update":
        update_fw(remaining_args)
    elif args.cmd == "fusb303":
        fusb303_diag(remaining_args)
    elif args.cmd == "serialmon":
        serial_monitor(remaining_args)

def main(argv=None):
    """Magnum CLI Main entry point"""

    if argv==None:
        argv = sys.argv

    try:
        return cli(argv[1:])
    except KeyboardInterrupt:
        print("Aborted by user")
    except Exception as e:
        print("FATAL: ", repr(e))
        print(traceback.format_exc())
        sys.exit(1)


if __name__ == '__main__':
    sys.exit(main())