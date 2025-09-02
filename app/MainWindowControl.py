'''
MainWindow Control for UI_MainWindow.py
'''

import sys
import os
from pathlib import Path
from datetime import datetime

import cv2
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QDialog
from PyQt5.QtGui import QTextCursor, QPixmap, QImage
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer, Qt
from PyQt5 import uic
#from PyQt5 import QtGui
from .Ui_MainWindow import Ui_NuMLTool
from .UI_cam_capture import Ui_WebcamWindow

from .sds_utilities import sds_view
from .sds_utilities import sdsio_server
from .sds_utilities import sds_convert
from .sds_utilities import flash_fw
from .NuML_TFLM_Tool import numl_tool
from .NuML_TFLM_Tool.ei_upload import EiUploadDir

# Recording firmware list
record_fw_list = [
    # combox's text, firmware binary filename, baudrate of uart recording
    ['G-sensor (X, Y, Z)', 'SDS_Recorder_gsensor_uart_CMSIS.bin', 115200],
    ['Audio (16kHZ)', 'SDS_Recorder_audio_uart_CMSIS.bin', 921600],
    ['Image', 'HSUSBD_Video_CAM.bin', ' '],
]

# Project type for Nuvoton deployment
deployed_project_type_list = [
    # combox's text, project type
    ['Vscode', 'vscode'],
    ['uVision5_armc6', 'uvision5_armc6'],
]

# Application type for Nuvoton deployment
deployed_application_list = [
    # combox's text, application type
    ['TFLite Inference Example', 'generic'],
    ['Sds Gsensor example', 'gsensor_sds'],
    ['Image Classification example', 'imgclass'],
]

# Application type for EI deployment
ei_deployed_application_list = [
    # combox's text, application type
    ['EI Inference Example', 'generic'],
]

def get_download_folder():
    """
    Retrieves the path to the user's Downloads folder.
    """
    download_path = Path.home() / "Downloads"

    if download_path.exists():
        return str(download_path)
    else:
        # Fallback: use OS-specific environment variables
        return str(Path(os.path.join(os.path.expanduser("~"), "Downloads")))

temp = sys.stdout
class Stream(QObject):
    """
    A custom stream class that redirects text output and emits it as a signal.
    Attributes:
        newText (pyqtSignal): A signal that emits a string whenever new text is written.
    """
    newText = pyqtSignal(str)
    def write(self, text):
        """
        Emits the provided text as a signal and refreshes the GUI.
        """
        self.newText.emit(str(text))
        # 实时刷新界面
        QApplication.processEvents()

    def flush(self):
        """
        A placeholder method to handle stream flushing.
        """

class PlotDialog(QDialog):
    """
    A dialog window for displaying an image using PyQt.
    Attributes:
        imageLabel (QLabel): A label widget to display the image or a message.
    """
    def __init__(self, image_path=None):
        super().__init__()
        uic.loadUi("app/plot_sds.ui", self)

        if image_path:
            self.load_image(image_path)
        else:
            self.imageLabel.setText("No image loaded.")

    def load_image(self, image_path):
        """
        Loads an image from the specified file path and displays it on the imageLabel widget.
        """
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            self.imageLabel.setText("Failed to load image.")
        else:
            self.imageLabel.setPixmap(pixmap)

class WebcamWindow(QMainWindow):
    """
    This class represents a GUI window for webcam operations, including camera selection, resolution configuration, 
    live video feed display, image capture, and application closure.
    """
    def __init__(self):
        super().__init__()
        self.ui = Ui_WebcamWindow()
        self.ui.setupUi(self)

        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.current_frame = None
        self.output_dir = r"sds_out_dir/images"
        os.makedirs(self.output_dir, exist_ok=True)

        self.populate_cameras()
        self.populate_resolutions()

        # Initialize status bar
        self.statusBar()

        # Connect UI buttons
        self.ui.pushButton_3.clicked.connect(self.start_camera)
        self.ui.pushButton.clicked.connect(self.capture_image)
        self.ui.pushButton_2.clicked.connect(self.close_app)

    def populate_cameras(self):
        """
        Populates the camera selector dropdown with available cameras.
        """
        self.ui.camera_selector.clear()
        for i in range(2):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                self.ui.camera_selector.addItem(f"Camera {i}", i)
                cap.release()

    def populate_resolutions(self):
        """
        Populates the resolution selector dropdown with a predefined list of resolutions.
        """
        resolutions = ["640x480", "320x240"]
        self.ui.resolution_selector.addItems(resolutions)

    def start_camera(self):
        """
        Raises:
            QMessageBox: Displays a critical error message if the camera cannot be opened.
        Attributes:
            cap (cv2.VideoCapture): The OpenCV video capture object used to interface 
                with the camera.
            timer (QTimer): A timer object used to periodically capture frames.
        UI Elements:
            camera_selector (QComboBox): UI element for selecting the camera device index.
            resolution_selector (QComboBox): UI element for selecting the camera resolution.
        """
        if self.cap and self.cap.isOpened():
            self.cap.release()

        device_index = self.ui.camera_selector.currentData()
        resolution = self.ui.resolution_selector.currentText()
        width, height = map(int, resolution.split('x'))

        self.cap = cv2.VideoCapture(device_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        if not self.cap.isOpened():
            print(f"Error: Cannot open camera {device_index}")
            self.statusBar().showMessage(f"Error: Cannot open camera {device_index}", 5000)
            return

        self.timer.start(30)

    def update_frame(self):
        """
        Updates the current frame displayed in the application's UI.
        """
        if not self.cap:
            return
        ret, frame = self.cap.read()
        if not ret:
            return
        self.current_frame = frame
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.ui.image_label.setPixmap(QPixmap.fromImage(qimg))

    def capture_image(self):
        """
        Captures the current frame and saves it as an image file.
        """
        if self.current_frame is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.output_dir, f"capture_{timestamp}.jpg")
            cv2.imwrite(filename, self.current_frame)
            print(f"[INFO] Captured: {filename}")
            self.statusBar().showMessage(f"Image captured: capture_{timestamp}.jpg", 2000)

    def close_app(self):
        """
        Closes the application gracefully.
        """
        self.timer.stop()
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.close()

    def keyPressEvent(self, event):
        """
        Handles key press events for the application window.
        """
        if event.key() == Qt.Key_C:
            self.capture_image()
        elif event.key() == Qt.Key_Escape:
            self.close_app()

class FlashThread(QThread):
    """
    A thread class for handling firmware flashing operations asynchronously.
    """

    finished = pyqtSignal(str)  # signal to send status back to UI

    def __init__(self, board, data_type):
        super().__init__()
        self.board = board
        self.data_type = data_type
        self.setTerminationEnabled(True)  # allow thread to be stopped gracefully

    def run(self):
        """
        Executes the firmware flashing process using the specified board and binary file.
        """
        ret = flash_fw.start(['--board', self.board, '--binary_file', self.data_type])

        if ret != 0:
            self.finished.emit(f"Error flashing firmware: {ret}")  # notify UI when done
        else:
            self.finished.emit("Flashing complete!")  # notify UI when done

class myMainWindow(QMainWindow, Ui_NuMLTool):
    """
    This class represents the main window of the application, inheriting from QMainWindow and Ui_NuMLTool.
    It provides functionality for interacting with various components of the application, including SDS view, 
    SDS firmware flashing, SDSIO server, SDS conversion, NuML tool, Edge Impulse upload, and webcam capture.
    """
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # --- Add Pages to StackedWidget ---
        self.pages = {}
        self.add_page("Record Data", self.page_Record_Data) # first layer using first page
        self.add_page("Recording", self.page_Recording)
        self.add_page("View", self.page_View)
        self.add_page("Output", self.page_Output)
        self.add_page("Upload", self.page_Upload)
        self.add_page("Deployment", self.page_Deployment)
        self.add_page("Nuvoton", self.page)
        self.add_page("EI", self.page_2)

        self.pages_structure = {
            "Record Data": ["Recording", "View", "Output", "Upload"],
            "Deployment": ["Nuvoton", "EI"],
        }

        # --- Set up the Collapsible Menu ---
        # Sidebar (TreeWidget)
        self.treeWidget.setHeaderHidden(True)
        #self.treeWidget.setStyleSheet("""
        #    QTreeWidget {
        #        border: none;
        #        background: white;
        #        font-size: 14px;
        #    }
        #    QTreeWidget::item {
        #        padding: 6px;
        #    }
        #    QTreeWidget::item:selected {
        #        background: #d9d9d9;
        #        border-radius: 4px;
        #    }
        #""")
        self.treeWidget.expandAll()

        # Default page
        self.switch_page("Recording")

        # Signal connect
        self.treeWidget.itemClicked.connect(self.on_item_clicked)

        # print output to textEdit
        sys.stdout = Stream(newText=self.on_update_edit_sds)
        # clear textEdit buttons connect
        self.pushButton_8.clicked.connect(lambda: self.clear_text_edit(self.textEdit_2))
        self.pushButton_9.clicked.connect(lambda: self.clear_text_edit(self.textEdit_3))

        # sds view connect
        self.open_windows = []
        self.pushButton_3_yamlF_2.clicked.connect(self.show_textedit_yamlfile)
        self.pushButton_2_sdsF_2.clicked.connect(self.show_textedit_sdsfile)
        self.pushButton_sdsview_2.clicked.connect(self.execute_sds_view)

        # SDS firmware flash
        self.populate_firmwares()
        self.pushButton_sdsioServer_3.clicked.connect(self.execute_sds_flash_fw)
        self.thread_flash_fw = QThread()

        # sdsio server connect
        self.pushButton_outputDir_2.clicked.connect(self.show_textedit_sdsio_outdir)
        self.pushButton_sdsioServer_2.clicked.connect(self.execute_sdsio_server)
        self.thread_a = QThread()

        # sds convert connect
        self.pushButton_5_sdsF_2.clicked.connect(self.show_textedit_convert_sdsfile)
        self.pushButton_outDir_2.clicked.connect(self.show_textedit_convert_outfile)
        self.pushButton_6_yamlF_2.clicked.connect(self.show_textedit_convert_yamlfile)
        self.pushButton_sdsConvert_2.clicked.connect(self.execute_sds_convert)

        # Deployment Nuvoton connect
        self.populate_deployed_project_type()
        self.populate_deployed_application(deployed_application_list, self.comboBox_6)
        self.show_textedit_out_path_default(self.textEdit_8, "gen_proj_ml")
        self.pushButton_11.clicked.connect(self.show_textedit_tflite_model)
        self.pushButton_12.clicked.connect(lambda: self.show_textedit_out_path(self.textEdit_8))
        self.pushButton_10.clicked.connect(self.execute_numltool)
        #self.comboBox_5.currentTextChanged.connect(self.handle_combobox5_change)

        # Deployment Edge Impulse connect
        self.populate_deployed_application(ei_deployed_application_list, self.comboBox_14)
        self.show_textedit_out_path_default(self.textEdit_13, "gen_proj_EI_ml")
        self.pushButton_14.clicked.connect(self.show_textedit_eisdk_path)
        self.pushButton_15.clicked.connect(lambda: self.show_textedit_out_path(self.textEdit_13, "gen_proj_EI_ml"))
        self.pushButton_16.clicked.connect(self.execute_eisdk_deploy)

        # EI upload connect
        self.pushButton_5_sdsF_3.clicked.connect(self.choose_upload_dir)
        self.pushButton_sdsConvert_3.clicked.connect(self.execute_eiupload)

        # Webcam capture connect
        self.webcam_window = None
        self.pushButton_7.clicked.connect(self.open_webcam_capture)

    def add_page(self, name, widget):
        """
        Adds a new page to the application.
        """
        self.pages[name] = widget

    def switch_page(self, name):
        """
        Switches the current page in the application's user interface based on the provided page name.
        """
        # first layer
        if name in ['Record Data']:
            sys.stdout = Stream(newText=self.on_update_edit_sds)
            self.stackedWidget_Main.setCurrentWidget(self.page_Record_Data)
        elif name in ['Deployment']:
            sys.stdout = Stream(newText=self.on_update_edit_numltool)
            #sys.stdout = temp
            self.stackedWidget_Main.setCurrentWidget(self.page_Deployment)
        # second layer
        elif name in self.pages_structure.get("Record Data", []):
            sys.stdout = Stream(newText=self.on_update_edit_sds)
            self.stackedWidget_Main.setCurrentWidget(self.page_Record_Data)
            self.stackedWidget_2.setCurrentWidget(self.pages[name])
        elif name in self.pages_structure.get("Deployment", []):
            sys.stdout = Stream(newText=self.on_update_edit_numltool)
            #sys.stdout = temp
            self.stackedWidget_Main.setCurrentWidget(self.page_Deployment)
            self.stackedWidget_deployment.setCurrentWidget(self.pages[name])
        else:
            print(f"Page '{name}' not found in {self.pages}.")

    def on_item_clicked(self, item, column):
        """
        Handles the event when an item in the UI is clicked.
        """
        name = item.text(0).lstrip('- ').strip()
        if name in self.pages:
            self.switch_page(name) 

    def close_event(self, event):
        """
        Handles the close event for the main window.
        """
        # Return stdout to defaults.
        sys.stdout = temp
        super().close_event(event)

    def on_update_edit_sds(self, text):
        """
        Appends the given text to the end of the textEdit_2 widget, ensuring the cursor
        is moved to the end and remains visible.
        """
        cursor = self.textEdit_2.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.textEdit_2.setTextCursor(cursor)
        self.textEdit_2.ensureCursorVisible()

    def on_update_edit_numltool(self, text):
        """
        Updates the text in the `textEdit_3` widget by appending the provided text.
        """
        cursor = self.textEdit_3.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.textEdit_3.setTextCursor(cursor)
        self.textEdit_3.ensureCursorVisible()

    def clear_text_edit(self, text_edit):
        """Clear the specified QTextEdit."""
        text_edit.clear()

    def show_textedit_yamlfile(self):
        """
        Opens a file dialog to select a YAML file and displays the selected file path 
        in a text edit widget.
        """
        filepath , filetype = QFileDialog.getOpenFileName(
            directory='sds_out_dir', filter='*.yml')
        # show file path in textEdit
        self.textEdit_5_yamlF_2.setPlainText(filepath)
        self.textEdit_5_yamlF_2.ensureCursorVisible()

    def show_textedit_sdsfile(self):
        """
        Opens a file dialog to select an SDS file and displays the selected file path 
        in a text edit widget.
        """
        filepath , filetype = QFileDialog.getOpenFileName(
            directory='sds_out_dir', filter='*.sds')
        # show file path in textEdit
        self.textEdit_6_sdsF_2.setPlainText(filepath)
        self.textEdit_6_sdsF_2.ensureCursorVisible()

    def execute_sds_view(self):
        """
        Executes the SDS view process using the provided YAML and SDS files.
        """

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

    def show_textedit_sdsio_outdir(self):
        """
        Opens a folder selection dialog for the user to choose a directory.
        """

        folderpath = QFileDialog.getExistingDirectory(
            directory='sds_out_dir')
        # show file path in textEdit
        self.textEdit_outputDir_2.setPlainText(folderpath)
        self.textEdit_outputDir_2.ensureCursorVisible()

    def populate_deployed_project_type(self):
        """
        Populates the comboBox_5 widget with a list of deployed project types.
        """
        project_types = [item[0] for item in deployed_project_type_list]
        self.comboBox_5.addItems(project_types)

    def populate_deployed_application(self, input_application_list, comboBox):
        """
        Populates the comboBox widget with a list of deployed applications.
        """
        applications = [item[0] for item in input_application_list]
        comboBox.addItems(applications)

    def populate_firmwares(self):
        """
        Populates the firmware selection combo box with a list of firmware names
        and sets up a callback for when the selected firmware changes.
        """
        fws = [item[0] for item in record_fw_list]
        self.comboBox_8.addItems(fws)
        # disable some widgets
        self.comboBox_8.currentTextChanged.connect(self.on_firmware_selected_cam)

    def on_firmware_selected_cam(self, selected_item):
        """
        Handles the selection of a firmware option for the camera.
        """
        # Example: Disable other widgets if a specific item is selected
        if selected_item == "Image":
            self.comboBox_serverType_2.setDisabled(True)
            self.lineEdit.setDisabled(True)
            self.lineEdit_2.setDisabled(True)
            self.pushButton_outputDir_2.setDisabled(True)
            self.textEdit_outputDir_2.setDisabled(True)
            self.pushButton_sdsioServer_2.setDisabled(True)
        else:
            self.comboBox_serverType_2.setDisabled(False)
            self.lineEdit.setDisabled(False)
            self.lineEdit_2.setDisabled(False)
            self.pushButton_outputDir_2.setDisabled(False)
            self.textEdit_outputDir_2.setDisabled(False)
            self.pushButton_sdsioServer_2.setDisabled(False)

    def execute_sds_flash_fw(self):
        """
        Executes the firmware flashing process for the selected board and data type.
        """
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
                self.lineEdit_2.setPlainText(str(fw_list_item[2]))
                self.lineEdit_2.ensureCursorVisible()

                break
        binary_file = os.path.join('app', 'mcu_firmware', board, binary_file)

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
        """
        Handles the completion of a flash operation.
        """
        print(message)
        self.pushButton_sdsioServer_3.setEnabled(True)
        self.pushButton_sdsioServer_2.setEnabled(True)

    def execute_sdsio_server(self):
        """
        Executes the SDSIO server with the specified configuration parameters.
        """
        server_type = self.comboBox_serverType_2.currentText()
        serial_port = self.lineEdit.toPlainText()
        baudrate = self.lineEdit_2.toPlainText()
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

    def show_textedit_convert_sdsfile(self):
        """
        Opens a file dialog to select an SDS file and displays the selected file's path 
        """
        filepath , filetype = QFileDialog.getOpenFileName(
            directory='sds_out_dir', filter='*.sds')
        # show file path in textEdit
        self.textEdit_10_sdsF_2.setPlainText(filepath)
        self.textEdit_10_sdsF_2.ensureCursorVisible()

    def show_textedit_convert_outfile(self):
        """
        Opens a file dialog to save a file with a specific format based on the selected server type 
        and displays the selected file path in a text edit widget.
        """
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

    def show_textedit_convert_yamlfile(self):
        """
        Opens a file dialog for selecting a YAML file and displays the selected file's path 
        """
        filepath , filetype = QFileDialog.getOpenFileName(
            directory='sds_out_dir', filter='*.yml')
        # show file path in textEdit
        self.textEdit_9_yamlF_2.setPlainText(filepath)
        self.textEdit_9_yamlF_2.ensureCursorVisible()

    def execute_sds_convert(self):
        """
        Executes the SDS conversion process based on the provided configuration parameters.
        """
        convert_format = self.comboBox_serverType_convertFormat_2.currentText()
        ei_export_enable = self.checkBox_EI_2.isChecked()
        sds_file = self.textEdit_10_sdsF_2.toPlainText()
        out_file = self.textEdit_8_outDir_2.toPlainText()
        yaml_file = self.textEdit_9_yamlF_2.toPlainText()
        label = self.lineEdit_3.toPlainText()

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

    def show_textedit_tflite_model(self):
        """
        Opens a file dialog for selecting a TensorFlow Lite (*.tflite) model file 
        and displays the selected file path in a text edit widget.
        """
        filepath , filetype = QFileDialog.getOpenFileName(
            directory='models', filter='*.tflite')
        # show file path in textEdit
        self.textEdit_10.setPlainText(filepath)
        self.textEdit_10.ensureCursorVisible()

    def show_textedit_eisdk_path(self):
        """
        Opens a folder selection dialog for the user to choose the Edge Impulse SDK path.
        """
        open_fdir_path = get_download_folder()
        folderpath = QFileDialog.getExistingDirectory(
            self,
            "Select Edge Impulse SDK Folder",
            open_fdir_path,  # Default directory set to current directory
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        # show folder path in textEdit
        self.textEdit_12.setPlainText(folderpath)
        self.textEdit_12.ensureCursorVisible()

    def show_textedit_out_path_default(self, textEdit, default_dir_name="gen_proj_ml"):
        """
        Sets the default output path in the text edit widget.
        """
        textEdit.setPlainText(os.path.join(r'C:/', default_dir_name))
        textEdit.ensureCursorVisible()

    def show_textedit_out_path(self, textEdit, default_dir_name="gen_proj_ml"):
        """
        Opens a dialog for the user to select or create a folder, then sets the 
        text of `textEdit_8` to the selected folder path appended with a default 
        directory name.
        """
        open_fdir_path = "C:/"
        folderpath = QFileDialog.getExistingDirectory(
            self,
            "Select or Create Folder",
            open_fdir_path,  # Default directory set to C:/
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )

        textEdit.setPlainText(os.path.join(folderpath, default_dir_name))
        textEdit.ensureCursorVisible()

    def handle_combobox5_change(self, text):
        """
        Handles the change event for ComboBox5.
        """
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
        """
        Executes the NuML_TFLM_Tool based on the provided configuration parameters.
        """
        numl_type = self.comboBox_3.currentText()
        tflite_model = self.textEdit_10.toPlainText()
        board = self.comboBox_4.currentText()
        out_proj_path = self.textEdit_8.toPlainText()
        proj_type = self.comboBox_5.currentText()
        app_type = self.comboBox_6.currentText()
        arena_size = self.lineEdit_5.toPlainText()
        if not numl_type or not tflite_model or not out_proj_path:
            print("Error: Missing NuML_TFLM_Tool configuration parameters.")
            return

        for project_type_item in deployed_project_type_list:
            if proj_type == project_type_item[0]:
                proj_type = project_type_item[1]
                break

        for application_item in deployed_application_list:
            if app_type == application_item[0]:
                app_type = application_item[1]
                break

        if numl_type == "Generate project":
            try:
                if arena_size == "Auto":
                    numl_tool.start(['generate', '--model_file', tflite_model, '--board', board,
                                     '--output_path', out_proj_path, '--project_type', proj_type, '--application', app_type])
                else:
                    numl_tool.start(['generate', '--model_file', tflite_model, '--board', board,
                                     '--output_path', out_proj_path, '--project_type', proj_type, '--application', app_type, '--model_arena_size', arena_size])
            except RuntimeError as e:
                print(f"Error in thread: {e}")        

        print("Nuvoton tflu deployment executed done.")

    def execute_eisdk_deploy(self):
        """
        Executes the Edge Impulse SDK deployment process based on the provided configuration parameters.
        """
        numl_type = self.comboBox_11.currentText()
        eisdk_path = self.textEdit_12.toPlainText()
        board = self.comboBox_12.currentText()
        out_proj_path = self.textEdit_13.toPlainText()
        app_type = self.comboBox_14.currentText()
        test_data_label = self.lineEdit_6.toPlainText()
        if not eisdk_path or not out_proj_path:
            print("Error: Missing Edge Impulse SDK dir path or output path.")
            return

        for application_item in ei_deployed_application_list:
            if app_type == application_item[0]:
                app_type = application_item[1]
                break

        if numl_type == "Generate project":
            try:
                if test_data_label:
                    numl_tool.start(['generate_ei', '--ei_sdk_path', eisdk_path, '--board', board,
                                     '--output_path', out_proj_path, '--application', app_type, '--specify_label', test_data_label])
                else:
                    numl_tool.start(['generate_ei', '--ei_sdk_path', eisdk_path, '--board', board,
                                      '--output_path', out_proj_path, '--application', app_type])          
            except RuntimeError as e:
                print(f"Error in thread: {e}")

        print("EI SDK project deployment executed done.")

    def choose_upload_dir(self):
        """
        Opens a dialog for the user to select a folder and updates the textEdit widget
        """
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
        """
        Executes the upload process to Edge Impulse using the specified folder path, category, and label.
        """
        folderpath = self.textEdit_10_sdsF_3.toPlainText()
        category = self.comboBox_serverType_convertFormat_3.currentText()
        label = self.lineEdit_4.toPlainText()

        ei_upload = EiUploadDir()
        if label == 'None':
            label = None

        # Upload the directory to Edge Impulse
        try:
            ei_upload.upload_dir(folderpath, category, label)
        except RuntimeError as e:
            # Handle the error gracefully
            print(f"Error in thread: {e}")
        except Exception as e:
            # Handle all other exceptions gracefully
            print(f"An unexpected error occurred: {e}")

    def open_webcam_capture(self):
        """
        Opens or brings to the foreground the webcam capture window.
        """
        if self.webcam_window is None or not self.webcam_window.isVisible():
            self.webcam_window = WebcamWindow()
            self.webcam_window.show()
        else:
            self.webcam_window.raise_()
            self.webcam_window.activateWindow()


#if __name__ == '__main__':
# for Pystand
def main(argv=None):
    """
    Entry point for the application.

    This function initializes the QApplication, creates the main window, displays it, 
    and starts the application's event loop.

    Args:
        argv (list, optional): Command-line arguments passed to the application. 
            Defaults to None, which uses sys.argv.

    Raises:
        SystemExit: Exits the application when the event loop ends.
    """
    app = QApplication(sys.argv)
    window = myMainWindow()
    window.show()
    sys.exit(app.exec_())

# for Pystand
def start(argv=None):
    """
    Initializes and starts the main application.

    Args:
        argv (list, optional): A list of command-line arguments. Defaults to None.

    Returns:
        None
    """
    main(argv)
