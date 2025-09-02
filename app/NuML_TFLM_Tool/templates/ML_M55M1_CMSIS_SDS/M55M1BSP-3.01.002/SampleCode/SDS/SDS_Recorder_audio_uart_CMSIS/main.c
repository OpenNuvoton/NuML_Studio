/*----------------------------------------------------------------------------
 * Name:    main.c
 *----------------------------------------------------------------------------*/

/* Includes ------------------------------------------------------------------*/
#include "NuMicro.h"
#include "USART_PinConfig.h"            // PinConfig for USART driver

#include "sds_app_config.h"

#include <math.h>

uint8_t button_start = 0;

// Read sensor thread
static __NO_RETURN void read_audio(void *argument)
{
    uint32_t num, buf_size;
    uint32_t timestamp;
    (void)   argument;

    timestamp = osKernelGetTickCount();

    for (;;)
    {
        if (close_flag == 0U)
        {
            //if (sensorGetStatus(sensorId_accelerometer).active != 0U)
            if (DMICRecord_AvailSamples() > SENSOR_AUDIO_SIZE)
            {
                DMICRecord_ReadSamples(audioBuf, SENSOR_AUDIO_SIZE);
                DMICRecord_UpdateReadSampleIndex(SENSOR_AUDIO_SIZE);

                buf_size = SENSOR_AUDIO_SIZE * sizeof(audioBuf[0]);
                //printf("audioBuf[8183]: %d, audioBuf[8185]: %d, audioBuf[8189]: %d\r\n", audioBuf[8183], audioBuf[8185], audioBuf[8189]);
                num = sdsRecWrite(recId_audio, timestamp, audioBuf, buf_size);
                //printf("sdsRecWrite Done: num: %u, buf_size: %u, timestamp: %u\r\n", num, buf_size, timestamp);

                if (num != buf_size)
                {
                    printf("Recorder write failed\r\n");
                }
            }

        }
        else
        {
            if (event_close_sent == 0U)
            {
                event_close_sent = 1U;
                osThreadFlagsSet(thrId_demo, EVENT_CLOSE);
            }
        }

        timestamp += SENSOR_POLLING_INTERVAL;
        osDelayUntil(timestamp);
    }
}

// Recorder event callback
static void recorder_event_callback(sdsRecId_t id, uint32_t event)
{
    if (event & SDS_REC_EVENT_IO_ERROR)
    {
        if (id == recId_audio)
        {
            printf("Recorder event - I/O error\r\n");
        }
    }
}

// Recorder start
static void recorder_start(void)
{
    // Open Recorder
    recId_audio = sdsRecOpen("DMicrophone", recBuf_audio, sizeof(recBuf_audio), SDS_REC_IO_THRESHOLD_AUDIO);
    DMICRecord_StartRec();
    printf("Audio Start\r\n");

}

// Recorder stop
static void recorder_stop(void)
{
    uint32_t flags;

    event_close_sent = 0U;
    close_flag = 1U;
    flags = osThreadFlagsWait(EVENT_CLOSE, osFlagsWaitAny, osWaitForever);

    if ((flags & osFlagsError) == 0U)
    {
        DMICRecord_StopRec();
        // Close Recorder
        sdsRecClose(recId_audio);
        recId_audio = NULL;
        printf("Audio sdsRecClose\r\n");

    }

    close_flag = 0U;
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

void SetSdsIOUartCLK(void)
{
#if (!defined(DEBUG_ENABLE_SEMIHOST) || (DEBUG_ENABLE_SEMIHOST == 1)) && !defined(OS_USE_SEMIHOSTING)
#if (RTE_USART0)
    /* Select UART0 clock source from HIRC */
	  CLK_SetModuleClock(UART0_MODULE, CLK_UARTSEL0_UART0SEL_HIRC, CLK_UARTDIV0_UART0DIV(1));
	  /* Enable module peripheral clock */
    CLK_EnableModuleClock(UART0_MODULE);
	
	  //SYS_ResetModule(SYS_UART0RST);
#endif
#if (RTE_USART6)
    /* Select UART0 clock source from HIRC */
	  CLK_SetModuleClock(UART6_MODULE, CLK_UARTSEL0_UART6SEL_HIRC, CLK_UARTDIV0_UART6DIV(1));
	  /* Enable module peripheral clock */
    CLK_EnableModuleClock(UART6_MODULE);
	
	  //SYS_ResetModule(SYS_UART6RST);
#endif
#endif
}

__WEAK void SetSdsIOUartMFP(void)
{
#if (RTE_USART0)
		RTE_SET_USART0_TX_PIN();
    RTE_SET_USART0_RX_PIN();
#endif
#if (RTE_USART6)		
		RTE_SET_USART6_TX_PIN();
    RTE_SET_USART6_RX_PIN();
    //RTE_SET_USART6_CTS_PIN();
    //RTE_SET_USART6_RTS_PIN();
#endif

}

static void SYS_Init(void)
{
    /* Unlock protected registers */
    SYS_UnlockReg();

    /*---------------------------------------------------------------------------------------------------------*/
    /* Init System Clock                                                                                       */
    /*---------------------------------------------------------------------------------------------------------*/
    /* Enable PLL1 192MHZ clock from HIRC for DMIC clock source to PLL1_DIV2 */
    CLK_EnableAPLL(CLK_APLLCTL_APLLSRC_HIRC, FREQ_192MHZ, CLK_APLL1_SELECT);
    /* Enable PLL0 220MHz clock from HIRC and switch SCLK clock source to PLL0 */
    CLK_SetBusClock(CLK_SCLKSEL_SCLKSEL_APLL0, CLK_APLLCTL_APLLSRC_HIRC, FREQ_220MHZ);

    /* Update System Core Clock */
    /* User can use SystemCoreClockUpdate() to calculate SystemCoreClock. */
    SystemCoreClockUpdate();

    /* Enable UART module clock */
    SetDebugUartCLK();

    // DMIC_APLL1_FREQ_196608KHZ for DMIC 8000/16000/48000 Hz sample-rate with 64/128/256 down-sample
    CLK_EnableAPLL(CLK_APLLCTL_APLLSRC_HIRC, DMIC_APLL1_FREQ_196608KHZ, CLK_APLL1_SELECT);
    // Select DMIC CLK source from APLL1_DIV2.
    CLK_SetModuleClock(DMIC0_MODULE, CLK_DMICSEL_DMIC0SEL_APLL1_DIV2, MODULE_NoMsk);
    // Enable DMIC clock.
    CLK_EnableModuleClock(DMIC0_MODULE);
    // DPWM IPReset.
    SYS_ResetModule(SYS_DMIC0RST);

    // LPPDMA Initial.
    CLK_EnableModuleClock(LPPDMA0_MODULE);
    //CLK_EnableModuleClock(LPSRAM0_MODULE);
    SYS_ResetModule(SYS_LPPDMA0RST);

    /*---------------------------------------------------------------------------------------------------------*/
    /* Init I/O Multi-function                                                                                 */
    /*---------------------------------------------------------------------------------------------------------*/

    /* BTN_1 */
    /* Enable GPIO Port B clock */
    CLK_EnableModuleClock(GPIOH_MODULE);
    /* Enable Internal low speed RC clock */
    CLK_EnableXtalRC(CLK_SRCCTL_LIRCEN_Msk);
    /* Waiting for Internal low speed RC clock ready */
    CLK_WaitClockReady(CLK_STATUS_LIRCSTB_Msk);


    SetDebugUartMFP();
		
		/*CMSIS USART driver */
		SetSdsIOUartCLK();
		SetSdsIOUartMFP();

    /* Set multi-function pins for DMIC */
    SET_DMIC0_CLK_PB4();
    SET_DMIC0_DAT_PB5();

    /* Lock protected registers */
    SYS_LockReg();
}

// Sensor Demo
static __NO_RETURN void demo(void *argument)
{

    uint32_t  value;
    uint32_t  value_last = 0U;
    uint8_t   rec_active = 0U;

    (void) argument;

    /* Configure PH.1 as Input mode and enable interrupt by falling edge trigger */
    /* BTN1 */
    GPIO_SetMode(PH, BIT1, GPIO_MODE_INPUT);
    GPIO_EnableInt(PH, 1, GPIO_INT_FALLING);
    /* Enable interrupt de-bounce function and select de-bounce sampling cycle time is 1024 clocks of LIRC clock */
    GPIO_SET_DEBOUNCE_TIME(PH, GPIO_DBCTL_DBCLKSRC_LIRC, GPIO_DBCTL_DBCLKSEL_1024);
    GPIO_ENABLE_DEBOUNCE(PH, BIT1);
    NVIC_EnableIRQ(GPH_IRQn);

    thrId_demo = osThreadGetId();

    // Initialize recorder
    printf("SDS: sdsORec init\n");
    int ret = 0;
    ret = sdsRecInit(recorder_event_callback);

    if (ret)
    {
        printf("SDS: sdsORec init fail!\n");
    }

    // Create sensor thread
    printf("osThreadNew\n");
    osThreadNew(read_audio, NULL, NULL);

    for (;;)
    {
        // Monitor user button, Button pressed
        if (button_start == 1)
        {
            button_start = 0; //clear button
            NVIC_DisableIRQ(GPH_IRQn);


            if (rec_active == 0U)
            {
                rec_active = 1U;
                recorder_start();
            }
            else
            {
                rec_active = 0U;
                recorder_stop();
            }

            NVIC_EnableIRQ(GPH_IRQn);
        }

        osDelay(100U);
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

    // initial audio DMIC
    int32_t ret;
    ret = DMICRecord_Init(AUDIO_SAMPLE_RATE, AUDIO_CHANNEL, SENSOR_AUDIO_SIZE, AUDIO_SAMPLE_BLOCK);

    if (ret)
    {
        printf("Unable init DMIC record error(%d)\n", ret);
    }


    osKernelInitialize();                // Initialize CMSIS-RTOS2

    osThreadNew(demo, NULL, NULL);       // Create validation main thread

    osKernelStart();                     // Start thread execution

    for (;;) {}

}
