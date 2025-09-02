/* os */
#include "cmsis_os2.h"
/* sds */
#include "sds_rec.h"

#define USE_DMIC
#include "DMICRecord.h"

#define AUDIO_SAMPLE_BLOCK  4
#define AUDIO_SAMPLE_RATE   16000
#define AUDIO_CHANNEL       1

#define EVENT_CLOSE     (1U << 0)

// Configuration
#ifndef SDS_REC_BUF_SIZE_AUDIO
    #define SDS_REC_BUF_SIZE_AUDIO     (AUDIO_SAMPLE_RATE * 1)  // set SDS_REC_BUF_SIZE aligned with this array size
#endif

#ifndef SDS_REC_IO_THRESHOLD_AUDIO
    #define SDS_REC_IO_THRESHOLD_AUDIO    16000U // size of array
#endif

#ifndef SENSOR_POLLING_INTERVAL
    #define SENSOR_POLLING_INTERVAL         100U
#endif

#ifndef SENSOR_AUDIO_SIZE
    #define SENSOR_AUDIO_SIZE      8192
#endif

// Sensor identifiers
//static sensorId_t sensorId_accelerometer;

// Sensor configuration
//static sensorConfig_t *sensorConfig_accelerometer;

// Recorder identifiers
static sdsRecId_t recId_audio     = NULL;

// Recorder buffers
static int16_t recBuf_audio[SDS_REC_BUF_SIZE_AUDIO];  // set SDS_REC_BUF_SIZE aligned with this array size

// Temporary audio buffer for DMICRecord
static int16_t audioBuf[SENSOR_AUDIO_SIZE];

// Sensor close flag
static uint8_t close_flag = 0U;

// Event close sent flag
static uint8_t event_close_sent;

// Thread identifiers
static osThreadId_t thrId_demo;