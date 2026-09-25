import os
import sys
import threading
import time
from collections import deque
from datetime import datetime
from queue import Empty, Queue

import serial
import serial.tools.list_ports
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog,
    QHBoxLayout, QLabel, QLineEdit, QMainWindow, QPushButton, QVBoxLayout, QWidget,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

PLOT_POINTS = 100
# Conserva alcuni campioni recenti per aggiornare il grafico al cambio del filtro.
RECENT_RAW_POINTS = 5000
BAUD_RATES = (9600, 115200, 19200, 38400, 57600, 4800, 250000)


class Analyzer(QMainWindow):
    serial_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('ArduExoPlanet Analyzer 1.0')
        icon = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
        if os.path.isfile(icon):
            self.setWindowIcon(QIcon(icon))

        self.port = None
        self.reader = None
        self.stop_event = None
        self.started = None
        self.log_directory = None
        self.log_data = []
        self.log_lock = threading.Lock()
        self.incoming = Queue()
        self.recent_raw = deque(maxlen=RECENT_RAW_POINTS)
        self.times = deque(maxlen=PLOT_POINTS)
        self.values = deque(maxlen=PLOT_POINTS)
        self.last_plotted_value = None
        self.closing = False

        self.setStyleSheet('''
            QWidget { background: #243746; color: #e6edf3; font-size: 12px; }
            QComboBox, QLineEdit, QDoubleSpinBox {
                background: #172a38; color: #f2f6fa; border: 1px solid #557085;
                border-radius: 4px; padding: 5px;
            }
            QComboBox QAbstractItemView { background: #172a38; color: #f2f6fa; }
            QPushButton { background: #426173; border: 1px solid #668396;
                border-radius: 5px; padding: 6px 10px; }
            QPushButton:hover { background: #55798e; }
            QPushButton#start { background: #188754; border-color: #25a66b; }
            QPushButton#start:hover { background: #1ca767; }
            QCheckBox { spacing: 6px; }
        ''')
        main = QWidget(self)
        self.setCentralWidget(main)
        layout = QVBoxLayout(main)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)
        port_row = QHBoxLayout()
        port_row.setSpacing(10)
        layout.addLayout(port_row)
        port_row.addWidget(QLabel('Seleziona la Porta COM:'))
        self.port_combo = QComboBox()
        port_row.addWidget(self.port_combo)
        scan = QPushButton('Scansiona')
        scan.clicked.connect(self.update_ports)
        port_row.addWidget(scan)
        port_row.addSpacing(14)
        port_row.addWidget(QLabel('Seleziona il Baud Rate:'))
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(map(str, BAUD_RATES))
        self.baud_combo.setCurrentText('250000')
        port_row.addWidget(self.baud_combo)
        port_row.addStretch()

        button_row = QHBoxLayout()
        button_row.setSpacing(10)
        layout.addLayout(button_row)
        self.start_button = QPushButton('Avvia')
        self.start_button.setObjectName('start')
        self.start_button.clicked.connect(self.toggle_serial)
        button_row.addWidget(self.start_button)
        for title, handler in (
            ('Salva Log', self.save_log), ('Reset Plot', self.reset_plot),
            ('Screenshot', self.save_screenshot),
        ):
            button = QPushButton(title)
            button.clicked.connect(handler)
            button_row.addWidget(button)
        button_row.addSpacing(30)
        button_row.addStretch(1)
        button_row.addWidget(QLabel('Velocità del Plot (ms):'))
        self.speed_entry = QLineEdit('50')
        self.speed_entry.setFixedWidth(65)
        button_row.addWidget(self.speed_entry)
        speed_button = QPushButton('Aggiorna Velocità')
        speed_button.clicked.connect(self.update_plot_speed)
        button_row.addWidget(speed_button)
        button_row.addSpacing(150)

        # Terza riga: opzioni del filtro, sotto ai controlli di acquisizione.
        filter_row = QHBoxLayout()
        filter_row.setSpacing(12)
        layout.addLayout(filter_row)
        self.filter_check = QCheckBox('Attiva filtro')
        filter_row.addWidget(self.filter_check)
        filter_row.addSpacing(16)
        filter_row.addWidget(QLabel('Soglia (variazione minima):'))
        self.threshold = QDoubleSpinBox()
        self.threshold.setFixedWidth(105)
        self.threshold.setRange(0.0, 1_000_000.0)
        self.threshold.setDecimals(2)
        self.threshold.setSingleStep(0.5)
        self.threshold.setValue(5.0)
        filter_row.addWidget(self.threshold)
        filter_row.addStretch()
        self.filter_check.toggled.connect(self.rebuild_plot)
        self.threshold.valueChanged.connect(self.rebuild_plot)

        self.figure = Figure(figsize=(8, 6), facecolor='#243746')
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#172a38')
        self.ax.set_xlabel('Tempo (s)', fontsize=10, color='#e6edf3')
        self.ax.set_ylabel('Luce', fontsize=10, color='#e6edf3')
        self.ax.set_title('ArduExoPlanet Analyzer - Photometry Simulation', fontsize=12, color='#e6edf3')
        self.ax.tick_params(colors='#e6edf3')
        for spine in self.ax.spines.values():
            spine.set_color('#7992a3')
        self.ax.grid(True, color='#557085', alpha=0.65)
        (self.line,) = self.ax.plot([], [], color='#40c4ff', lw=2)
        self.figure.tight_layout(pad=2)
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas, stretch=1)
        self.resize(940, 720)

        self.serial_error.connect(self.on_serial_error)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_graph)
        self.timer.start(50)
        self.update_ports()

    def update_ports(self):
        selected = self.port_combo.currentText()
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_combo.clear()
        self.port_combo.addItems(ports)
        if selected in ports:
            self.port_combo.setCurrentText(selected)
        if not ports:
            print('Errore: Nessuna porta seriale disponibile.')

    def toggle_serial(self):
        if self.port is None:
            self.start_serial()
        else:
            self.stop_serial()

    def start_serial(self):
        port_name = self.port_combo.currentText()
        if not port_name:
            print('Errore: Selezionare una porta e un baud rate.')
            return
        try:
            port = serial.Serial(port_name, int(self.baud_combo.currentText()), timeout=0.1)
        except (ValueError, serial.SerialException, OSError) as exc:
            print(f"Errore durante l'inizializzazione: {exc}")
            return
        self.port = port
        self.started = time.monotonic()
        self.stop_event = threading.Event()
        self.reader = threading.Thread(target=self.read_serial, args=(port, self.started, self.stop_event), daemon=True)
        self.reader.start()
        self.start_button.setText('Ferma')
        print('Comunicazione avviata.')

    def read_serial(self, port, started, stopped):
        try:
            while not stopped.is_set():
                raw = port.readline()
                if stopped.is_set():
                    break
                if not raw:
                    continue
                try:
                    value = float(raw.decode('utf-8').strip())
                except (UnicodeDecodeError, ValueError):
                    continue
                elapsed = time.monotonic() - started
                with self.log_lock:
                    self.log_data.append((elapsed, value))
                self.incoming.put((elapsed, value))
        except (serial.SerialException, OSError) as exc:
            if not stopped.is_set():
                self.serial_error.emit(str(exc))

    def on_serial_error(self, message):
        if not self.closing:
            print(f'Errore durante la lettura dei dati: {message}')
            self.stop_serial()

    def stop_serial(self):
        if self.port is None:
            return
        self.stop_event.set()
        port, self.port = self.port, None
        try:
            port.close()
        except (serial.SerialException, OSError) as exc:
            print(f'Errore durante la chiusura della porta: {exc}')
        self.start_button.setText('Avvia')
        print('Comunicazione fermata.')

    def add_plot_sample(self, elapsed, value):
        # Un punto per ogni campione: il filtro azzera solo le variazioni
        # piccole rispetto all'ultimo livello rappresentato, senza creare buchi
        # sull'asse dei tempi. Il log continua a contenere il valore originale.
        if (self.filter_check.isChecked() and self.last_plotted_value is not None
                and abs(value - self.last_plotted_value) <= self.threshold.value()):
            plotted_value = self.last_plotted_value
        else:
            plotted_value = value
        self.times.append(elapsed)
        self.values.append(plotted_value)
        self.last_plotted_value = plotted_value

    def redraw(self):
        self.line.set_data(self.times, self.values)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw_idle()

    def update_graph(self):
        changed = False
        while True:
            try:
                elapsed, value = self.incoming.get_nowait()
            except Empty:
                break
            self.recent_raw.append((elapsed, value))
            self.add_plot_sample(elapsed, value)
            changed = True
        if changed:
            self.redraw()

    def rebuild_plot(self, *_):
        # Aggiorna anche i punti già acquisiti quando si cambia filtro o soglia.
        self.update_graph()
        self.times.clear()
        self.values.clear()
        self.last_plotted_value = None
        for elapsed, value in self.recent_raw:
            self.add_plot_sample(elapsed, value)
        self.redraw()

    def update_plot_speed(self):
        try:
            interval = int(self.speed_entry.text())
            if interval <= 0:
                raise ValueError
        except ValueError:
            print('Errore: Inserisci un valore numerico valido per la velocità del plot.')
            return
        self.timer.setInterval(interval)
        print(f'Velocità del plot impostata su {interval} ms')

    def save_log(self):
        if not self.log_directory:
            self.log_directory = QFileDialog.getExistingDirectory(self, 'Seleziona la directory di salvataggio')
            if not self.log_directory:
                print('Errore: Nessuna directory selezionata.')
                return
        filename = os.path.join(self.log_directory, f"fotoresistenza_log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt")
        try:
            with self.log_lock:
                snapshot = self.log_data.copy()
            with open(filename, 'w') as output:
                output.write('Tempo (s);  Valore Fotoresistenza\n')
                for elapsed, value in snapshot:
                    output.write(f'{elapsed:.2f};       {value:.2f}\n')
            print(f'Log salvato in {filename}')
        except OSError as exc:
            print(f'Errore durante il salvataggio del log: {exc}')

    def reset_plot(self):
        with self.log_lock:
            self.log_data.clear()
            while True:
                try:
                    self.incoming.get_nowait()
                except Empty:
                    break
        self.recent_raw.clear()
        self.times.clear()
        self.values.clear()
        self.last_plotted_value = None
        self.redraw()

    def save_screenshot(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Scegli dove salvare lo screenshot', '', 'PNG files (*.png);;All files (*)')
        if filename:
            if not os.path.splitext(filename)[1]:
                filename += '.png'
            try:
                self.figure.savefig(filename, dpi=300)
            except (OSError, ValueError) as exc:
                print(f'Errore durante il salvataggio dello screenshot: {exc}')

    def closeEvent(self, event):
        self.closing = True
        self.timer.stop()
        self.stop_serial()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = Analyzer()
    window.show()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
