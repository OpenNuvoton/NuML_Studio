/* os */
#include "cmsis_os2.h"
/* sds */
#include "sds.h"
/* sensor interface */
#include "sensor_drv.h"
#include "sensor_config.h"

// Configuration
#define EVENT_DATA_MPU6500        (1U << 0)

#ifndef SDS_BUF_SIZE_MPU6500
    #define SDS_BUF_SIZE_MPU6500      2048U
#endif

#ifndef SDS_THRESHOLD_MPU6500
    #define SDS_THRESHOLD_MPU6500     512U
#endif

#ifndef SENSOR_POLLING_INTERVAL
    #define SENSOR_POLLING_INTERVAL         100U  // 100ms
#endif

#ifndef SENSOR_HARDWARE_BUF_SIZE
    #define SENSOR_HARDWARE_BUF_SIZE        1024U // This value should match with the FIFO size (bit) of sensor hardware
#endif

#ifndef SENSOR_ACCELEROMETER_NUM_PER_SAMPLE
    #define SENSOR_ACCELEROMETER_NUM_PER_SAMPLE   3U // Each sample has X, Y ,Z
#endif

#ifndef SENSOR_ACCELEROMETER_SIZE
    #define SENSOR_ACCELEROMETER_SIZE            (SENSOR_HARDWARE_BUF_SIZE / SENSOR3_SAMPLE_SIZE * SENSOR_ACCELEROMETER_NUM_PER_SAMPLE) // 1024/(6*2) = 85, 85*3 = 255
#endif


// Sensor identifier
static sensorId_t sensorId_MPU6500;

// Sensor configuration
static sensorConfig_t *sensorConfig_MPU6500;

// SDS identifier
static sdsId_t sdsId_MPU6500;

// SDS buffer
static float sdsBuf_mpu6500[SDS_BUF_SIZE_MPU6500];

// Temporary sensor buffer
static float sensorBuf[SENSOR_ACCELEROMETER_SIZE];

// Thread identifiers
static osThreadId_t thrId_demo;