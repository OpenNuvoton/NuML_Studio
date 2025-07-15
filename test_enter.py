#  vim: set ts=4 sw=4 tw=0 et ft=python :
import os
import sys

'''
Update the import path to include your testing application directory
'''

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
    from app.MainWindowControl import start
    start()
    
    #from app.NuML_TFLM_Tool.numl_tool import start
    #start(['generate', '--model_file', 'models\ei-g-sensor-test2-classifier-tensorflow-lite-int8-quantized-model.3.tflite', 
    #'--board', 'NuMaker-M55M1', '--output_path', 'C:\gen_proj_vscode_1', 
    #'--project_type', 'uvision5_armc6', '--vs_ex_type', 'tflite_only'])

    #from app.sds_utilities.sdsio_server import start
    #start(['serial', '-p', 'COM8', '--baudrate', '921600', '--outdir', 'sds_out_dir'])
    #start(['serial', '-p', 'COM8', '--baudrate', '115200', '--outdir', 'sds_out_dir'])

    #from app.sds_utilities.sds_convert import start
    #start(['audio_wav', '-i', 'sds_out_dir/DMicrophone.3.sds', 
    #'-o', 'sds_out_dir/DMicrophone_3.wav', 
    #'-y', 'sds_out_dir/DMicrophone.sds.yml'])

