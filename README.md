NuML_embedded
===
### This is the UI tool of TFLM ML model project generate and real time data collection tool for Nuvoton ML MCU. It can be executed on Windows without the need to install Python or any related libraries.

## How this works
- Download from newest [release](https://github.com/MaxCYCHEN/NuML_embedded/releases) or build yourself.
- Double-click `NuML_tool_UI.exe` to launch the tool.
    - If you want to upload to Edge Impulse, please update your project API key in `API_key.txt`.

- Other `*.exe` files are command-line programs. Please refer to the examples in `cmd.txt` or use the `-h` option for help.
    - Users can update the corresponding `*.int` file for each `*.exe` to perform testing, or execute the program without entering parameters.

## Support Functions
#### NuMaker-M55M1
- **Collecting data**: click the `Record Data` tab, and click `FLASH Firmware` to flash [firmware](https://github.com/OpenNuvoton/ML_M55M1_CMSIS_SDS/tree/master) into your board.
    - Supports the following options, and users can modify them as needed:
        - G-sensor: [SDS_Recorder_gsensor_uart_CMSIS firmware](https://github.com/OpenNuvoton/ML_M55M1_CMSIS_SDS/tree/master/M55M1BSP-3.01.001/SampleCode/SDS/SDS_Recorder_gsensor_uart_CMSIS)
        - Audio: [SDS_Recorder_audio_uart_CMSI firmware](https://github.com/OpenNuvoton/ML_M55M1_CMSIS_SDS/tree/master/M55M1BSP-3.01.001/SampleCode/SDS/SDS_Recorder_audio_uart_CMSI)        

- **Generate ML model project**: click the `Deployment` tab, and choose your TFLite int8 model. We support Keil/VSCode CMSIS projects.
    - Model inference firmware code generation.
    - G-snsor + ARM SDS firmware code generation.


## Tools we use
- `NuML_TFLM_Tool`: A tool for generating ML model projects based on the TFLM framework. It is based on and references the [NuML_Tool_TFLM](https://github.com/MaxCYCHEN/NuML_Toolkit).
- `sds_utilities`: A tool for collecting data to a local PC or uploading it to Edge Impulse. Based on the [SDS-Framework](https://github.com/ARM-software/SDS-Framework) and Edge Impulse.

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