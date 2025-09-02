# M55M1_SDS
M55M1 version of [ARM SDS-Framework](https://github.com/ARM-software/SDS-Framework)(v1.1.0)

## Requirement
1. Need CMSIS driver (This will be added in M55M1BSP in the future) 
2. M55M1BSP V3.01.001
3. Keil uVision5 or VSCode
## Install
- Manual  
    1. Download M55M1BSP from [BSP release](https://github.com/OpenNuvoton/M55M1BSP/releases)
    2. Unzip BSP zip file
    3. Copy this patch folders/files (`M55M1BSP-3.01.001`) to BSP

- Folder structure
```
M55M1BSP-3.01.001
|--- Document
|--- Library
|    |--- ...
|    |--- SDS-Framework (This M55M1_SDS patch)
|    |--- ...
|--- SampleCode
|    |--- SDS (This M55M1_SDS patch)
|    |--- CotrexM55
|    |--- Crypto
|    |--- FreeRTOS
|    |--- Hard_Fault_Sample
|    |--- ISP
|    |--- MachineLearning
|    |--- NuEdgeWise
|    |--- NuMaker_M55M1
|    |--- PowerDelivery
|    |--- PowerManagement
|    |--- SecureApplication
|    |--- Semihost
|    |--- StdDriver
|    |--- Template
|    |--- TrustZone
|    |--- XOM
|--- ThirdParty
|    |--- MPU6500 (This M55M1_SDS patch)
|    |--- executorch
|    |--- FatFs
|    |--- FreeRTOS
|    |--- libjpeg
|    |--- libmad
|    |--- lwIP
|    |--- mbedtls
|    |--- ml-embedded-evaluation-kit
|    |--- openmv
|    |--- paho.mqtt.embedded-c
|    |--- shine
|    |--- tflite_micro
|--- LICENSE
|--- README.md

```
## Config of NuMaker_M55M1
### USART - Recorder
- Please set `#define RTE_USART<NUMBER> 1` in `Library\CMSIS\Driver\Source\RTE_Device\RTE_Device_USART.h` 
to align with `#define SDSIO_USART_DRIVER_NUMBER <NUMBER>` in `RTE\SDS\sdsio_config_serial_usart.h`.
- For example using UART0: `#define RTE_USART 1`, `#define SDSIO_USART_DRIVER_NUMBER 0`. And please remember to update to `#define USING_UART0    0` in `\Library\Device\Nuvoton\M55M1\Include\system_M55M1.h`. 
- This way of using UART0, the user can transmit data by directly connecting the NuMaker-M55M1 to a PC without needing an additional USART port.
- For debug printing, UART6 is used. Users need to connect and configure the appropriate pins for UART6. (TX: PE14, RX: PE15)

### USART - Player
- Place the `*.sds` files on a USB drive and plug the USB into the HSUSB port on the NuMaker-M55M1.
- Run the program.

