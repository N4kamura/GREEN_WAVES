from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QErrorMessage, QTimeEdit, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt
from interface.new_interface import Ui_MainWindow
from utils import start_algorithm, read_gps_data, read_program
import os
import json
import csv
import pandas as pd

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.pushButton.clicked.connect(self.open_program)
        self.ui.pushButton_2.clicked.connect(self.save_config)
        self.ui.pushButton_3.clicked.connect(self.load_config)
        self.ui.pushButton_4.clicked.connect(self.add_path)
        self.ui.pushButton_5.clicked.connect(self.start)

        self.status = self.statusBar()

    def open_program(self):
        self.excel_path, _ = QFileDialog.getOpenFileName(self, "Open Programs File", "", "Excel Files (*.xlsx)")
        if self.excel_path:
            self.ui.lineEdit.setText(self.excel_path)
            self.status.showMessage("Load programs file")

    def save_config(self):
        self.folder_config = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta para guardar configuración")
        if self.folder_config:
            config_txt_path = os.path.join(self.folder_config, "config.txt")

            with open(config_txt_path, "w", newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=',')

                headers = ["GPS Path", "Name GPS", "In / Out", "Start Time", "Delay", "Cycles"]
                writer.writerow(headers)

                row_count = self.ui.tableWidget.rowCount()
                column_count = self.ui.tableWidget.columnCount()

                for row in range(row_count):
                    row_data = []
                    for column in range(column_count):
                        if column == 2: # Order for In / Out
                            item = self.ui.tableWidget.item(row, column)
                            
                            if item is not None:
                                state = item.checkState()

                                if state == Qt.Checked:
                                    row_data.append("Checked")
                                elif state == Qt.Unchecked:
                                    row_data.append("Unchecked")
                                elif state == Qt.PartiallyChecked:
                                    row_data.append("PartiallyChecked")
                            else:
                                row_data.append("")
                        else:
                            item = self.ui.tableWidget.item(row,column)

                            if item is not None:
                                row_data.append(item.text())
                            else:
                                row_data.append("")

                    row_data.append(f"{self.ui.spinBox.value()}")

                    writer.writerow(row_data)

            self.status.showMessage(f"Archivo guardado en: {self.folder_config}")

    def start(self):

        ###########################
        # Converting to dataframe #
        ###########################

        row_count = self.ui.tableWidget.rowCount()
        column_count = self.ui.tableWidget.columnCount()

        headers = []
        for column in range(column_count):
            header_item = self.ui.tableWidget.horizontalHeaderItem(column)
            if header_item is not None:
                headers.append(header_item.text())
            else:
                headers.append(f"Column {column}")

        table_data = []
        for row in range(row_count):
            row_data = []
            for column in range(column_count):
                if column == 2:
                    item = self.ui.tableWidget.item(row, column)
                    if item is not None:
                        state = item.checkState()
                        if state == Qt.Checked:
                            row_data.append("Checked")
                        elif state == Qt.Unchecked:
                            row_data.append("Unchecked")
                        elif state == Qt.PartiallyChecked:
                            row_data.append("PartiallyChecked")
                    else:
                        row_data.append("")
                else:
                    item = self.ui.tableWidget.item(row, column)
                    if item is not None:
                        row_data.append(item.text())
                    else:
                        row_data.append("")
            table_data.append(row_data)

        df = pd.DataFrame(table_data, columns=headers)

        print(df)
        print(df.dtypes)

        return df

    def add_path(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo GPS", "", "Archivos de texto (*.txt)")
        file_name = os.path.basename(file_path)
        if file_path:
            row_count = self.ui.tableWidget.rowCount()
            for row in range(row_count):
                if not self.ui.tableWidget.item(row, 0): # check if cell is empty
                    self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(file_path))
                    self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(file_name))
                    return
                
            self.status.showMessage("No se pueden agregar más archivos")

    def load_config(self):
        pass

def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()