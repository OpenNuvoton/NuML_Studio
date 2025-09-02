/* os */
#include "cmsis_os2.h"
/* sds */
#include "sds_play.h"

// Configuration
#ifndef PLAY_BUF_SIZE_ACCELEROMETER
    #define PLAY_BUF_SIZE_ACCELEROMETER      2048U
#endif

#ifndef PLAY_IO_THRESHOLD_ACCELEROMETER
    #define PLAY_IO_THRESHOLD_ACCELEROMETER     1024U
#endif

#ifndef SENSOR_HARDWARE_BUF_SIZE
    #define SENSOR_HARDWARE_BUF_SIZE        1024U // This value should match with the FIFO size of sensor hardware
#endif

#ifndef TEMP_BUF_SIZE
    #define TEMP_BUF_SIZE                   2048U
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


// Player identifier
static sdsPlayId_t playId_accelerometer;

// Player buffer
static float playBuf_accelerometer[PLAY_BUF_SIZE_ACCELEROMETER];

// Temporary buffer
static float tempBuf[TEMP_BUF_SIZE];