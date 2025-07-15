'''
MainWindow Control for UI_MainWindow.py
'''

import sys
import os
from pathlib import Path

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QDialog
from PyQt5.QtGui import QTextCursor, QPixmap
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PyQt5 import uic
#from PyQt5 import QtGui
from .Ui_MainWindow import Ui_MainWindow

from .sds_utilities import sds_view
from .sds_utilities import sdsio_server
from .sds_utilities import sds_convert
from .sds_utilities import sds_flash_fw
from .NuML_TFLM_Tool import numl_tool
from .NuML_TFLM_Tool.ei_upload import EiUploadDir

record_fw_list = [
    # combox's text, firmware binary filename, baudrate of uart recording
    ['G-sensor (X, Y, Z)', 'SDS_Recorder_gsensor_uart_CMSIS.bin', 115200],
    ['Audio (16kHZ)', 'SDS_Recorder_audio_uart_CMSIS.bin', 921600],
]

temp = sys.stdout
class Stream(QObject):
    newText = pyqtSignal(str)
    def write(self, text):
        self.newText.emit(str(text))
        # 实时刷新界面
        QApplication.processEvents()

class PlotDialog(QDialog):
    def __init__(self, image_path=None):
        super().__init__()
        uic.loadUi("app/plot_sds.ui", self)

        if image_path:
            self.load_image(image_path)
        else:
            self.imageLabel.setText("No image loaded.")

    def load_image(self, image_path):
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            self.imageLabel.setText("Failed to load image.")
        else:
            self.imageLabel.setPixmap(pixmap)    

class FlashThread(QThread):

    finished = pyqtSignal(str)  # signal to send status back to UI

    def __init__(self, board, data_type):
        super().__init__()
        self.board = board
        self.data_type = data_type
        self.setTerminationEnabled(True)  # allow thread to be stopped gracefully

    def run(self):
        ret = sds_flash_fw.start(['--board', self.board, '--binary_file', self.data_type])

        if ret != 0:
            self.finished.emit(f"Error flashing firmware: {ret}")  # notify UI when done
        else:    
            self.finished.emit("Flashing complete!")  # notify UI when done             

class myMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # print output to textEdit 
        sys.stdout = Stream(newText=self.onUpdateEdit_sds)

        # connect tabs page to textEdit
        self.tabWidget.currentChanged.connect(self.on_tab_changed)

        # sds view connect
        self.open_windows = []
        self.pushButton_3_yamlF_2.clicked.connect(self.show_textEdit_yamlFile)
        self.pushButton_2_sdsF_2.clicked.connect(self.show_textEdit_sdsFile)
        self.pushButton_sdsview_2.clicked.connect(self.execute_sds_view)

        # SDS firmware flash
        self.pushButton_sdsioServer_3.clicked.connect(self.execute_sds_flash_fw)
        self.thread_flash_fw = QThread()

        # sdsio server connect
        self.pushButton_outputDir_2.clicked.connect(self.show_textEdit_sdsio_outdir)
        self.pushButton_sdsioServer_2.clicked.connect(self.execute_sdsio_server)
        self.thread_a = QThread()

        # sds convert connect
        self.pushButton_5_sdsF_2.clicked.connect(self.show_textEdit_convert_sdsFile)
        self.pushButton_outDir_2.clicked.connect(self.show_textEdit_convert_outfile)
        self.pushButton_6_yamlF_2.clicked.connect(self.show_textEdit_convert_yamlFile)
        self.pushButton_sdsConvert_2.clicked.connect(self.execute_sds_convert)

        # NuML_Tool connect
        self.pushButton_5.clicked.connect(self.show_textEdit_tflite_model)
        self.pushButton_6.clicked.connect(self.show_textEdit_out_path)
        self.pushButton_7.clicked.connect(self.execute_numltool)
        self.comboBox_5.currentTextChanged.connect(self.handleComboBox5Change)

        # EI upload connect
        self.pushButton_5_sdsF_3.clicked.connect(self.choose_upload_dir)
        self.pushButton_sdsConvert_3.clicked.connect(self.execute_eiupload)    

    def on_tab_changed(self, index):
        if self.tabWidget.widget(index) == self.SDS_tab_2:
            sys.stdout = Stream(newText=self.onUpdateEdit_sds)
        elif self.tabWidget.widget(index) == self.NuML_Tool_tab_2:
            sys.stdout = Stream(newText=self.onUpdateEdit_numltool)    

    def closeEvent(self, event):
        """Shuts down application on close."""
        # Return stdout to defaults.
        sys.stdout = temp
        super().closeEvent(event)

    def onUpdateEdit_sds(self, text):
        cursor = self.textEdit_2.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.textEdit_2.setTextCursor(cursor)
        self.textEdit_2.ensureCursorVisible()

    def onUpdateEdit_numltool(self, text):
        cursor = self.textEdit_3.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.textEdit_3.setTextCursor(cursor)
        self.textEdit_3.ensureCursorVisible()    

    def show_textEdit_yamlFile(self):
        filepath , filetype = QFileDialog.getOpenFileName(
            directory='sds_out_dir', filter='*.yml')
        # show file path in textEdit  
        self.textEdit_5_yamlF_2.setPlainText(filepath)
        self.textEdit_5_yamlF_2.ensureCursorVisible()

    def show_textEdit_sdsFile(self):
        filepath , filetype = QFileDialog.getOpenFileName(
            directory='sds_out_dir', filter='*.sds')
        # show file path in textEdit
        self.textEdit_6_sdsF_2.setPlainText(filepath)
        self.textEdit_6_sdsF_2.ensureCursorVisible()

    def execute_sds_view(self):
        yaml_file = self.textEdit_5_yamlF_2.toPlainText()
        sds_file = self.textEdit_6_sdsF_2.toPlainText()
        if not yaml_file or not sds_file:
            print("Error: No YAML or SDS file selected.")
            print("Please select both YAML and SDS files.")
            return
        
        print(f"Executing SDS view with YAML: {yaml_file} and SDS: {sds_file}")
        sds_view.start(['-y', yaml_file, '-s', sds_file])
        # Open the plot dialog with the image path
        file_path = os.path.join(Path(sds_file).parent, 'myplot.png')
        if file_path:
            plot_window = PlotDialog(file_path)
            plot_window.show()
            self.open_windows.append(plot_window)

        print("SDS view executed done.")

    def show_textEdit_sdsio_outdir(self):
        folderpath = QFileDialog.getExistingDirectory(
            directory='sds_out_dir')
        # show file path in textEdit
        self.textEdit_outputDir_2.setPlainText(folderpath)
        self.textEdit_outputDir_2.ensureCursorVisible()

    def execute_sds_flash_fw(self):
        
        binary_file = None

        board = self.comboBox_7.currentText()
        data_type = self.comboBox_8.currentText()
        if not board or not data_type:
            print("Error: Missing board or data_type parameters.")
            return

        # corrsponding data_type to firmware binary file 
        for fw_list_item in record_fw_list:
            if data_type == fw_list_item[0]:
                binary_file = fw_list_item[1]

                # update baudrate to textEdit
                self.textEdit_Baudrate_2.setPlainText(str(fw_list_item[2]))
                self.textEdit_Baudrate_2.ensureCursorVisible()

                break
        binary_file = os.path.join('app', 'sds_firmware', board, binary_file)

        if not os.path.isfile(binary_file):
            print(f"Error: Firmware binary file {binary_file} not found.")
        else:
            # disable button
            self.pushButton_sdsioServer_3.setEnabled(False)
            self.pushButton_sdsioServer_2.setEnabled(False)
            self.thread_flash_fw = FlashThread(board, binary_file)
            self.thread_flash_fw.finished.connect(self.on_flash_done)
            self.thread_flash_fw.start()

    def on_flash_done(self, message):
        print(message)
        self.pushButton_sdsioServer_3.setEnabled(True)
        self.pushButton_sdsioServer_2.setEnabled(True)     


    def execute_sdsio_server(self):
        server_type = self.comboBox_serverType_2.currentText()
        serial_port = self.textEdit_serialPort_2.toPlainText()
        baudrate = self.textEdit_Baudrate_2.toPlainText()
        out_dir = self.textEdit_outputDir_2.toPlainText()
        if not server_type or not serial_port or not baudrate or not out_dir:
            print("Error: Missing server configuration parameters.")
            return
        print("Executing SDSIO server")

        try: 
            self.thread_a.run = sdsio_server.start([server_type, '-p', serial_port, '--baudrate', baudrate, '--outdir', out_dir])       # 設定該執行緒執行 a()
            self.thread_a.start()       # 啟動執行緒
        except RuntimeError as e:
            # Handle the error gracefully
            print(f"Error in thread: {e}")
            self.thread_a.quit()  # Ensure the thread is stopped  

    def show_textEdit_convert_sdsFile(self):
        filepath , filetype = QFileDialog.getOpenFileName(
            directory='sds_out_dir', filter='*.sds')
        # show file path in textEdit
        self.textEdit_10_sdsF_2.setPlainText(filepath)
        self.textEdit_10_sdsF_2.ensureCursorVisible()

    def show_textEdit_convert_outfile(self):
        openfile_format = "Text Files (*.txt)"
        if self.comboBox_serverType_convertFormat_2.currentText() == "simple_csv":
            openfile_format = "CSV Files (*.csv)"
        elif self.comboBox_serverType_convertFormat_2.currentText() == "audio_wav":
            openfile_format = "WAV Files (*.wav)"

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save File As",
            "",  # Default directory
            f"{openfile_format};;All Files (*)"
        )
        # show file path in textEdit
        self.textEdit_8_outDir_2.setPlainText(filepath)
        self.textEdit_8_outDir_2.ensureCursorVisible()

    def show_textEdit_convert_yamlFile(self):
        filepath , filetype = QFileDialog.getOpenFileName(
            directory='sds_out_dir', filter='*.yml')
        # show file path in textEdit
        self.textEdit_9_yamlF_2.setPlainText(filepath)
        self.textEdit_9_yamlF_2.ensureCursorVisible()     

    def execute_sds_convert(self):
        convert_format = self.comboBox_serverType_convertFormat_2.currentText()
        ei_export_enable = self.checkBox_EI_2.isChecked()
        sds_file = self.textEdit_10_sdsF_2.toPlainText()
        out_file = self.textEdit_8_outDir_2.toPlainText()
        yaml_file = self.textEdit_9_yamlF_2.toPlainText()
        label = self.textEdit_5.toPlainText()

        if not convert_format or not sds_file or not out_file or not yaml_file:
            print("Error: Missing convert configuration parameters.")
            return

        if ei_export_enable:
            print("Executing SDS convert with EI export enabled")
            try:
                sds_convert.start([convert_format, '-i', sds_file, '-o', out_file, '-y', yaml_file, 
                                '--normalize', '--label', label, '--ei-export'])
            except RuntimeError as e:
                print(f"Error in thread: {e}")
        else:
            print("Executing SDS convert")
            try:
                sds_convert.start([convert_format, '-i', sds_file, '-o', out_file, '-y', yaml_file, 
                                '--normalize', '--label', label])
            except RuntimeError as e:
                print(f"Error in thread: {e}")

    def show_textEdit_tflite_model(self):
        filepath , filetype = QFileDialog.getOpenFileName(
            directory='models', filter='*.tflite')
        # show file path in textEdit
        self.textEdit_10.setPlainText(filepath)
        self.textEdit_10.ensureCursorVisible()

    def show_textEdit_out_path(self):
        folderpath = QFileDialog.getExistingDirectory(
            self,
            "Select or Create Folder",
            "C:/",  # Default directory set to C:/
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        default_dir_name = "gen_proj_numl"
        # show folder path in textEdit
        self.textEdit_8.setPlainText(os.path.join(folderpath, default_dir_name))
        self.textEdit_8.ensureCursorVisible()

    def handleComboBox5Change(self, text):
        specify_child_text = "vscode"
        if text == specify_child_text:
            # Enable other labels and combo boxes
            self.label_36.setEnabled(True)
            self.comboBox_6.setEnabled(True)
        else:
            # Disable other labels and combo boxes
            self.comboBox_6.setCurrentText("TFLite_inference_only_example")
            self.label_36.setEnabled(False)
            self.comboBox_6.setEnabled(False)      

    def execute_numltool(self):
        numl_type = self.comboBox_3.currentText()
        tflite_model = self.textEdit_10.toPlainText()
        board = self.comboBox_4.currentText()
        out_proj_path = self.textEdit_8.toPlainText()
        proj_type = self.comboBox_5.currentText()
        vscode_ex_type = self.comboBox_6.currentText()
        if not numl_type or not tflite_model or not out_proj_path:
            print("Error: Missing NuML_TFLM_Tool configuration parameters.")
            return
        
        # update vscode_ex_type for argparser
        if vscode_ex_type == "Sds Gsensor example":
            vscode_ex_type = "sds_gsensor"
        elif vscode_ex_type == "TFLite_inference_only_example":
            vscode_ex_type = "tflite_only"

        #print(['generate', '--model_file', tflite_model, '--board', board, 
        #                     '--output_path', out_proj_path, '--project_type', proj_type, '--vs_ex_type', vscode_ex_type])    

        if numl_type == "Generate project":
            numl_tool.start(['generate', '--model_file', tflite_model, '--board', board, 
                             '--output_path', out_proj_path, '--project_type', proj_type, '--vs_ex_type', vscode_ex_type])
        print("NuML_TFLM_Tool executed done.")

    def choose_upload_dir(self):
        folderpath = QFileDialog.getExistingDirectory(
            self,
            "Select Folder",
            ".",  # Default directory set to C:/
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        # show folder path in textEdit
        self.textEdit_10_sdsF_3.setPlainText(folderpath)
        self.textEdit_10_sdsF_3.ensureCursorVisible()

    def execute_eiupload(self):
        folderpath = self.textEdit_10_sdsF_3.toPlainText()
        category = self.comboBox_serverType_convertFormat_3.currentText()
        label = self.textEdit_6.toPlainText()

        ei_upload = EiUploadDir()
        if label == 'None':
            label = None

        # Upload the directory to Edge Impulse
        try:
            ei_upload.upload_dir(folderpath, category, label)
        except RuntimeError as e:
            # Handle the error gracefully
            print(f"Error in thread: {e}")    

        

#if __name__ == '__main__':
# for Pystand
def main(argv=None):
    app = QApplication(sys.argv)
    window = myMainWindow()
    window.show()
    sys.exit(app.exec_())

# for Pystand
def start(argv=None):
    main(argv)