import subprocess
import shutil


class Term:

    def __init__(self, dev_path, baud):
        self.port = dev_path
        self.baud = baud


    def _open_serial_port_terminal(self):
        wait_on_process = False
        if shutil.which('putty'):
            term_str = f"putty {self.port} -serial -sercfg {self.baud},8,n,1,N"
        elif shutil.which('minicom'):
            term_str = f"minicom -D {self.port} -b {self.baud}"
        else:
            print("No terminal program detected. Using pyserial's internal terminal...\n\n")
            term_str = f"python -m serial.tools.miniterm {self.port} {self.baud}"
            wait_on_process = True

        try:
            proc = subprocess.Popen(term_str.split())
            if wait_on_process:
                proc.wait()
        except FileNotFoundError:
            print(f"Error opening port {self.port}")
            return -1
        return 0


    def start(self, term=None):
        return self._open_serial_port_terminal()
