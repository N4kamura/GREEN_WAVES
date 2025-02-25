from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QErrorMessage, QTimeEdit, QMessageBox
from multi_tsd_interface import Ui_MainWindow
from utils import start_algorithm, read_gps_data, read_program
import os
import json

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.config_path = None

        self.ui.save_general_Button.clicked.connect(self.save_basic_config)

        # GPS Data #
        # Inbound
        self.ui.gps_ida_load_Button.clicked.connect(self.open_ida_gps_load_file)
        self.ui.gps_ida_save_Button.clicked.connect(self.open_ida_gps_save_file)

        # Outbound
        self.ui.gps_vuelta_load_Button.clicked.connect(self.open_vuelta_gps_load_file)
        self.ui.gps_vuelta_save_Button.clicked.connect(self.open_vuelta_gps_save_file)

        # Program Data #
        self.ui.program_load_Button.clicked.connect(self.open_program_load_file)
        self.ui.program_save_Button.clicked.connect(self.open_program_save_file)

        # Starters #
        # Inbound
        self.ui.start_ida_save_Button.clicked.connect(self.start_ida_save)
        # Outbound
        self.ui.start_vuelta_save_Button.clicked.connect(self.start_vuelta_save)

        # Delays #
        # Inbound
        self.ui.delay_ida_save_Button.clicked.connect(self.delay_ida_save)
        # Outbound
        self.ui.delay_vuelta_save_Button.clicked.connect(self.delay_vuelta_save)

        # Final buttons #
        self.ui.general_config_save_Button.clicked.connect(self.save_general_config)
        self.ui.general_config_load_Button.clicked.connect(self.load_general_config)
        self.ui.general_start_Button.clicked.connect(self.start_general)

        # Default values #
        self.ida_checkBox = False
        self.vuelta_checkBox = False
        self.cycles = 3
        self.in_path = None
        self.list_in_paths = []
        self.out_path = None
        self.list_out_paths = []
        self.excel_path = None

    #############
    # Functions #
    #############

    def save_basic_config(self):
        self.ida_checkBox = self.ui.ida_checkBox.isChecked()
        self.vuelta_checkBox = self.ui.vuelta_checkBox.isChecked()
        self.cycles = self.ui.cycles_spinBox.value()
        message_box = QMessageBox(self)
        message_box.setIcon(QMessageBox.Information)
        message_box.setText("Configuration saved")
        message_box.exec_()

    def open_ida_gps_load_file(self):
        self.in_path, _ = QFileDialog.getOpenFileName(self, "Open GPS File", "", "Text Files (*.txt)")
        if self.in_path:
            self.ui.gps_ida_lineEdit.setText(self.in_path)

    def open_ida_gps_save_file(self):
        if not self.in_path:
            error_message = QErrorMessage(self)
            error_message.showMessage("No file loaded")
        else:
            self.list_in_paths.append(self.in_path)
            self.ui.statusbar.showMessage("Loaded inbound file")

    def open_vuelta_gps_load_file(self):
        self.out_path, _ = QFileDialog.getOpenFileName(self, "Open GPS File", "", "Text Files (*.txt)")
        if self.out_path:
            self.ui.gps_vuelta_lineEdit.setText(self.out_path)

    def open_vuelta_gps_save_file(self):
        if not self.out_path:
            error_message = QErrorMessage(self)
            error_message.showMessage("No file loaded")
        else:
            self.list_out_paths.append(self.out_path)
            self.ui.statusbar.showMessage("Loaded outbound file")

    def open_program_load_file(self):
        self.excel_path, _ = QFileDialog.getOpenFileName(self, "Open Programs File", "", "Excel Files (*.xlsx)")
        if self.excel_path:
            self.ui.program_lineEdit.setText(self.excel_path)
            self.ui.statusbar.showMessage("Load programs file")

    def open_program_save_file(self):
        pass # NOTE: It's not necessary

    def start_ida_save(self):
        self.start_ida = self.ui.start_ida_timeEdit.time().toString("HH:mm:ss")
        self.ui.start_ida_spinBox.setValue(self.ui.start_ida_spinBox.value() + 1)

    def start_vuelta_save(self):
        self.start_vuelta = self.ui.start_vuelta_timeEdit.time().toString("HH:mm:ss")
        self.ui.start_vuelta_spinBox.setValue(self.ui.start_vuelta_spinBox.value() + 1)

    def delay_ida_save(self):
        self.delay_ida = self.ui.delay_ida_spinBox.value()
        self.ui.delay_ida_order_spinBox.setValue(self.ui.delay_ida_order_spinBox.value() + 1)

    def delay_vuelta_save(self):
        self.delay_vuelta = self.ui.delay_vuelta_spinBox.value()
        self.ui.delay_vuelta_order_spinBox.setValue(self.ui.delay_vuelta_order_spinBox.value() + 1)

    def save_general_config(self):
        # Open Folder
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        max_iter = max(self.ui.delay_vuelta_order_spinBox.value(), self.ui.delay_ida_order_spinBox.value())
        self.data_dict = {}
        if folder_path:
            for i in range(1,max_iter):
                try:
                    self.data_dict[i] = {
                        "Configuration": {
                            "in_path": self.list_in_paths[i-1],
                            "out_path": self.list_out_paths[i-1],
                            "excel_path": self.excel_path,
                            "inbound": self.ida_checkBox,
                            "outbound": self.vuelta_checkBox,
                            "outbound_start_time": self.start_vuelta,
                            "inbound_start_time": self.start_ida,
                            "displacement_in": self.delay_ida,
                            "displacement_out": self.delay_vuelta,
                            "number_cycles": self.cycles
                        }
                    }
                except Exception as e:
                    error_message = QErrorMessage(self)
                    return error_message.showMessage(f"Error in iteration {i}: {e}")
                
        with open(f"{os.path.join(folder_path, "multi_config.json")}", "w") as f:
            json.dump(self.data_dict, f)

        self.ui.statusbar.showMessage("Multi-configuration saved")

    def load_general_config(self):
        self.multi_config_path, _ = QFileDialog.getOpenFileName(self, "Open Multi-Configuration File", "", "JSON Files (*.json)")
        self.data_dict = {}
        if self.multi_config_path:
            with open(self.multi_config_path, "r") as f:
                data = json.load(f)
                
                for key in data.keys():
                    self.in_path = data[key]["Configuration"]["in_path"]
                    self.out_path = data[key]["Configuration"]["out_path"]
                    self.excel_path = data[key]["Configuration"]["excel_path"]
                    self.ida_checkBox = data[key]["Configuration"]["inbound"]
                    self.vuelta_checkBox = data[key]["Configuration"]["outbound"]
                    self.start_ida = data[key]["Configuration"]["inbound_start_time"]
                    self.start_vuelta = data[key]["Configuration"]["outbound_start_time"]
                    self.delay_ida = data[key]["Configuration"]["displacement_in"]
                    self.delay_vuelta = data[key]["Configuration"]["displacement_out"]
                    self.cycles = data[key]["Configuration"]["number_cycles"]

    def start_general(self):
        pass

def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()