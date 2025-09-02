/*----------------------------------------------------------------------------
 * Name:    main.c
 *----------------------------------------------------------------------------*/
//#include <cstdio>
/* Includes ------------------------------------------------------------------*/
#include "NuMicro.h"
#include "sds_app_config.h"

#include <string.h>

//#define __DEBUG_PRINT

// NN inference
#include "BufAttributes.hpp"
#include "NNModel.hpp"       /* Model API */
#include "ModelFileReader.h"
#include "ff.h"
#define LOG_LEVEL             1
#include "log_macros.h"      /* Logging macros (optional) */
#include "Classifier.hpp"
#include "Labels.hpp"
#include "BoardInit.hpp"      /* Board initialisation */

#ifndef INPUT_SAMPLE_NUMBER_MPU6500
    #define INPUT_SAMPLE_NUMBER_MPU6500      200U // 100(HZ) * 2(S) = 200(Sample) per Inference or Calculation
#endif

//#define __PROFILE__
/****************************************************************************
 * autogen section: Model in SD
 ****************************************************************************/
//#define __LOAD_MODEL_FROM_SD__

#undef ACTIVATION_BUF_SZ
/****************************************************************************
 * autogen section: Activation size
 ****************************************************************************/
#define ACTIVATION_BUF_SZ (18432)

#define MODEL_AT_HYPERRAM_ADDR 0x82400000

#include "Profiler.hpp"

namespace arm
{
namespace app
{
/* Tensor arena buffer */
static uint8_t tensorArena[ACTIVATION_BUF_SZ] ACTIVATION_BUF_ATTRIBUTE;

/* Optional getter function for the model pointer and its size. */
namespace nn
{
extern uint8_t *GetModelPointer();
extern size_t GetModelLen();
} /* namespace nn */
} /* namespace app */
} /* namespace arm */


/* Private functions ---------------------------------------------------------*/

// Read sensor thread
static __NO_RETURN void read_sensors(void *argument)
{
    uint32_t num, buf_size, tick, max_num;
    (void)   argument;

    tick = osKernelGetTickCount();

    for (;;)
    {
        max_num = SENSOR_ACCELEROMETER_SIZE / SENSOR_ACCELEROMETER_NUM_PER_SAMPLE;
        num = sensorReadSamples(sensorId_MPU6500, max_num, sensorBuf, SENSOR_HARDWARE_BUF_SIZE);

        if (num != 0U)
        {
            buf_size = num * SENSOR_ACCELEROMETER_NUM_PER_SAMPLE * sizeof(sensorBuf[0]);
            num = sdsWrite(sdsId_MPU6500, sensorBuf, buf_size);
#if defined(__DEBUG_PRINT)
            //printf("sdsRecWrite Done: num: %u, buf_size: %u\r\n", num, buf_size);
#endif

            if (num != buf_size)
            {
                printf("%s: SDS write failed\r\n", sensorConfig_MPU6500->name);
            }
        }
        else
        {
            printf("sensorReadSamples NUM is zero!!\r\n");
        }

        tick += SENSOR_POLLING_INTERVAL;
        osDelayUntil(tick);
    }
}

// SDS event callback
static void sds_event_callback(sdsId_t id, uint32_t event, void *arg)
{
    (void)arg;

    if ((event & SDS_EVENT_DATA_HIGH) != 0U)
    {
        if (id == sdsId_MPU6500)
        {
            osThreadFlagsSet(thrId_demo, EVENT_DATA_MPU6500);
        }
    }
}

// Sensor Demo
static __NO_RETURN void demo(void *argument)
{

#if defined(__LOAD_MODEL_FROM_SD__)

    /* Copy model file from SD to HyperRAM*/
    int32_t i32ModelSize;

    printf("==================== Load model file from SD card =================================\n");
    printf("Please copy NN_ModelInference/Model/xxx_vela.tflite to SDCard:/nn_model.tflite     \n");
    printf("===================================================================================\n");
    i32ModelSize = PrepareModelToHyperRAM();

    if (i32ModelSize <= 0)
    {
        printf_err("Failed to prepare model\n");
        return 1;
    }

    /* Model object creation and initialisation. */
    arm::app::NNModel model;

    if (!model.Init(arm::app::tensorArena,
                    sizeof(arm::app::tensorArena),
                    (unsigned char *)MODEL_AT_HYPERRAM_ADDR,
                    i32ModelSize))
    {
        printf_err("Failed to initialise model\n");
    }

#else

    info("Set tesnor arena cache policy to WTRA \n");

    /* Model object creation and initialisation. */
    arm::app::NNModel model;

    if (!model.Init(arm::app::tensorArena,
                    sizeof(arm::app::tensorArena),
                    arm::app::nn::GetModelPointer(),
                    arm::app::nn::GetModelLen()))
    {
        printf_err("Failed to initialise model\n");
    }

#endif

    /* Setup cache poicy of tensor arean buffer */
    info("Set tesnor arena cache policy to WTRA \n");
    const std::vector<ARM_MPU_Region_t> mpuConfig =
    {
        {
            // SRAM for tensor arena
            ARM_MPU_RBAR(((unsigned int)arm::app::tensorArena),        // Base
                         ARM_MPU_SH_NON,    // Non-shareable
                         0,                 // Read-only
                         1,                 // Non-Privileged
                         1),                // eXecute Never enabled
            ARM_MPU_RLAR((((unsigned int)arm::app::tensorArena) + ACTIVATION_BUF_SZ - 1),        // Limit
                         eMPU_ATTR_CACHEABLE_WTRA) // Attribute index - Write-Through, Read-allocate
        },
    };

    // Setup MPU configuration
    InitPreDefMPURegion(&mpuConfig[0], mpuConfig.size());

    size_t numOutput = model.GetNumOutputs();
    TfLiteTensor *inputTensor   = model.GetInputTensor(0);
    TfLiteTensor *outputTensor = model.GetOutputTensor(0);

    CLK_SysTickDelay(2000);

    arm::app::QuantParams inQuantParams = arm::app::GetTensorQuantParams(inputTensor);

    /* Classifier object for results */
    arm::app::Classifier classifier;
    /* Object to hold classification results */
    std::vector<arm::app::ClassificationResult> singleInfResult;
    /* Object to hold label strings. */
    std::vector<std::string> labels;
    /* Populate the labels here. */
    GetLabelsVector(labels);

    /* Init the SDS Buffer*/
    uint32_t  n, num, flags, buf_idx;
    const uint32_t input_feature_size = INPUT_SAMPLE_NUMBER_MPU6500 * SENSOR_ACCELEROMETER_NUM_PER_SAMPLE;
    uint32_t sliding_window_size = input_feature_size / 2;
    float  alloc_buf[input_feature_size];
    float  *buf;

    buf = alloc_buf;

    thrId_demo = osThreadGetId();

    printf("SENSOR: sensorGetId\n");
    // Get sensor identifier
    sensorId_MPU6500 = sensorGetId("Accelerometer");

    printf("SENSOR: sensorGetConfig\n");
    // Get sensor configuration
    sensorConfig_MPU6500 = sensorGetConfig(sensorId_MPU6500);

    printf("SDS: sdsOpen\n");
    // Open SDS
    sdsId_MPU6500 = sdsOpen(sdsBuf_mpu6500, sizeof(sdsBuf_mpu6500),
                            0U, SDS_THRESHOLD_MPU6500 * sizeof(sdsBuf_mpu6500[0]));

    printf("SDS: sdsRegisterEvents\n");
    // Register SDS events
    sdsRegisterEvents(sdsId_MPU6500, sds_event_callback, SDS_EVENT_DATA_HIGH, NULL);

    printf("SENSOR: sensorEnable\n");
    // Enable sensor
    sensorEnable(sensorId_MPU6500);
    printf("SENSOR: Accelerometer enabled\r\n");

    // Create sensor thread
    osThreadNew(read_sensors, NULL, NULL);

    buf_idx = -sliding_window_size;

    for (;;)
    {
        flags = osThreadFlagsWait(EVENT_DATA_MPU6500, osFlagsWaitAny, osWaitForever);

        if ((flags & osFlagsError) == 0U)
        {

            // Accelerometer data event
            if ((flags & EVENT_DATA_MPU6500) != 0U)
            {
                // sliding window
                if (buf_idx + sliding_window_size >= input_feature_size)
                {
                    memmove(buf, &buf[sliding_window_size], (input_feature_size - sliding_window_size) * sizeof(buf[0]));
                    // The first window size is been shifted and the idx keep same
                }
                else
                {
                    buf_idx += sliding_window_size;
                }

                // get the buf
                num = sdsRead(sdsId_MPU6500, &buf[buf_idx], sliding_window_size * sizeof(sensorBuf[0]));
#if defined(__DEBUG_PRINT)
                printf("Detected! buf_idx: %d,  num: %d, n: %d, buf[299]: %f, buf[599]: %f\r\n", buf_idx, num, n++, buf[299], buf[599]);
#endif

                // Quantize input tensor data. set all input vaule to 0.5
                //debug("inputTensor->bytes: %d, inQuantParams.scale: %lf\n", inputTensor->bytes, inQuantParams.scale);
                auto *signed_req_data = static_cast<int8_t *>(inputTensor->data.data);

                for (size_t i = 0; i < inputTensor->bytes; i++)
                {
                    auto i_data_int8 = static_cast<int8_t>((buf[i] / inQuantParams.scale) + inQuantParams.offset);
                    signed_req_data[i] = std::min<int8_t>(INT8_MAX, std::max<int8_t>(i_data_int8, INT8_MIN));
                }

                // Inference
                if (!model.RunInference())
                {
                    printf_err("Inference failed.");
                }

                //Dequantize output tensor data
                for (int i = 0; i < numOutput; i ++)
                {
                    outputTensor = model.GetOutputTensor(i);
                    //arm::app::QuantParams outputQuantParams = arm::app::GetTensorQuantParams(outputTensor);
                    //int8_t *tensorOutputData = outputTensor->data.int8;
                    //
                    //for(int j = 0; j < outputTensor->bytes; j ++)
                    //{
                    //
                    //  outputQuantParams.scale * static_cast<float>(tensorOutputData[j] - outputQuantParams.offset);
                    //  debug("Tensor output[%d][%d]: %f\n",i,j, );
                    //}

                    classifier.GetClassificationResults(outputTensor, singleInfResult, labels, 1, false);

                    for (const auto &result : singleInfResult)
                    {

                        info("inference #:  label: %s, score: %f;\n",
                             result.m_label.c_str(), result.m_normalisedVal);

                    }

                }

                // Output

            }
        }
    }


}

/**
  * @brief  Main program
  * @param  None
  * @retval None
  */
int main(void)
{
    /* Init System, IP clock and multi-function I/O */
    //SYS_Init();
    BoardInit();
    printf("Test BoardInit\n");

    /* Init Debug UART for printf */
    //InitDebugUart();

    osKernelInitialize();                // Initialize CMSIS-RTOS2

    osThreadNew(demo, NULL, NULL);   // Create validation main thread

    osKernelStart();                     // Start thread execution

    for (;;) {}

}
