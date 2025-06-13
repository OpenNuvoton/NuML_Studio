NuML_embedded
===
### Embedded UI version of NuML_Toolkit and collecting data Tool. This tool can be excuted without installing python and relative libs on Windows

## Tools
- `NuML_TFLM_Tool`: Tool for machine learning project generate base on TFLM framework. Reference from [NuML_Tool_TFLM](https://github.com/MaxCYCHEN/NuML_Toolkit).
- `sds_utilities`: Collecting data to local PC or uploading data to Edge Impulse. Reference from [SDS-Framework](https://github.com/ARM-software/SDS-Framework) and Edge Impulse.

## How this works
- Download from release.
- Double click the `NuML_tool_UI.exe`.
    - If you want to upload to Edge Impulse, and please update your project API on `API_key.txt`
- Others `*.exe` are CMD program, please check the examples in `cmd.exe` or `-h`

## Build youself
- Reference from [Python Releases for Windows](https://www.python.org/downloads/windows/) and [PyStand](https://github.com/skywind3000/PyStand)
- Download embedded Python `3.10.6` and copy to `runtime`
- In python `venv`, pip install the `requirements.txt`, and copy the `site-packages`. ⚠️ **Warning**: The version of python virtual env must be the same as the embedded version.
