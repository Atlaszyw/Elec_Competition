#include "stm32f4xx.h"

#include "Bsp.h"
#include "Drv_BlueTooth.h"
#include "Drv_Wave.h"
#include "timer.h"
#include "usart.h"

void System_Init( )
{
    NVIC_SetPriorityGrouping( NVIC_GROUP );

    Sys_Timer_Init( );

    // #: General
    DrvUart1Init( 921600 );
    // #: BlueTooth
    DrvUart2Init( 9600 );
    // #: UtrSound
    DrvUart3Init( 9600 );
}
