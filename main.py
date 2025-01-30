from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QErrorMessage, QButtonGroup, QCheckBox, QTableWidgetItem, QMessageBox
import warnings
from interface import Ui_mainWindow
from utils import start_algorithm, read_gps_data

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)

        self.ui.gpsButton.clicked.connect(self.open_gps_file)
        self.ui.programsButton.clicked.connect(self.open_programs_file)

        self.ui.startButton.clicked.connect(self.start)

    def open_gps_file(self):
        self.gps_path, _ = QFileDialog.getOpenFileName(self, "Open GPS File", "", "Text Files (*.txt)")
        if self.gps_path:
            self.ui.gpsLine.setText(self.gps_path)

    def open_programs_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Programs File", "", "CSV Files (*.csv)")
        if file_path:
            self.ui.programLine.setText(file_path)

    def start(self):
        df = read_gps_data(self.gps_path, True, 0)
        start_algorithm(df)

def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()