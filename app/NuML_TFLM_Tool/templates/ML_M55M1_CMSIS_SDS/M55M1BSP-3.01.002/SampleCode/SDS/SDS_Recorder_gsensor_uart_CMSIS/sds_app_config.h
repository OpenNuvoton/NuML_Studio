/* os */
#include "cmsis_os2.h"
/* sds */
#include "sds_rec.h"
/* sensor interface */
#include "sensor_drv.h"
#include "sensor_config.h"

#define EVENT_CLOSE     (1U << 0)

// Configuration
#ifndef SDS_REC_BUF_SIZE_ACCELEROMETER
    #define SDS_REC_BUF_SIZE_ACCELEROMETER      2048U
#endif

#ifndef SDS_REC_IO_THRESHOLD_ACCELEROMETER
    #define SDS_REC_IO_THRESHOLD_ACCELEROMETER     512U
#endif

#ifndef SENSOR_HARDWARE_BUF_SIZE
    #define SENSOR_HARDWARE_BUF_SIZE        1024U // This value should match with the FIFO size of sensor hardware
#endif

#ifndef SENSOR_ACCELEROMETER_NUM_PER_SAMPLE
    #define SENSOR_ACCELEROMETER_NUM_PER_SAMPLE   3U // Each sample has X, Y ,Z
#endif

#ifndef SENSOR_ACCELEROMETER_SIZE
    #define SENSOR_ACCELEROMETER_SIZE            (SENSOR_HARDWARE_BUF_SIZE / SENSOR3_SAMPLE_SIZE * SENSOR_ACCELEROMETER_NUM_PER_SAMPLE) // 1024/(6*2) = 85, 85*3 = 255

    #ifndef SENSOR_POLLING_INTERVAL
        #define SENSOR_POLLING_INTERVAL         100U  // 100ms
    #endif
#endif

// Sensor identifiers
static sensorId_t sensorId_accelerometer;
//static sensorId_t sensorId_temperatureSensor;

// Sensor configuration
static sensorConfig_t *sensorConfig_accelerometer;
//static sensorConfig_t *sensorConfig_temperatureSensor;

// Recorder identifiers
static sdsRecId_t recId_accelerometer     = NULL;
//static sdsRecId_t recId_temperatureSensor = NULL;

// Recorder buffers
static float recBuf_accelerometer[SDS_REC_BUF_SIZE_ACCELEROMETER];
//static uint8_t recBuf_temperatureSensor[REC_BUF_SIZE_TEMPERATURE_SENSOR];

// Temporary sensor buffer
static float sensorBuf[SENSOR_ACCELEROMETER_SIZE];

// Sensor close flag
static uint8_t close_flag = 0U;

// Event close sent flag
static uint8_t event_close_sent;

// Thread identifiers
static osThreadId_t thrId_demo;