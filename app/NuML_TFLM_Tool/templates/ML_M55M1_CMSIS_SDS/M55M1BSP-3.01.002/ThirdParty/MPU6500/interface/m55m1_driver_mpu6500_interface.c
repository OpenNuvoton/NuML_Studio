/**
 * Copyright (c) 2015 - present LibDriver All rights reserved
 *
 * The MIT License (MIT)
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 * @file      driver_mpu6500_interface_template.c
 * @brief     driver mpu6500 interface template source file
 * @version   1.0.0
 * @author    Nuvoton Chen Chih Yen
 * @date      2025-02-25
 *
 * <h3>history</h3>
 * <table>
 * <tr><th>Date        <th>Version  <th>Author      <th>Description
 * <tr><td>2024/07/30  <td>1.0      <td>Shifeng Li  <td>first upload
 * </table>
 */

#include "cmsis_os2.h"
#include "driver_mpu6500_interface.h"
#include <stdarg.h>

#define IMU_I2C  LPI2C0
#define MPU6500_DEVICE_ID  0x68

/**
 * @brief  interface iic bus init
 * @return status code
 *         - 0 success
 *         - 1 iic init failed
 * @note   none
 */
uint8_t mpu6500_interface_iic_init(void)
{
    /* Open LPI2C0 module and set bus clock */
    LPI2C_Open(IMU_I2C, 100000);

    return 0;
}

/**
 * @brief  interface iic bus deinit
 * @return status code
 *         - 0 success
 *         - 1 iic deinit failed
 * @note   none
 */
uint8_t mpu6500_interface_iic_deinit(void)
{
    LPI2C_Close(IMU_I2C);

    return 0;
}

/**
 * @brief      interface iic bus read
 * @param[in]  addr iic device write address
 * @param[in]  reg iic register address
 * @param[out] *buf pointer to a data buffer
 * @param[in]  len length of the data buffer
 * @return     status code
 *             - 0 success
 *             - 1 read failed
 * @note       none
 */
uint8_t mpu6500_interface_iic_read(uint8_t addr, uint8_t reg, uint8_t *buf, uint16_t len)
{
    uint8_t res = 1;
    uint32_t bytes_len_received;

    __disable_irq();

    if (len == 1)
    {
        *buf = LPI2C_ReadByteOneReg(IMU_I2C, MPU6500_DEVICE_ID, reg);
    }
    else
    {
        bytes_len_received = LPI2C_ReadMultiBytesOneReg(IMU_I2C, MPU6500_DEVICE_ID, reg, buf, (uint32_t)len);
    }

    res = 0;

    __enable_irq();

    return res;

}

/**
 * @brief     interface iic bus write
 * @param[in] addr iic device write address
 * @param[in] reg iic register address
 * @param[in] *buf pointer to a data buffer
 * @param[in] len length of the data buffer
 * @return    status code
 *            - 0 success
 *            - 1 write failed
 * @note      none
 */
uint8_t mpu6500_interface_iic_write(uint8_t addr, uint8_t reg, uint8_t *buf, uint16_t len)
{
    uint8_t res = 1;
    uint32_t bytes_len_transmitted;

    __disable_irq();

    if (len == 1)
    {
        LPI2C_WriteByteOneReg(IMU_I2C, MPU6500_DEVICE_ID, reg, *buf);
    }
    else
    {
        bytes_len_transmitted = LPI2C_WriteMultiBytesOneReg(IMU_I2C, MPU6500_DEVICE_ID, reg, buf, (uint32_t)len);
    }

    res = 0;

    __enable_irq();

    return res;
}

/**
 * @brief  interface spi bus init
 * @return status code
 *         - 0 success
 *         - 1 spi init failed
 * @note   none
 */
uint8_t mpu6500_interface_spi_init(void)
{
    return 0;
}

/**
 * @brief  interface spi bus deinit
 * @return status code
 *         - 0 success
 *         - 1 spi deinit failed
 * @note   none
 */
uint8_t mpu6500_interface_spi_deinit(void)
{
    return 0;
}

/**
 * @brief      interface spi bus read
 * @param[in]  reg register address
 * @param[out] *buf pointer to a data buffer
 * @param[in]  len length of data buffer
 * @return     status code
 *             - 0 success
 *             - 1 read failed
 * @note       none
 */
uint8_t mpu6500_interface_spi_read(uint8_t reg, uint8_t *buf, uint16_t len)
{
    return 0;
}

/**
 * @brief     interface spi bus write
 * @param[in] reg register address
 * @param[in] *buf pointer to a data buffer
 * @param[in] len length of data buffer
 * @return    status code
 *            - 0 success
 *            - 1 write failed
 * @note      none
 */
uint8_t mpu6500_interface_spi_write(uint8_t reg, uint8_t *buf, uint16_t len)
{
    return 0;
}

/**
 * @brief     interface delay ms
 * @param[in] ms time
 * @note      none
 */
void mpu6500_interface_delay_ms(uint32_t ms)
{
#if   defined(CMSIS_OS2_H_)
    osDelay(ms);
#else
    //Max: 200MHz => 83886us, 180MHz => 93206us
    uint32_t count;

    for (count = 0; count < ms; count++)
        CLK_SysTickDelay(1000); // 1 ms = 1000 us

#endif
}

/**
 * @brief     interface print format data
 * @param[in] fmt format data
 * @note      none
 */
void mpu6500_interface_debug_print(const char *const fmt, ...)
{
    char str[256];
    va_list args;

    memset((char *)str, 0, sizeof(char) * 256);
    va_start(args, fmt);
    vsnprintf((char *)str, 255, (char const *)fmt, args);
    va_end(args);

    printf("%s", str);

}

/**
 * @brief     interface receive callback
 * @param[in] type irq type
 * @note      none
 */
void mpu6500_interface_receive_callback(uint8_t type)
{
    switch (type)
    {
        case MPU6500_INTERRUPT_MOTION :
        {
            mpu6500_interface_debug_print("mpu6500: irq motion.\n");

            break;
        }

        case MPU6500_INTERRUPT_FIFO_OVERFLOW :
        {
            mpu6500_interface_debug_print("mpu6500: irq fifo overflow.\n");

            break;
        }

        case MPU6500_INTERRUPT_FSYNC_INT :
        {
            mpu6500_interface_debug_print("mpu6500: irq fsync int.\n");

            break;
        }

        case MPU6500_INTERRUPT_DMP :
        {
            mpu6500_interface_debug_print("mpu6500: irq dmp\n");

            break;
        }

        case MPU6500_INTERRUPT_DATA_READY :
        {
            mpu6500_interface_debug_print("mpu6500: irq data ready\n");

            break;
        }

        default :
        {
            mpu6500_interface_debug_print("mpu6500: irq unknown code.\n");

            break;
        }
    }
}

/**
 * @brief     interface dmp tap callback
 * @param[in] count tap count
 * @param[in] direction tap direction
 * @note      none
 */
void mpu6500_interface_dmp_tap_callback(uint8_t count, uint8_t direction)
{
    switch (direction)
    {
        case MPU6500_DMP_TAP_X_UP :
        {
            mpu6500_interface_debug_print("mpu6500: tap irq x up with %d.\n", count);

            break;
        }

        case MPU6500_DMP_TAP_X_DOWN :
        {
            mpu6500_interface_debug_print("mpu6500: tap irq x down with %d.\n", count);

            break;
        }

        case MPU6500_DMP_TAP_Y_UP :
        {
            mpu6500_interface_debug_print("mpu6500: tap irq y up with %d.\n", count);

            break;
        }

        case MPU6500_DMP_TAP_Y_DOWN :
        {
            mpu6500_interface_debug_print("mpu6500: tap irq y down with %d.\n", count);

            break;
        }

        case MPU6500_DMP_TAP_Z_UP :
        {
            mpu6500_interface_debug_print("mpu6500: tap irq z up with %d.\n", count);

            break;
        }

        case MPU6500_DMP_TAP_Z_DOWN :
        {
            mpu6500_interface_debug_print("mpu6500: tap irq z down with %d.\n", count);

            break;
        }

        default :
        {
            mpu6500_interface_debug_print("mpu6500: tap irq unknown code.\n");

            break;
        }
    }
}

/**
 * @brief     interface dmp orient callback
 * @param[in] orientation dmp orientation
 * @note      none
 */
void mpu6500_interface_dmp_orient_callback(uint8_t orientation)
{
    switch (orientation)
    {
        case MPU6500_DMP_ORIENT_PORTRAIT :
        {
            mpu6500_interface_debug_print("mpu6500: orient irq portrait.\n");

            break;
        }

        case MPU6500_DMP_ORIENT_LANDSCAPE :
        {
            mpu6500_interface_debug_print("mpu6500: orient irq landscape.\n");

            break;
        }

        case MPU6500_DMP_ORIENT_REVERSE_PORTRAIT :
        {
            mpu6500_interface_debug_print("mpu6500: orient irq reverse portrait.\n");

            break;
        }

        case MPU6500_DMP_ORIENT_REVERSE_LANDSCAPE :
        {
            mpu6500_interface_debug_print("mpu6500: orient irq reverse landscape.\n");

            break;
        }

        default :
        {
            mpu6500_interface_debug_print("mpu6500: orient irq unknown code.\n");

            break;
        }
    }
}