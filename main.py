from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QErrorMessage, QTimeEdit, QMessageBox
from interface import Ui_mainWindow
from utils import start_algorithm, read_gps_data, read_program
import os
import json

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)

        self.ui.inButton.clicked.connect(self.open_gps_in_file)
        self.ui.outButton.clicked.connect(self.open_gps_out_file)
        self.ui.programsButton.clicked.connect(self.open_programs_file)
        self.ui.saveButton.clicked.connect(self.save_config)
        self.ui.readButton.clicked.connect(self.load_config)

        self.ui.startButton.clicked.connect(self.start)

        self.status = self.statusBar()

        self.config_path = None

    def open_gps_in_file(self):
        self.in_path, _ = QFileDialog.getOpenFileName(self, "Open GPS File", "", "Text Files (*.txt)")
        if self.in_path:
            self.ui.inLine.setText(self.in_path)
            self.status.showMessage("Loaded inbound file")

    def open_gps_out_file(self):
        self.out_path, _ = QFileDialog.getOpenFileName(self, "Open GPS File", "", "Text Files (*.txt)")
        if self.out_path:
            self.ui.outLine.setText(self.out_path)
            self.status.showMessage("Loaded outbound file")

    def open_programs_file(self):
        self.excel_path, _ = QFileDialog.getOpenFileName(self, "Open Programs File", "", "Excel Files (*.xlsx)")
        if self.excel_path:
            self.ui.programLine.setText(self.excel_path)
            self.status.showMessage("Load programs file")

    def save_config(self):
        # Open a folder
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            inbound, outbound = False, False
            if self.ui.in_checkBox.isChecked():
                inbound = True
            else:
                self.in_path = None
            if self.ui.out_checkBox.isChecked():
                outbound = True
            else:
                self.in_path = None
            try:
                data_dict = {
                    "Configuration": {
                        "in_path": self.in_path,
                        "out_path": self.out_path,
                        "excel_path": self.excel_path,
                        "inbound": inbound,
                        "outbound": outbound,
                        "outbound_start_time": self.ui.out_timeEdit.time().toString("HH:mm:ss"),
                        "inbound_start_time": self.ui.in_timeEdit.time().toString("HH:mm:ss"),
                    }
                }
            except Exception as e:
                error = QErrorMessage(self)
                return error.showMessage(f"Error: {e}")

            with open(f"{os.path.join(folder_path, 'config.json')}", "w") as f:
                json.dump(data_dict, f, indent=4)

            self.status.showMessage("Save configuration")
        else:
            error = QErrorMessage(self)
            return error.showMessage("Please select a folder to save the configuration.")

    def load_config(self):
        self.config_path, _ = QFileDialog.getOpenFileName(self, "Open Configuration File", "", "JSON Files (*.json)")
        if self.config_path:
            with open(self.config_path, "r") as f:
                data = json.load(f)

            self.in_path = data["Configuration"]["in_path"]
            self.out_path = data["Configuration"]["out_path"]
            self.excel_path = data["Configuration"]["excel_path"]
            self.inbound = data["Configuration"]["inbound"]
            self.outbound = data["Configuration"]["outbound"]
            self.outbound_start_time = data["Configuration"]["outbound_start_time"]
            self.inbound_start_time = data["Configuration"]["inbound_start_time"]

            self.status.showMessage("Configuration loaded")

    def start(self):
        if not self.config_path:
            # Obtaining hours and minutes from QTimeEdit
            if self.ui.in_checkBox.isChecked():
                self.inbound_start_time = self.ui.in_timeEdit.time().toString("HH:mm:ss")
                self.inbound = True
            else:
                self.in_path = None
            
            if self.ui.out_checkBox.isChecked():
                self.outbound_start_time = self.ui.out_timeEdit.time().toString("HH:mm:ss")
                self.outbound = True
            else:
                self.out_path = None
            
            programs = read_program(self.excel_path)

        # Obtaining upper_limit in case of outbound
        df_in, df_out = read_gps_data(
            in_path=self.in_path,
            out_path=self.out_path,
            inbound=self.inbound,
            outbound=self.outbound,
            upper_hour=self.outbound_start_time,
            lower_hour=self.inbound_start_time,
            )
        
        start_algorithm(df_in, df_out, programs)

        self.status.showMessage("Space-Time Diagram created")

def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()