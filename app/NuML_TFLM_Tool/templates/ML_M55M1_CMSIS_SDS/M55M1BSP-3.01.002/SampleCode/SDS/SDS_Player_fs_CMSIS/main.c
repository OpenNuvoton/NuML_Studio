/*----------------------------------------------------------------------------
 * Name:    main.c
 *----------------------------------------------------------------------------*/

/* Includes ------------------------------------------------------------------*/
#include "NuMicro.h"

/* os */
#include "cmsis_os2.h"
/* sds */
#include "sds_app_config.h"

#include <math.h>
#include "USBH_MSC.h"

uint8_t button_start = 0;

/* Private functions ---------------------------------------------------------*/

#define USE_USB_APLL1_CLOCK         1

// Player event callback
static void player_event_callback(sdsPlayId_t id, uint32_t event)
{
    if (event & SDS_PLAY_EVENT_IO_ERROR)
    {
        if (id == playId_accelerometer)
        {
            printf("Player event - I/O error\r\n");
        }
    }
}

NVT_ITCM void GPH_IRQHandler(void)
{
    volatile uint32_t temp;

    /* To check if PH.1 interrupt occurred */
    if (GPIO_GET_INT_FLAG(PH, BIT1))
    {
        GPIO_CLR_INT_FLAG(PH, BIT1);
        button_start = 1;
    }
    else
    {
        /* Un-expected interrupt. Just clear all PB interrupts */
        temp = PH->INTSRC;
        PH->INTSRC = temp;
        printf("PH_1 Un-expected interrupts.\n");
    }
}

static void SYS_Init(void)
{
    /* Unlock protected registers */
    SYS_UnlockReg();

    /* Enable clock */
    CLK_EnableXtalRC(CLK_SRCCTL_HXTEN_Msk);
    CLK_EnableXtalRC(CLK_SRCCTL_HIRCEN_Msk);
    CLK_EnableXtalRC(CLK_SRCCTL_HIRC48MEN_Msk);

    /* Wait for clock ready */
    CLK_WaitClockReady(CLK_STATUS_HXTSTB_Msk);
    CLK_WaitClockReady(CLK_STATUS_HIRCSTB_Msk);
    CLK_WaitClockReady(CLK_STATUS_HIRC48MSTB_Msk);

    /*---------------------------------------------------------------------------------------------------------*/
    /* Init System Clock                                                                                       */
    /*---------------------------------------------------------------------------------------------------------*/
    /* Enable PLL0 220MHz clock from HIRC and switch SCLK clock source to PLL0 */
    CLK_SetBusClock(CLK_SCLKSEL_SCLKSEL_APLL0, CLK_APLLCTL_APLLSRC_HIRC, FREQ_220MHZ);

#if (USE_USB_APLL1_CLOCK)
    /* Enable APLL1 96MHz clock */
    CLK_EnableAPLL(CLK_APLLCTL_APLLSRC_HXT, 96000000, CLK_APLL1_SELECT);
#endif

    /* Enable GPIOA module clock */
    CLK_EnableModuleClock(GPIOA_MODULE);
    CLK_EnableModuleClock(GPIOB_MODULE);
    CLK_EnableModuleClock(GPIOC_MODULE);
    CLK_EnableModuleClock(GPIOD_MODULE);
    CLK_EnableModuleClock(GPIOE_MODULE);
    CLK_EnableModuleClock(GPIOF_MODULE);
    CLK_EnableModuleClock(GPIOG_MODULE);
    CLK_EnableModuleClock(GPIOH_MODULE);
    CLK_EnableModuleClock(GPIOI_MODULE);
    CLK_EnableModuleClock(GPIOJ_MODULE);

    /* Enable HSOTG module clock */
    CLK_EnableModuleClock(HSOTG0_MODULE);
    /* Select HSOTG PHY Reference clock frequency which is from HXT*/
    HSOTG_SET_PHY_REF_CLK(HSOTG_PHYCTL_FSEL_24_0M);

#if (USE_USB_APLL1_CLOCK)
    /* USB Host desired input clock is 48 MHz. Set as APLL1 divided by 2 (96/2 = 48) */
    CLK_SetModuleClock(USBH0_MODULE, CLK_USBSEL_USBSEL_APLL1_DIV2, CLK_USBDIV_USBDIV(1));
#else
    /* USB Host desired input clock is 48 MHz. Set as HIRC48M divided by 1 (48/1 = 48) */
    CLK_SetModuleClock(USBH0_MODULE, CLK_USBSEL_USBSEL_HIRC48M, CLK_USBDIV_USBDIV(1));
#endif
    /* Enable USBH module clock */
    CLK_EnableModuleClock(USBH0_MODULE);
    CLK_EnableModuleClock(USBD0_MODULE);
    CLK_EnableModuleClock(OTG0_MODULE);
    /* Enable HSUSBH module clock */
    CLK_EnableModuleClock(HSUSBH0_MODULE);

    /* Set OTG as USB Host role */
    SYS->USBPHY = (0x1ul << (SYS_USBPHY_HSOTGPHYEN_Pos)) | (0x1ul << (SYS_USBPHY_HSUSBROLE_Pos)) | (0x1ul << (SYS_USBPHY_OTGPHYEN_Pos)) | (0x1 << SYS_USBPHY_USBROLE_Pos);
    osDelay(20);
    SYS->USBPHY |= SYS_USBPHY_HSUSBACT_Msk;

    /* Update System Core Clock */
    /* User can use SystemCoreClockUpdate() to calculate SystemCoreClock. */
    SystemCoreClockUpdate();

    /* Enable UART module clock */
    SetDebugUartCLK();

    /*---------------------------------------------------------------------------------------------------------*/
    /* Init I/O Multi-function                                                                                 */
    /*---------------------------------------------------------------------------------------------------------*/
    SetDebugUartMFP();

    /* USB_VBUS_EN (USB 1.1 VBUS power enable pin) multi-function pin - PB.15     */
    SET_USB_VBUS_EN_PB15();

    /* USB_VBUS_ST (USB 1.1 over-current detect pin) multi-function pin - PB.14   */
    SET_USB_VBUS_ST_PB14();

    /* HSUSB_VBUS_EN (USB 2.0 VBUS power enable pin) multi-function pin - PJ.13   */
    SET_HSUSB_VBUS_EN_PJ13();

    /* HSUSB_VBUS_ST (USB 2.0 over-current detect pin) multi-function pin - PJ.12 */
    SET_HSUSB_VBUS_ST_PJ12();

    /* USB 1.1 port multi-function pin VBUS, D+, D-, and ID pins */
    SET_USB_VBUS_PA12();
    SET_USB_D_MINUS_PA13();
    SET_USB_D_PLUS_PA14();
    SET_USB_OTG_ID_PA15();

    /* BTN_1 */
    /* Enable GPIO Port B clock */
    CLK_EnableModuleClock(GPIOH_MODULE);
    /* Enable Internal low speed RC clock */
    CLK_EnableXtalRC(CLK_SRCCTL_LIRCEN_Msk);
    /* Waiting for Internal low speed RC clock ready */
    CLK_WaitClockReady(CLK_STATUS_LIRCSTB_Msk);

    /* Lock protected registers */
    SYS_LockReg();
}

int USBH_MSC_INIT_SETUP()
{
    uint8_t ret = 0;
    usbStatus usb_status;                 // USB status
    int32_t   msc_status;                 // MSC status

    usb_status = USBH_Initialize(0U);     // Initialize USB Host 0

    if (usb_status != usbOK)
    {
        printf("USBH_Initialize error, usb_status: %d\n", usb_status);
        return 0;
    }

    for (;;)
    {
        msc_status = USBH_MSC_DriveGetMediaStatus("U0:");   // Get MSC device status

        if (msc_status == USBH_MSC_OK)
        {
            return 1;
        }
    }


}


//USB MSC Thread
/*-----------------------------------------------------------------------------
 * Application main thread
 *----------------------------------------------------------------------------*/
char rbuf[100];
__NO_RETURN void app_main_thread(void *argument)
{

    uint32_t  timestamp, tick;
    uint32_t  n, size;
    float *pbuf;
    double    abs;
    double    abs_max;
    (void)argument;


    // Initialize USBH
	  printf("Init USBH ...\r\n");
    uint8_t usbh_msc_ret = 0;
    usbh_msc_ret = USBH_MSC_INIT_SETUP();

    if (!usbh_msc_ret)
    {
        printf("USBH_MSC_INIT_SETUP Fail.\r\n");

        while (1);
    }

    // Initialize player
    sdsPlayInit(player_event_callback);
    printf("Init SDS Player\r\n");

    for (;;)
    {
        // Open SDS Player
        playId_accelerometer = sdsPlayOpen("Accelerometer",
                                           playBuf_accelerometer,
                                           sizeof(playBuf_accelerometer),
                                           PLAY_IO_THRESHOLD_ACCELEROMETER);

        tick = osKernelGetTickCount();

        if (playId_accelerometer == NULL)
        {
            printf("End of example\r\n");

            while (1);
        }
        else
        {
            printf("SDSPlay Open, PlayId: %d\r\n", (int) playId_accelerometer);
        }

        for (;;)
        {
            do
            {
                size = sdsPlayGetSize(playId_accelerometer);

                //printf("Size: %d\n", size);
                if (size > sizeof(tempBuf))
                {
                    // Fatal error: Should not happen
                    printf("Error: Record size is bigger than buffer size\r\n");

                    while (1);
                }

                if (size == 0U)
                {
                    if (sdsPlayEndOfStream(playId_accelerometer) != 0)
                    {
                        sdsPlayClose(playId_accelerometer);
                        break;
                    }
                }
            } while (size == 0U);

            if (size == 0U)
            {
                // End of stream
                break;
            }

            sdsPlayRead(playId_accelerometer, &timestamp, tempBuf, size);

            osDelayUntil(tick + timestamp);

            abs_max = 0.0;
            pbuf = (float *)tempBuf;
            printf("timestamp: %d size: %d, pbuf[0]: %f, pbuf[1]: %f, pbuf[2]: %f \n", timestamp, size, pbuf[0], pbuf[1], pbuf[2]);
            printf("Last: pbuf[0]: %f, pbuf[1]: %f, pbuf[2]: %f \n", pbuf[3 * (size / 12 - 1) + 0], pbuf[3 * (size / 12 - 1) + 1], pbuf[3 * (size / 12 - 1) + 2]);

            for (n = size / SENSOR_ACCELEROMETER_NUM_PER_SAMPLE; n != 0U; n--)
            {
                //abs = sqrt((pbuf[0] * pbuf[0]) + (pbuf[1] * pbuf[1]) + (pbuf[2] * pbuf[2]));
                //pbuf += 3;
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

    osThreadNew(app_main_thread, NULL, NULL);   // Create validation main thread

    osKernelStart();                     // Start thread execution

    for (;;) {}
}
