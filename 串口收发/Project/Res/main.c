#include "Bsp.h"
#include "stm32f4xx.h"    // 相当于51单片机中的  #include <reg51.h>

int main( )
{
    // 若没有配置RCC时钟, 则自动被配置为72MHz.
    System_Init( );

    while ( 1 ) {}
}
