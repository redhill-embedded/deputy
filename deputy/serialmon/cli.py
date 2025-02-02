import argparse
from colorama import Fore, Style
import sys
import traceback

from deputy import __version__
from deputy.serialmon.serialmon import SerialPort

def serialmon_cli_print_port_list(verbose, test_availability):
    port_list = SerialPort.get_port_list()
    if not port_list:
        print("No serial ports available.")
        return
    print("Available serial ports:")
    for i, port in enumerate(port_list):
        dev_str = f"{i+1}. {port.path}"
        if test_availability:
            print(dev_str, end='')
            if port.is_available():
                print(Fore.GREEN + "\tAvailable")
            else:
                print(Fore.RED + "\tIn use")
            print(Style.RESET_ALL, end='')
        else:
            print(dev_str)
        if verbose:
            print(f"\r\tDesc: {port.description}\n\r\tHWID: {port.hwid}")


def serialmon_cli_open_port():
    pass

def cli(argv):
    parser = argparse.ArgumentParser(description="Serial monitor CLI.")
    parser.add_argument('--version', action='version', version=__version__,
                                                help="Print package version")
    parser.add_argument('-S', '--serial', help='Serial number to search for')
    parser.add_argument('-p', '--port', help="Serial port path or number")
    parser.add_argument('--baud', type=int, default=115200,
                                                help="Baud rate (default: 115200)")
    parser.add_argument('-v', '--verbose', action='store_true',
                                                help="Print more information")
    parser.add_argument('-t', '--test', action='store_true',
                                                help="Test if serial port is available")

    args, remaining_args = parser.parse_known_args(argv)

    if not args.port or args.serial:
        # If no port or serial was provided, then we simply print the list of serial ports.
        serialmon_cli_print_port_list(args.verbose, args.test)
        return 0
    else:
        # Try to open the serial port
        return serialmon_cli_open_port()

def main(argv=None):
    """Serialmon CLI Main entry point"""

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