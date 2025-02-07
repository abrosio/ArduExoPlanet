import serial
import time
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, filedialog
from datetime import datetime
import serial.tools.list_ports
import ttkbootstrap as ttkb
import threading
from queue import Queue
from matplotlib.animation import FuncAnimation
import os

times = []
values = []
ser = None
start_time = None
log_directory = None
update_interval = 50
logged_data = []
data_queue = Queue()
previous_value = None

def read_serial_data():
    global previous_value, logged_data
    while ser and ser.is_open:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                current_time = time.time() - start_time
                try:
                    value = float(line)
                    variation = value - previous_value if previous_value is not None else 0
                    previous_value = value
                    data_queue.put((current_time, value, variation))
                    logged_data.append((current_time, value))
                except ValueError:
                    pass
            else:
                time.sleep(0.01)
        except Exception as e:
            print(f"Errore durante la lettura dei dati: {e}")
            break

def update_graph(frame):
    while not data_queue.empty():
        current_time, value, variation = data_queue.get()
        times.append(current_time)
        values.append(value)
        if len(times) > 100:
            times.pop(0)
            values.pop(0)
    line.set_data(times, values)
    ax.relim()
    ax.autoscale_view()
    return line,

def save_log():
    global log_directory, logged_data
    if not log_directory:
        log_directory = filedialog.askdirectory(title="Seleziona la directory di salvataggio")
        if not log_directory:
            print("Errore: Nessuna directory selezionata.")
            return
    filename = os.path.join(log_directory, f"fotoresistenza_log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt")
    try:
        with open(filename, 'w') as f:
            f.write("Tempo (s);  Valore Fotoresistenza\n")
            for t, v in logged_data:
                f.write(f"{t:.2f};       {v:.2f}\n")
        print(f"Log salvato in {filename}")
    except Exception as e:
        print(f"Errore durante il salvataggio del log: {e}")

def start_serial():
    global ser, start_time, previous_value
    port = port_combobox.get()
    baud_rate = int(baud_combobox.get())
    if not port or not baud_rate:
        print("Errore: Selezionare una porta e un baud rate.")
        return
    try:
        ser = serial.Serial(port, baud_rate, timeout=0.1)
        start_time = time.time()
        previous_value = None
        threading.Thread(target=read_serial_data, daemon=True).start()
        start_button.config(text="Ferma", command=stop_serial)
        print("Comunicazione avviata.")
    except Exception as e:
        print(f"Errore durante l'inizializzazione: {e}")

def stop_serial():
    global ser
    if ser and ser.is_open:
        ser.close()
        start_button.config(text="Avvia", command=start_serial)
        print("Comunicazione fermata.")

def get_available_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def update_ports():
    available_ports = get_available_ports()
    if not available_ports:
        print("Errore: Nessuna porta seriale disponibile.")
        return
    port_combobox['values'] = available_ports
    if port_combobox.get() not in available_ports:
        port_combobox.set('')
    if available_ports:
        port_combobox.set(available_ports[0])

def update_plot_speed():
    global update_interval, ani
    try:
        new_interval = int(speed_entry.get())
        if new_interval <= 0:
            raise ValueError("Il valore deve essere positivo.")
        update_interval = new_interval
        ani.event_source.interval = update_interval
        print(f"Velocità del plot impostata su {update_interval} ms")
    except ValueError:
        print("Errore: Inserisci un valore numerico valido per la velocità del plot.")

fig, ax = plt.subplots(figsize=(8, 6))
ax.set_xlabel("Tempo (s)", fontsize=10)
ax.set_ylabel("Luce", fontsize=10)
ax.set_title("ArduExoPlanet Analyzer - Photometry Simulation", fontsize=12)
ax.grid(True)
line, = ax.plot([], [], lw=2)

def reset_plot():
    global times, values, logged_data
    times.clear()
    values.clear()
    logged_data.clear()
    line.set_data([], [])
    ax.relim()
    ax.autoscale_view()
    canvas.draw()

def save_screenshot():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
        title="Scegli dove salvare lo screenshot"
    )
    if file_path:
        try:
            fig.savefig(file_path, dpi=300)
        except Exception as e:
            print(f"Errore durante il salvataggio dello screenshot: {e}")

def start_gui():
    global canvas, root, speed_entry, port_combobox, baud_combobox, start_button, ani
    root = ttkb.Window(themename="superhero")
    root.title("ArduExoPlanet Analyzer 1.0")
    try:
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
        root.iconbitmap(icon_path)
    except Exception as e:
        print(f"Errore durante il caricamento dell'icona: {e}")

    frame_ports = ttk.Frame(root)
    frame_ports.pack(padx=10, pady=10, fill="x")
    tk.Label(frame_ports, text="Seleziona la Porta COM:", font=('Arial', 10)).pack(side="left", padx=5)
    global port_combobox
    port_combobox = ttk.Combobox(frame_ports, width=10, font=('Arial', 10), state="readonly")
    port_combobox.pack(side="left", padx=5)
    scan_button = ttkb.Button(frame_ports, text="Scansiona", command=update_ports, style="TButton", width=12, takefocus=False)
    scan_button.pack(side="left", padx=5)
    tk.Label(frame_ports, text="Seleziona il Baud Rate:", font=('Arial', 10)).pack(side="left", padx=5)
    baud_rates = [9600, 115200, 19200, 38400, 57600, 4800, 250000]
    global baud_combobox
    baud_combobox = ttk.Combobox(frame_ports, values=baud_rates, width=10, font=('Arial', 10), state="readonly")
    baud_combobox.set(9600)
    baud_combobox.pack(side="left", padx=5)

    frame_buttons = ttk.Frame(root)
    frame_buttons.pack(padx=10, pady=10, fill="x")
    global start_button
    start_button = ttkb.Button(frame_buttons, text="Avvia", command=start_serial, style="TButton", width=12, takefocus=False)
    start_button.pack(side="left", padx=5)
    save_button = ttkb.Button(frame_buttons, text="Salva Log", command=save_log, style="TButton", width=12, takefocus=False)
    save_button.pack(side="left", padx=5)
    reset_button = ttkb.Button(frame_buttons, text="Reset Plot", command=reset_plot, style="TButton", width=12, takefocus=False)
    reset_button.pack(side="left", padx=5)
    screenshot_button = ttkb.Button(frame_buttons, text="Screenshot", command=save_screenshot, style="TButton", width=12, takefocus=False)
    screenshot_button.pack(side="left", padx=5)
    tk.Label(frame_buttons, text="Velocità del Plot (ms):", font=('Arial', 10)).pack(side="left", padx=5)
    speed_entry = ttk.Entry(frame_buttons, width=8, font=('Arial', 10))
    speed_entry.insert(0, str(update_interval))
    speed_entry.pack(side="left", padx=5)
    speed_button = ttkb.Button(frame_buttons, text="Aggiorna Velocità", command=update_plot_speed, style="TButton", width=16, takefocus=False)
    speed_button.pack(side="left", padx=5)

    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(padx=20, pady=20)
    
    update_ports()
    
    ani = FuncAnimation(fig, update_graph, interval=update_interval, blit=False)
    
    root.mainloop()

plt.tight_layout(pad=2.0)

start_gui()
