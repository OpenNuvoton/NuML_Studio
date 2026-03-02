> **ARM<sup>®</sup> Cortex<sup>®</sup>- M**

**32-bit Microcontroller**

**NuMicro<sup>®</sup> NuML Studio**

**User Manual**

*The information described in this document is the exclusive
intellectual property of  
Nuvoton Technology Corporation and shall not be reproduced without
permission from Nuvoton.*

*Nuvoton is providing this document only for reference purposes of
NuMicro microcontroller based system design. Nuvoton assumes no
responsibility for errors or omissions.*

*All data and specifications are subject to change without notice.*

For additional information or questions, please contact: Nuvoton
Technology Corporation.

[<span custom-style="Hyperlink">www.nuvoton.com</span>](http://www.nuvoton.com)

***Table of Contents***

<div custom-style="toc 1">

[<span custom-style="Hyperlink">Chapter 1:</span>
<span custom-style="Hyperlink">Overview</span>](#chapter-1-overview)
[4](#chapter-1-overview)

</div>

<div custom-style="toc 1">

[<span custom-style="Hyperlink">Chapter 2:</span>
<span custom-style="Hyperlink">Data Collection</span>](#chapter-2-data-collection)
[5](#chapter-2-data-collection)

</div>

<div custom-style="toc 2">

[<span custom-style="Hyperlink">2.1</span>
<span custom-style="Hyperlink">Create Project</span>](#21-create-project)
[5](#21-create-project)

</div>

<div custom-style="toc 2">

[<span custom-style="Hyperlink">2.2</span>
<span custom-style="Hyperlink">Sensor Data Collection</span>](#22-sensor-data-collection)
[6](#22-sensor-data-collection)

</div>

<div custom-style="toc 2">

[<span custom-style="Hyperlink">2.3</span>
<span custom-style="Hyperlink">Audio Data Collection</span>](#23-audio-data-collection)
[9](#23-audio-data-collection)

</div>

<div custom-style="toc 2">

[<span custom-style="Hyperlink">2.4</span>
<span custom-style="Hyperlink">Image Data Collection</span>](#24-image-data-collection)
[9](#24-image-data-collection)

</div>

<div custom-style="toc 2">

[<span custom-style="Hyperlink">2.5</span>
<span custom-style="Hyperlink">Output Converting and Upload</span>](#25-output-converting-and-upload)
[11](#25-output-converting-and-upload)

</div>

<div custom-style="toc 1">

[<span custom-style="Hyperlink">Chapter 3:</span>
<span custom-style="Hyperlink">Generate ML Model Project</span>](#chapter-3-generate-ml-model-project)
[13](#chapter-3-generate-ml-model-project)

</div>

<div custom-style="toc 2">

[<span custom-style="Hyperlink">3.1</span>
<span custom-style="Hyperlink">LiteRT (TFLite) Deployment</span>](#31-litert-tflite-deployment)
[13](#31-litert-tflite-deployment)

</div>

<div custom-style="toc 2">

[<span custom-style="Hyperlink">3.2</span>
<span custom-style="Hyperlink">Edge Impulse Deployment</span>](#32-edge-impulse-deployment)
[14](#32-edge-impulse-deployment)

</div>

***List of Figures***

<div custom-style="table of figures">

> [<span custom-style="Hyperlink">Figure 2.1-1 Project management
> page</span>](#_Toc221026272) [5](#_Toc221026272)

</div>

<div custom-style="table of figures">

> [<span custom-style="Hyperlink">Figure 2.1-2 Create project</span>](#_Toc221026273)
> [6](#_Toc221026273)

</div>

<div custom-style="table of figures">

> [<span custom-style="Hyperlink">Figure 2.1-3 Open project page</span>](#_Toc221026274)
> [6](#_Toc221026274)

</div>

<div custom-style="table of figures">

> [<span custom-style="Hyperlink">Figure 2.2-1 Connect the NuMaker to PC
> USB</span>](#_Toc221026275) [7](#_Toc221026275)

</div>

<div custom-style="table of figures">

> [<span custom-style="Hyperlink">Figure 2.2-2 Flash the data collection
> firmware</span>](#_Toc221026276) [8](#_Toc221026276)

</div>

<div custom-style="table of figures">

> [<span custom-style="Hyperlink">Figure 2.2-3 Collect the data</span>](#_Toc221026277)
> [8](#_Toc221026277)

</div>

<div custom-style="table of figures">

> [<span custom-style="Hyperlink">Figure 2.2-4 Reviewing Capture
> Data</span>](#_Toc221026278) [9](#_Toc221026278)

</div>

<div custom-style="table of figures">

> [<span custom-style="Hyperlink">Figure 2.4-1 Steps of image data
> collection</span>](#_Toc221026279) [10](#_Toc221026279)

</div>

<div custom-style="table of figures">

> [<span custom-style="Hyperlink">Figure 2.5-1 Output page</span>](#_Toc221026280)
> [11](#_Toc221026280)

</div>

<div custom-style="table of figures">

> [<span custom-style="Hyperlink">Figure 2.5-2 Upload page</span>](#_Toc221026281)
> [12](#_Toc221026281)

</div>

<div custom-style="table of figures">

> [<span custom-style="Hyperlink">Figure 3.1-1 LiteRT (TFLite) Deployment
> page</span>](#_Toc221026282) [13](#_Toc221026282)

</div>

<div custom-style="table of figures">

> [<span custom-style="Hyperlink">Figure 3.2-1 Edge Impulse deployment
> page (image classification example)</span>](#_Toc221026283)
> [14](#_Toc221026283)

</div>

<br>

<br>

<br>

# Chapter 1: Overview

<div custom-style="Normal - Style Left  2 ch">

NuML Studio is a graphical user interface (GUI) tool designed to
simplify the development workflow of Machine Learning (ML) applications
for Nuvoton ML MCUs. It allows users to generate LiteRT for
Microcontrollers (TFLM) firmware projects, collect real-time sensor data
with Nuvoton ML MCU board, and interact with Edge Impulse without
requiring Python installation or additional software dependencies.

</div>

<div custom-style="Normal - Style Left  2 ch">

The tool provides an end-to-end environment—from data collection to
model deployment—tailored for Nuvoton’s NuMaker-M55M1 development board
and compatible ML firmware. These two modes are introduced in Chapters 2
and 3.

</div>

<div custom-style="Normal - Style Left  2 ch">

The NuML Studio repository is available on GitHub.

</div>

<div custom-style="Normal - Style Left  2 ch">

Please check the following link to get the latest update.

</div>

<div custom-style="Normal - Style Left  2 ch">

[<span custom-style="Hyperlink">https://github.com/OpenNuvoton/NuML_Studio/tree/main</span>](https://github.com/OpenNuvoton/NuML_Studio/tree/main)

</div>

<div custom-style="Normal - Style Left  2 ch">

This tool focuses on data collection and model deployment. For the
Machine Learning (ML) process—such as data processing, training, and
testing—users can refer to Nuvoton NuEdgeWise for model training
examples. Third-party sources like Edge Impulse can also be used, or you
can import your own fully quantized int8 LiteRT (TFLite) model into this
tool.

</div>

<div custom-style="Normal - Style Left  2 ch">

[<span custom-style="Hyperlink">https://github.com/OpenNuvoton/NuEdgeWise</span>](https://github.com/OpenNuvoton/NuEdgeWise)

</div>

<br>

<br>

<br>

# Chapter 2: Data Collection

## 2.1 Create Project

<div custom-style="Normal - Style Left  2 ch">

The first step in using NuML Studio is to create a project. You can
create a project for data collection, ML deployment firmware generation,
or both ([Figure 2.1-1](#_Toc221026272)).

</div>

<div custom-style="Normal - Style Left  2 ch">

Click the **“Choose”** button from **“Create Project”** to select a
directory, enter your project name, and then click **“Create This
Project”** to generate a new project ([Figure 2.1-2](#_Toc221026273)). NuML Studio creates a
folder in the specified path, and the project can be reopened later when
needed.

</div>

<div custom-style="Normal - Style Left  2 ch">

Before performing data collection, ensure that a project is opened. The
**“Open Project”** section allows you to open either the newly created
project or a previously saved one ([Figure 2.1-3](#_Toc221026274)).

</div>

![Project management page](./media/image2.png)
<div id="_Toc221026272">Figure 2.1-1 Project management page</div>

<br>

![Create project](./media/image3.png)
<div id="_Toc221026273">Figure 2.1-2 Create project</div>

<br>

![Open project page](./media/image4.png)
<div id="_Toc221026274">Figure 2.1-3 Open project page</div>

## 2.2 Sensor Data Collection

<div custom-style="Normal - Style Left  2 ch">

For sensor data collection, NuML Studio uses the G-sensor (MPU-6500) on
the NuMaker-M55M1 board, which provides acceleration data along the X,
Y, and Z axes. The data is streamed to the PC via UART.

</div>

<div custom-style="Normal - Style Left  2 ch">

To begin, connect the NuMaker board to the PC using a USB cable ([Figure 2.2-1](#_Toc221026275)). Select **“G-sensor (X, Y, Z)”** under **“Data Type”**, and flash
the corresponding firmware to the NuMaker board ([Figure 2.2-2](#_Toc221026276)).

</div>

<div custom-style="Normal - Style Left  2 ch">

Next, select the correct serial port and specify a data label in
**“Label Folder Name”**. A folder with the same name as the label will
be automatically created in your project directory to store the
collected raw data.

</div>

<div custom-style="Normal - Style Left  2 ch">

Once the NuMaker board is successfully connected, the right-hand panel
will prompt you to click **“Button 1”** to start recording. Click the button
again to stop recording and save the raw data file (with the .sds
extension) in your project ([Figure 2.2-3](#_Toc221026277)). You may record data for as long
as needed, and click the button again to start a new recording session,
which will create a separate file.

</div>

<div custom-style="Normal - Style Left  2 ch">

After completing all data collection, disconnect the serial port to
release the connection between the PC and the NuMaker board. NuML Studio
will remain ready for continued use.

</div>

<div custom-style="Normal - Style Left  2 ch">

The corresponding collection firmware can be found at the following
path:

</div>

<div custom-style="Normal - Style Left  2 ch">

NuML_Studio\app\NuML_TFLM_Tool\templates\ML_M55M1_CMSIS_SDS\M55M1BSP-3.01.002\SampleCode\SDS\SDS_Recorder_gsensor_uart_CMSIS

</div>

<div custom-style="Normal - Style Left  2 ch">

NuML Studio also supports easy preview of time-series data files (with
the .sds extension), such as sensor and audio data introduced in Section
2.3.

</div>

<div custom-style="Normal - Style Left  2 ch">

To preview data, select **“View”** from the left-side tree panel, then
choose the corresponding YAML file that describes the collected data.
(For information on how to configure this file, refer to the
app/sds_utilities in NuML Studio GitHub repository.)

</div>

<div custom-style="Normal - Style Left  2 ch">

Finally, select the desired .sds file from your project’s Data
Collection folder to display the recorded data ([Figure 2.2-4](#_Toc221026278)).

</div>

<br>

![Connect the NuMaker to PC USB](./media/image5.jpeg)
<div id="_Toc221026275">Figure 2.2-1 Connect the NuMaker to PC USB</div>

<br>

![Flash the data collection firmware](./media/image6.jpeg)
<div id="_Toc221026276">Figure 2.2-2 Flash the data collection firmware</div>

<br>

![Collect the data](./media/image7.png)
<div id="_Toc221026277">Figure 2.2-3 Collect the data</div>

<br>

![Reviewing Capture Data](./media/image8.png)
<div id="_Toc221026278">Figure 2.2-4 Reviewing Capture Data</div>

## 2.3 Audio Data Collection

<div custom-style="Normal - Style Left  2 ch">

The process for audio data collection is the same as for sensor data
collection. All steps are identical except that you need to select
**“Audio (16 kHz)”** under **“Data Type”**.

</div>

<div custom-style="Normal - Style Left  2 ch">

The corresponding collection firmware can be found at the following
path:

</div>

<div custom-style="Normal - Style Left  2 ch">

NuML_Studio\app\NuML_TFLM_Tool\templates\ML_M55M1_CMSIS_SDS\M55M1BSP-3.01.002\SampleCode\SDS\SDS_Recorder_audio_uart_CMSIS

</div>

## 2.4 Image Data Collection

<div custom-style="Normal - Style Left  2 ch">

For image data collection, select **“Image”** under **“Data Type”** and
flash the corresponding firmware to the NuMaker board.

</div>

<div custom-style="Normal - Style Left  2 ch">

Next, specify a data label in **“Label Folder Name”**. A folder with the
same name as the label will be automatically created in your project
directory to store the collected image files in JPG format.

</div>

<div custom-style="Normal - Style Left  2 ch">

Then, connect the PC to the HSUSB port on the NuMaker board. Click the
**“Camera Enable”** button to open the camera preview window. This
preview supports both the NuMaker’s CCAP camera and the PC webcam.

</div>

<div custom-style="Normal - Style Left  2 ch">

After selecting the desired camera (NuMaker or PC) and the preferred
resolution, click **“Start”** to begin the camera preview. You can then
click the **“Raw Image Collection”** button at any time to capture and
save the current image to your project’s Data Collection folder.

</div>

<div custom-style="Normal - Style Left  2 ch">

The corresponding collection firmware can be found at the following
link:

</div>

<div custom-style="Normal - Style Left  2 ch">

[<span custom-style="Hyperlink">https://github.com/OpenNuvoton/M55M1BSP/tree/master/SampleCode/StdDriver/HSUSBD_Video_CAM</span>](https://github.com/OpenNuvoton/M55M1BSP/tree/master/SampleCode/StdDriver/HSUSBD_Video_CAM)

</div>

<br>

![Steps of image data collection](./media/image9.jpeg)
<div id="_Toc221026279">Figure 2.4-1 Steps of image data collection</div>

## 2.5 Output Converting and Upload

<div custom-style="Normal - Style Left  2 ch">

After collecting sensor or audio raw data from Section 2.2 or 2.3, it is
necessary to convert the files into a more readable format, such as CSV
for sensor data or WAV for audio data. To begin, select **“Convert
Format”** based on your data type. If you are working with sensor data,
choose CSV; if you are working with audio data, choose WAV.

</div>

<div custom-style="Normal - Style Left  2 ch">

If the **“Edge Impulse Format & Export”** option is checked, the
converted data will be automatically uploaded to your Edge Impulse
project. (For more details, please refer to the Edge Impulse website.)
Before uploading, make sure that the Edge Impulse project API key has
been updated in the following file:

</div>

<div custom-style="Normal - Style Left  2 ch">

NuML_Studio/API_key.txt

</div>

<div custom-style="Normal - Style Left  2 ch">

Next, select the raw data file from the Input **“SDS Data Recording
File”** section, specify the desired output file name in the **“Output
File Name”** section, and select the corresponding YAML description file
from the **“YAML Description File”** section. If the **“Edge Impulse
Format & Export”** option is enabled, the label information will be
included in the Edge Impulse dataset by adding the label name as a
prefix to the original data file.

</div>

<div custom-style="Normal - Style Left  2 ch">

Finally, click the **“Execute”** button to generate the output file. If
Edge Impulse export is selected, the data will be automatically uploaded
to the linked Edge Impulse project ([Figure 2.5-1](#_Toc221026280)).

</div>

<div custom-style="Normal - Style Left  2 ch">

NuML Studio also supports uploading an entire data folder to Edge
Impulse. Simply select the folder that contains your collected data,
such as sensor CSV files, audio WAV files, or image files. Other file
types in the folder will be ignored during the upload process.

</div>

<div custom-style="Normal - Style Left  2 ch">

You can choose to upload the data to either the training or testing
dataset of your Edge Impulse project by selecting the desired option
under **“Category”**. To label all the files in the folder, enter the
label name in the **“Label”** text box before starting the upload ([Figure 2.5-2](#_Toc221026281)).

</div>

<br>

![Output page](./media/image10.png)
<div id="_Toc221026280">Figure 2.5-1 Output page</div>

<br>

![Upload page](./media/image11.png)
<div id="_Toc221026281">Figure 2.5-2 Upload page</div>

<br>

<br>

<br>

# Chapter 3: Generate ML Model Project

<div custom-style="Normal - Style Left  2 ch">

In machine learning, deployment refers to the process of porting an ML
model to run on a real device. One of the key functions of NuML Studio
is to help users deploy their own models, either as a TFLite int8
quantization model or as an Edge Impulse deployment package.

</div>

<div custom-style="Normal - Style Left  2 ch">

The primary purpose of NuML Studio’s deployment feature is to generate
model inference code that runs on the NuMaker platform. It also provides
several general example applications. Example applications include
support for CCAP, DMIC, sensor, and other peripheral drivers. Example
projects include real-time keyword spotting (KWS), image classification
with live image preview and so on.

</div>

## 3.1 LiteRT (TFLite) Deployment

<div custom-style="Normal - Style Left  2 ch">

Users can convert an int8 quantized LiteRT (TFLite) model into a
ready-to-run inference project for NuMaker by selecting **“Deployment” →
“Nuvoton”** from the left-side tree panel ([Figure 3.1-1](#_Toc221026282)).

</div>

<div custom-style="Normal - Style Left  2 ch">

First, select the TFLite model file from the **“TFLite Model File”**
section. Then, choose the desired **“Project Type”**. Currently, NuML
Studio supports two build environments: ARM VS Code CMSIS solution and
ARM Keil µVision.

</div>

<div custom-style="Normal - Style Left  2 ch">

Under the **“Application”** section, NuML Studio provides several
example templates, including Model Inference, G-sensor, Image
Classification, and Object Detection (YOLOv8-nano). Users can select an
example that best fits their application and use it as a starting point
for developing their own machine learning project.

</div>

<div custom-style="Normal - Style Left  2 ch">

For the NuMaker-M55M1 platform, the system automatically enables the
NPU, and the model must be compiled using the Vela compiler. Normally,
the tensor arena size is determined by Vela; however, advanced users can
manually adjust it in the **“Tensor Arena Size”** field if needed.

</div>

<div custom-style="Normal - Style Left  2 ch">

Once all settings are configured, NuML Studio will begin converting the
model and generating the corresponding inference example code. This
process may take a few minutes. The generated NuMaker firmware project
will be placed in the project directory you created at the beginning.

</div>

<br>

![LiteRT (TFLite) Deployment page](./media/image12.png)
<div id="_Toc221026282">Figure 3.1-1 LiteRT (TFLite) Deployment page</div>

## 3.2 Edge Impulse Deployment

<div custom-style="Normal - Style Left  2 ch">

NuML Studio also provides another deployment option—Edge Impulse—which
offers a complete end-to-end machine learning workflow in the cloud,
along with a deployment-ready C++ SDK. The SDK includes not only the
model inference code but also the necessary pre-processing and
post-processing functions. This feature helps users easily generate
firmware that can run their Edge Impulse project on NuMaker hardware.

</div>

<div custom-style="Normal - Style Left  2 ch">

A quick start guide on integrating with Edge Impulse and generating the
deployment package is available at:

</div>

<div custom-style="Normal - Style Left  2 ch">

[<span custom-style="Hyperlink">https://github.com/OpenNuvoton/NuML_Studio/blob/main/doc/QuickStart/QuickStart-EIProject.md</span>](https://github.com/OpenNuvoton/NuML_Studio/blob/main/doc/QuickStart/QuickStart-EIProject.md)

</div>

<div custom-style="Normal - Style Left  2 ch">

The downloaded Edge Impulse deployment package is provided as a
compressed file. Unzip the file first, then navigate to **“Deployment” →
“Edge Impulse”** in NuML Studio and select your deployment folder in the
**“Download Edge Impulse SDK Path”** section ([Figure 3.2-1](#_Toc221026283)).

</div>

<div custom-style="Normal - Style Left  2 ch">

Before executing, make sure that the Edge Impulse project API key has
been updated in the following file:

</div>

<div custom-style="Normal - Style Left  2 ch">

NuML_Studio/API_key.txt

</div>

<div custom-style="Normal - Style Left  2 ch">

Similar to the LiteRT (TFLite) deployment, Edge Impulse deployment also
provides several **“Application”** options, including model inference,
keyword spotting (KWS), and image classification examples. The **“Test
Data Label”** field is used for validating the deployment firmware with
offline test data. By entering a classification label, NuML Studio will
automatically download the corresponding test data to help users verify
whether the model’s inference behavior matches the expected results.

</div>

<div custom-style="Normal - Style Left  2 ch">

Once all settings are configured, NuML Studio will start generating the
inference example code integrated with the Edge Impulse SDK. This
process may take a few minutes. The generated NuMaker firmware project
will be saved in the project directory created earlier.

</div>

<br>

![Edge Impulse deployment page (image classification example)](./media/image13.png)
<div id="_Toc221026283">Figure 3.2-1 Edge Impulse deployment page (image classification example)</div>

<br>

<br>

<br>

**Important Notice**

**Using this software indicates your acceptance of the disclaimer
hereunder:**

**THIS SOFTWARE IS FOR YOUR REFERENCE ONLY AND PROVIDED "AS IS" AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE ARE DISCLAIMED. YOUR USING THIS SOFTWARE/FIRMWARE IS BASED ON
YOUR OWN DISCRETION, IN NO EVENT SHALL THE COPYRIGHT OWNER OR PROVIDER
BE LIABLE TO ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
THE POSSIBILITY OF SUCH DAMAGE.**

![Bottom Bar](./media/image14.png)
