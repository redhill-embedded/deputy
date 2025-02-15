import time

from deputy.devices import cy4500
from deputy.pdmon import pd_parser

if __name__ == '__main__':
    parser = pd_parser.PD_Parser()
    
    probe = cy4500.CY4500()
    print("Opening probe")
    probe.open()

    version = probe.get_version()
    print(f"Probe version: {version}")

    print("Starting capture")
    probe.start()
    
    print("Reading PD data")
    try:
        
        while True:
            data = probe.get_pd_data()
            if len(data) > 4:
                parser.parse(data)
    except KeyboardInterrupt:
        print("Aborted by user")

    print("Stopping capture")
    probe.stop()