NuML-GUI
===
### This is the UI tool of TFLM ML model project generate and real time data collection tool for Nuvoton ML MCU. It can be executed on Windows without the need to install Python or any related libraries.

## How this works
- Download from newest [release](https://github.com/MaxCYCHEN/NuML_embedded/releases) or build yourself.
- Double-click `NuML-GUI.exe` to launch the tool.
    - If you want to upload to Edge Impulse or download single test data to deployment, please update your project API key in `API_key.txt`.

- Other `*.exe` files are command-line programs. Please refer to the examples in `cmd.txt` or use the `-h` option for help.
    - Users can update the corresponding `*.int` file for each `*.exe` to perform testing, or execute the program without entering parameters.

## Support Functions
#### NuMaker-M55M1
- **Collecting data**: click the `- Recording` tab, and click `FLASH Firmware` to flash [firmware](https://github.com/OpenNuvoton/ML_M55M1_CMSIS_SDS/tree/master) into your board.
    - Supports the following options, and users can modify them as needed:
        - G-sensor (3-axis): [SDS_Recorder_gsensor_uart_CMSIS firmware](https://github.com/OpenNuvoton/ML_M55M1_CMSIS_SDS/tree/master/M55M1BSP-3.01.001/SampleCode/SDS/SDS_Recorder_gsensor_uart_CMSIS)
        - Audio (16Khz): [SDS_Recorder_audio_uart_CMSI firmware](https://github.com/OpenNuvoton/ML_M55M1_CMSIS_SDS/tree/master/M55M1BSP-3.01.001/SampleCode/SDS/SDS_Recorder_audio_uart_CMSI)
        - Image (supports UVC using the NuMaker-M55M1's image sensor or the PC's webcam)
    - Convert the data to standard format in `- Output` tab:
        - Users can select `csv format` to convert sensor `*.sds` data into `*.csv`.
        - User can select `audio_wav format` to convert audio `*.sds` data  into `*.wav`.
        - Images collected in `CAM_APP` under `Recording` are already saved as `*.jpg`
     
- **Upload data to EdgeImpulse**:
    - Please update your Edge Impulse project API key in `API_key.txt`.
    - In `- Output` tab, user can enable `Edge Impulse format & export` to upload your data.
    - In `- Upload` tab, an entire data directory can be uploaded at once.

- **Generate ML Model Project**: 
    - Click the `Deployment`, `- Nuvoton` tab, and select your TFLite int8 model. Keil and VSCode CMSIS projects are supported.
        - Model inference firmware code generation.
        - G-sensor model with ARM SDS and RTX5 firmware code generation.
        - Image classification firmware code generation.
    - Click the `Deployment`, `- EI` tab, and select your downloaded Edge Impulse SDK folder (Please  selected deployment as `Ethos-U55-256 library`). Keil and VSCode CMSIS projects are supported.
        - Model inference firmware code generation.    


## Tools we use
- `NuML_TFLM_Tool`: A tool for generating ML model projects based on the TFLM framework. It is based on and references the [NuML_Tool_TFLM](https://github.com/MaxCYCHEN/NuML_Toolkit).
- `sds_utilities`: A tool for collecting data to a local PC or uploading it to Edge Impulse. Based on the [SDS-Framework](https://github.com/ARM-software/SDS-Framework) and Edge Impulse.
- `Edge Impulse API`: https://docs.edgeimpulse.com/tools/libraries/sdks/studio/python/edgeimpulse/data

## Build yourself
- References:
    - [Embedded Python Releases for Windows](https://www.python.org/downloads/windows/)

    - [PyStand](https://github.com/skywind3000/PyStand)
- Steps:

- Download the embedded Python `3.10.6` and copy it to the `runtime` directory.

- In a Python virtual environment (venv), use pip to install the dependencies listed in `requirements.txt`, then copy the `site-packages` directory to here.
**Warning**: The version of the Python virtual environment must exactly match the embedded Python version.

- Call the CLI module's entry point directly as a Python module using the embedded Python
    - Edit `python310._pth` (depends on your version) in `runtime` to add your `site-packages`. (The example is in `runtime/python310._pth`)
