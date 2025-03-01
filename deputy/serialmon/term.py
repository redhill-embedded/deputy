import os
import subprocess
import shutil

class Term:

    terminal_programs = {
        "putty": ["{path}", "-serial", "{port}", "-sercfg", "{baud},{config}"],
        "teraterm": ["{path}", "{port}", "/baud={baud}", "/{config}"],
        "realterm": ["{path}", "/port", "{port}", "/baud", "{baud}"],
        "minicom": ["{path}", "-b", "{baud}", "-D", "{port}"],
        "screen": ["{path}", "{port}", "{baud}"],
        "picocom": ["{path}", "-b", "{baud}", "{port}"],
        "tmux": ["{path}", "new-session", "screen {port} {baud}"],
        "cutecom": ["{path}", "-s", "{port}", "-b", "{baud}"],
        "gtkterm": ["{path}", "-p", "{port}", "-s", "{baud}"],
        "mobaxterm": ["{path}", "-serial", "{port}", "-baudrate", "{baud}"],
        "zoc": ["{path}", "-device", "{port}", "-speed", "{baud}"]
}

    def __init__(self, dev_path, baud, config, term):
        self.port = dev_path
        self.baud = baud
        self.config = config

        if not term:
            self.term = "builtin"
        else:
            if term not in self.terminal_programs:
                raise Exception(f"Terminal program {term} not supported")
            term_list = Term.term_list()
            if term not in term_list:
                raise Exception(f"Terminal program {term} not available")
            self.term = term
            self.term_path = term_list[term]


    def _is_term_available(term: str):
        """Check if a program is installed using shutil and additional methods."""
        # Check if the program is in the PATH
        path = shutil.which(term)
        if path:
            return path

        # Additional checks for Windows
        if os.name == "nt":

            # Common installation paths (Windows-specific)
            windows_possible_paths = {
                "putty": [r"C:\Program Files\PuTTY\putty.exe", r"C:\Program Files (x86)\PuTTY\putty.exe"],
                "kitty": [r"C:\Program Files\KiTTY\kitty.exe"],
                "mobaxterm": [r"C:\Program Files\MobaXterm\MobaXterm.exe"],
                "teraterm": [r"C:\Program Files (x86)\teraterm\ttermpro.exe"],
                "realterm": [r"C:\Program Files\RealTerm\realterm.exe"],
            }

            # Windows registry locations to search
            windows_registry_paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
            ]

            # Check common paths on Windows
            if term in windows_possible_paths:
                for p in windows_possible_paths[term]:
                    if os.path.exists(p):
                        return p

            def check_windows_registry(term_name):
                """Check Windows registry for installed applications."""
                try:
                    import winreg
                    for reg_path in windows_registry_paths:
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                            for i in range(winreg.QueryInfoKey(key)[0]):
                                subkey_name = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, subkey_name) as subkey:
                                    try:
                                        display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                        install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0] if "InstallLocation" in dict(winreg.QueryInfoKey(subkey)) else None
                                        if term_name.lower() in display_name.lower():
                                            return install_location or display_name
                                    except FileNotFoundError:
                                        continue
                except Exception:
                    return None
                return None

            # Check Windows Registry
            registry_path = check_windows_registry(term)
            if registry_path:
                return registry_path

        return None


    @classmethod
    def term_list(cls):
        """Returns a dictionary containg the names and paths of all installed terminal programs"""
        installed_terminal_programs = {}
        for term in cls.terminal_programs:
            path = cls._is_term_available(term)
            if path:
                installed_terminal_programs[term] = path
        # Add the builtin terminal
        installed_terminal_programs["builtin"] = "PySerial builtin"
        return installed_terminal_programs


    def start(self):
        if self.term == "builtin":
            term_str = f"python -m serial.tools.miniterm {self.port} {self.baud}"
            wait_on_process = True
        else:
            term_str = [arg.format(path=self.term_path, baud=self.baud, port=self.port, config=self.config) for arg in self.terminal_programs[self.term]]
            wait_on_process = False

        try:
            proc = subprocess.Popen(term_str)
            if wait_on_process:
                proc.wait()
        except FileNotFoundError:
            print(f"Error opening port {self.port}")
            return -1
        return 0
