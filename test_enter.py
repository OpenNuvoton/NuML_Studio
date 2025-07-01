#  vim: set ts=4 sw=4 tw=0 et ft=python :
import os
import sys

'''
Update the system path to include your testing application directory
'''
#from app.MainWindowControl import start
#from app.NuML_TFLM_Tool.numl_tool import start
from app.sds_utilities.sdsio_server import start

print()
msg = 'Hello from %s'%(os.path.abspath(__file__))
print(msg)
print()

print("SystemPaths:")
for path in sys.path:
    print('>', path)

#os.MessageBox(msg)

# Enter Point
if __name__ == "__main__":
    # test/cmd style
    #start()
    
    #start(['generate', '--model_file', 'models\ei-g-sensor-test2-classifier-tensorflow-lite-int8-quantized-model.3.tflite', 
    #'--board', 'NuMaker-M55M1', '--output_path', 'C:\gen_proj_vscode_1', 
    #'--project_type', 'uvision5_armc6', '--vs_ex_type', 'tflite_only'])

    start(['serial', '-p', 'COM8', '--baudrate', '115200', '--outdir', 'sds_out_dir'])

