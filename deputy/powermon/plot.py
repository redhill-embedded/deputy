import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import numpy as np
import platform

from deputy.magnum.magnum import MagnumPowerCtrl

MAX_DATAPOINTS = 200
UPDATE_RATE_HZ = 10

class MagnumVIPlot:
    def __init__(self, tk_root, probe):
        self.probe = probe
        self.root = tk_root
        self.root.title("Target Voltage and Current Plot")

        # Bind the window close event to a handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Create a figure and axis for plotting
        self.fig, self.ax = plt.subplots(2, 1, figsize=(10, 6))

        # Adjust the layout to add space between plots
        self.fig.subplots_adjust(hspace=0.4)

        # Embed the plot in the tkinter window
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Create a frame for the checkboxes and buttons
        self.controls_frame = ttk.Frame(self.root)
        self.controls_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Add checkboxes for automatic y-axis scaling
        self.auto_voltage_var = tk.BooleanVar(value=False)
        self.auto_voltage_check = ttk.Checkbutton(
            self.controls_frame, text="Auto Voltage Range",
            variable=self.auto_voltage_var, command=self.update_plot
        )
        self.auto_voltage_check.pack(side=tk.LEFT, padx=5)

        self.auto_current_var = tk.BooleanVar(value=False)
        self.auto_current_check = ttk.Checkbutton(
            self.controls_frame, text="Auto Current Range",
            variable=self.auto_current_var, command=self.update_plot
        )
        self.auto_current_check.pack(side=tk.LEFT, padx=5)

        # Add buttons to the frame
        self.on_button = ttk.Button(self.controls_frame, text="On", command=self.on_callback)
        self.on_button.pack(side=tk.LEFT, expand=True)

        self.off_button = ttk.Button(self.controls_frame, text="Off", command=self.off_callback)
        self.off_button.pack(side=tk.LEFT, expand=True)

        self.auto_button = ttk.Button(self.controls_frame, text="Auto", command=self.auto_callback)
        self.auto_button.pack(side=tk.LEFT, expand=True)

        self.ax[0].set_title("Voltage")
        self.ax[1].set_title("Current")
        self.ax[0].set_ylim(0, 6)  # Example voltage range
        self.ax[1].set_ylim(0, 5)  # Example current range
        self.ax[0].set_ylabel("Voltage (V)")
        self.ax[1].set_ylabel("Current (A)")
        self.ax[1].set_xlabel("Time (s)")

        self.x_data = []
        self.voltage_data = []
        self.current_data = []

        # Create initial plot lines
        self.voltage_line, = self.ax[0].plot([], [], color='blue')
        self.current_line, = self.ax[1].plot([], [], color='red')

        self.ani = FuncAnimation(self.fig, self.update_plot, interval=UPDATE_RATE_HZ)

    def update_plot(self, frame = None):
        if frame is not None:
            new_time = frame / UPDATE_RATE_HZ
            new_voltage = self.probe.get_target_voltage() / 1000
            new_current = self.probe.get_target_current() / 1000

            self.x_data.append(new_time)
            self.voltage_data.append(new_voltage)
            self.current_data.append(new_current)

            if len(self.x_data) > MAX_DATAPOINTS:  # Keep the last MAX_DATAPOINTS data points
                self.x_data = self.x_data[-MAX_DATAPOINTS:]
                self.voltage_data = self.voltage_data[-MAX_DATAPOINTS:]
                self.current_data = self.current_data[-MAX_DATAPOINTS:]

        # Update the plot lines with the new data
        self.voltage_line.set_data(self.x_data, self.voltage_data)
        self.current_line.set_data(self.x_data, self.current_data)

        # Update the plot limits
        self.ax[0].set_xlim(self.x_data[0], self.x_data[-1])
        self.ax[1].set_xlim(self.x_data[0], self.x_data[-1])

        # Update y-axis range based on checkbox state
        if self.auto_voltage_var.get():
            y_min = min(self.voltage_data)
            y_max = max(self.voltage_data)
            self.ax[0].set_ylim(y_min, y_max)
            #self.ax[0].relim()
            #self.ax[0].autoscale_view()
        else:
            self.ax[0].set_ylim(0, 10)  # Fixed voltage range

        if self.auto_current_var.get():
            y_min = min(self.current_data)
            y_max = max(self.current_data)
            self.ax[1].set_ylim(y_min, y_max)
            #self.ax[1].relim()
            #self.ax[1].autoscale_view()
        else:
            self.ax[1].set_ylim(0, 10)  # Fixed current range

        self.canvas.draw_idle()
    
    def on_callback(self):
        self.probe.set_power_ctrl(MagnumPowerCtrl.FORCE_ON)

    def off_callback(self):
        self.probe.set_power_ctrl(MagnumPowerCtrl.FORCE_OFF)

    def auto_callback(self):
        self.probe.set_power_ctrl(MagnumPowerCtrl.AUTOMATIC)

    def on_closing(self):
        print("Closing the application...")
        self.root.quit()
        self.root.destroy()
        #sys.exit()

def run_plot(probe):
    if platform.system() == 'Darwin':
        plt.switch_backend('macosx')

    root = tk.Tk()
    app = MagnumVIPlot(root, probe)
    root.mainloop()
