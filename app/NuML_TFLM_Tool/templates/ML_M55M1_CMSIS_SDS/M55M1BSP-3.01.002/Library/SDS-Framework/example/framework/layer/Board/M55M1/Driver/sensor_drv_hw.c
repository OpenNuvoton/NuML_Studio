/*
 * Copyright (c) 2022-2023 Arm Limited. All rights reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 *
 * Licensed under the Apache License, Version 2.0 (the License); you may
 * not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an AS IS BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// Sensor driver for B-U585I-IOT02A

#include "sensor_drv.h"
#include "sensor_drv_hw.h"
#include "sensor_config.h"

#include "driver_mpu6500_fifo.h"

#ifndef SENSOR_NO_LOCK
#include "cmsis_os2.h"

// MPU6500
mpu6500_address_t addr = MPU6500_ADDRESS_AD0_HIGH;
mpu6500_interface_t interface = MPU6500_INTERFACE_IIC;
// FIFO clear write sample, the max mpu6500 FIFO size is 1024 which is 85 samples (85 * 12)
uint16_t len_sample;
static int16_t accel_raw_sp[85][3];
static float accel_g_sp[255];
static int16_t gyro_raw_sp[85][3];
static float gyro_dps_sp[255];

// Mutex lock
static osMutexId_t lock_id  = NULL;
static uint32_t    lock_cnt = 0U;

static inline void sensorLockCreate(void)
{
    if (lock_cnt == 0U)
    {
        lock_id = osMutexNew(NULL);
    }

    lock_cnt++;
}
static inline void sensorLockDelete(void)
{
    if (lock_cnt != 0U)
    {
        lock_cnt--;

        if (lock_cnt == 0U)
        {
            osMutexDelete(lock_id);
        }
    }
}
static inline void sensorLock(void)
{
    osMutexAcquire(lock_id, osWaitForever);
}
static inline void sensorUnLock(void)
{
    osMutexRelease(lock_id);
}
#else
static inline void sensorLockCreate(void) {}
static inline void sensorLockDelete(void) {}
static inline void sensorLock(void) {}
static inline void sensorUnLock(void) {}
#endif


// Temperature Sensor

//static int32_t TemperatureSensor_Enable (void) {
//  int32_t ret = SENSOR_ERROR;
//  float   value;
//
//  sensorLockCreate();
//  sensorLock();
//  if (BSP_ENV_SENSOR_Enable(0, ENV_TEMPERATURE) == BSP_ERROR_NONE) {
//    BSP_ENV_SENSOR_GetValue(0, ENV_TEMPERATURE, &value);
//    ret = SENSOR_OK;
//  }
//  sensorUnLock();
//
//  return ret;
//}
//
//static int32_t TemperatureSensor_Disable (void) {
//  int32_t ret = SENSOR_ERROR;
//
//  sensorLock();
//  if (BSP_ENV_SENSOR_Disable(0, ENV_TEMPERATURE) == BSP_ERROR_NONE) {
//    ret = SENSOR_OK;
//  }
//  sensorUnLock();
//  sensorLockDelete();
//
//  return ret;
//}
//
//static uint32_t TemperatureSensor_GetOverflow (void) {
//  return 0U;
//}
//
//static uint32_t TemperatureSensor_ReadSamples (uint32_t num_samples, void *buf) {
//  uint32_t num = 0U;
//  int32_t  ret;
//  uint8_t  stat;
//  float    value;
//
//  (void)num_samples;
//
//  sensorLock();
//  ret = HTS221_TEMP_Get_DRDY_Status(Env_Sensor_CompObj[0], &stat);
//  if ((ret == 0) && (stat != 0U)) {
//    if (BSP_ENV_SENSOR_GetValue(0, ENV_TEMPERATURE, &value) == BSP_ERROR_NONE) {
//      memcpy(buf, &value, sizeof(float));
//      num = 1U;
//    }
//  }
//  sensorUnLock();
//
//  return num;
//}
//
//sensorDrvHW_t sensorDrvHW_0 = {
//  NULL,
//  TemperatureSensor_Enable,
//  TemperatureSensor_Disable,
//  TemperatureSensor_GetOverflow,
//  TemperatureSensor_ReadSamples,
//  NULL,
//  NULL
//};


// Accelerometer

static int32_t Accelerometer_Enable(void)
{

    int32_t ret = SENSOR_ERROR;
    len_sample = 100;

    sensorLockCreate();
    sensorLock();

    if (mpu6500_fifo_init(interface, addr) == 0)
    {
        // Clear MPU6500 FIFO
        mpu6500_interface_delay_ms(10);

        if (mpu6500_fifo_read(accel_raw_sp, accel_g_sp, gyro_raw_sp, gyro_dps_sp, &len_sample) != 0U)
        {
            ret = SENSOR_ERROR;
        }
        else
        {
            ret = SENSOR_OK;
        }

    }
    else
    {
        printf("mpu6500_fifo_init Fail\n!!");
    }

    sensorUnLock();

    return ret;
}

static int32_t Accelerometer_Disable(void)
{
    int32_t ret = SENSOR_ERROR;

    sensorLock();

    if (mpu6500_fifo_deinit() == 0)
    {
        ret = SENSOR_OK;
    }

    sensorUnLock();
    sensorLockDelete();

    return ret;
}

static uint32_t Accelerometer_GetOverflow(void)
{

    uint8_t ret_int = 0;

    ret_int = mpu6500_fifo_overflow();

    if (ret_int != 0)
    {
        printf("irq handler fail: %u\n", ret_int);
    }

    return ret_int;
}

static uint32_t Accelerometer_ReadSamples(uint32_t num_samples, void *buf)
{
    uint16_t num;
    num = num_samples;

    sensorLock();

    mpu6500_fifo_read(accel_raw_sp, buf, gyro_raw_sp, gyro_dps_sp, &num);
    sensorUnLock();

    return (uint32_t)num;
}

sensorDrvHW_t sensorDrvHW_3 =
{
    NULL,
    Accelerometer_Enable,
    Accelerometer_Disable,
    Accelerometer_GetOverflow,
    Accelerometer_ReadSamples,
    NULL,
    NULL
};


// Gyroscope

static int32_t Gyroscope_Enable(void)
{
    int32_t ret = SENSOR_ERROR;
    len_sample = 85;

    sensorLockCreate();
    sensorLock();

    if (mpu6500_fifo_init(interface, addr) == 0)
    {
        // Clear MPU6500 FIFO
        mpu6500_interface_delay_ms(10);

        if (mpu6500_fifo_read(accel_raw_sp, accel_g_sp, gyro_raw_sp, gyro_dps_sp, &len_sample) != 0U)
        {
            ret = SENSOR_ERROR;
        }
        else
        {
            ret = SENSOR_OK;
        }
    }
    else
    {
        printf("mpu6500_fifo_init Fail\n!!");
    }

    sensorUnLock();

    return ret;
}

static int32_t Gyroscope_Disable(void)
{
    int32_t ret = SENSOR_ERROR;

    sensorLock();

    if (mpu6500_fifo_deinit() == 0)
    {
        ret = SENSOR_OK;
    }

    sensorUnLock();
    sensorLockDelete();

    return ret;
}

static uint32_t Gyroscope_GetOverflow(void)
{
    uint8_t ret_int = 0;

    ret_int = mpu6500_fifo_overflow();

    if (ret_int != 0)
    {
        printf("irq handler fail: %u\n", ret_int);
    }

    return ret_int;
}

static uint32_t Gyroscope_ReadSamples(uint32_t num_samples, void *buf)
{
    uint16_t num;
    num = num_samples;

    sensorLock();

    mpu6500_fifo_read(accel_raw_sp, accel_g_sp, gyro_raw_sp, buf, &num);
    sensorUnLock();

    return (uint32_t)num;
}

sensorDrvHW_t sensorDrvHW_4 =
{
    NULL,
    Gyroscope_Enable,
    Gyroscope_Disable,
    Gyroscope_GetOverflow,
    Gyroscope_ReadSamples,
    NULL,
    NULL
};

// Accelerometer+Gyroscope

//sensorDrvHW_t sensorDrvHW_6 = {
//  NULL,
//  AcceGyro_Enable,
//  AcceGyro_Disable,
//  AcceGyro_GetOverflow,
//  NULL,
//  AcceGyro_ReadSamples,
//  NULL
//};
