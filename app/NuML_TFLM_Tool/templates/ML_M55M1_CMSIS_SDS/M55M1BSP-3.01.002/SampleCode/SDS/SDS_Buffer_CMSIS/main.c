/*----------------------------------------------------------------------------
 * Name:    main.c
 *----------------------------------------------------------------------------*/

/* Includes ------------------------------------------------------------------*/
#include "NuMicro.h"
#include "sds_app_config.h"

#include <string.h>

#ifndef INPUT_SAMPLE_NUMBER_MPU6500
    #define INPUT_SAMPLE_NUMBER_MPU6500      200U // 100(HZ) * 2(S) = 200(Sample) per Inference or Calculation
#endif

#define __DEBUG_PRINT

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
            printf("sdsRecWrite Done: num: %u, buf_size: %u\r\n", num, buf_size);
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

static void SYS_Init(void)
{
    /* Unlock protected registers */
    SYS_UnlockReg();

    /*---------------------------------------------------------------------------------------------------------*/
    /* Init System Clock                                                                                       */
    /*---------------------------------------------------------------------------------------------------------*/
    /* Enable PLL0 220MHz clock from HIRC and switch SCLK clock source to PLL0 */
    CLK_SetBusClock(CLK_SCLKSEL_SCLKSEL_APLL0, CLK_APLLCTL_APLLSRC_HIRC, FREQ_220MHZ);

    /* Update System Core Clock */
    /* User can use SystemCoreClockUpdate() to calculate SystemCoreClock. */
    SystemCoreClockUpdate();

    /* Enable UART module clock */
    SetDebugUartCLK();

    /*---------------------------------------------------------------------------------------------------------*/
    /* Init I/O Multi-function                                                                                 */
    /*---------------------------------------------------------------------------------------------------------*/
    SetDebugUartMFP();

    /* Enable LPI2C module clock, for G-sensor*/
    CLK_EnableModuleClock(LPI2C0_MODULE);

    SET_LPI2C0_SCL_PC12();

    SET_LPI2C0_SDA_PC11();

    /* Open LPI2C0 module and set bus clock */
    //LPI2C_Open(LPI2C0, 100000);

    /* Lock protected registers */
    SYS_LockReg();
}

// Sensor Demo
static __NO_RETURN void demo(void *argument)
{

    /* Init the SDS Buffer*/
    uint32_t  n, num, flags, buf_idx;
    uint32_t input_feature_size = INPUT_SAMPLE_NUMBER_MPU6500 * SENSOR_ACCELEROMETER_NUM_PER_SAMPLE;
    uint32_t sliding_window_size = input_feature_size / 2;
    float  alloc_buf[input_feature_size];
    float  *buf;
    double    abs;
    double    abs_max;
    double     x_max, y_max, z_max;

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

                num = sdsRead(sdsId_MPU6500, &buf[buf_idx], sliding_window_size * sizeof(sensorBuf[0]));
#if defined(__DEBUG_PRINT)
                printf("Detected! buf_idx: %d,  num: %d, n: %d, buf[299]: %f, buf[599]: %f\r\n", buf_idx, num, n++, buf[299], buf[599]);
#endif

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
    SYS_Init();

    /* Init Debug UART for printf */
    InitDebugUart();

    osKernelInitialize();                // Initialize CMSIS-RTOS2

    osThreadNew(demo, NULL, NULL);   // Create validation main thread

    osKernelStart();                     // Start thread execution

    for (;;) {}

}
