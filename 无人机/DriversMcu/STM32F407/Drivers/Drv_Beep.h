#ifndef _BEEP_H_
#define _BEEP_H_

#include "SysConfig.h"

/***************LED GPIO定义******************/
#define RCC_BEEP  RCC_AHB1Periph_GPIOC
#define GPIO_BEEP GPIOC
#define Pin_BEEP  GPIO_Pin_6
/*********************************************/
#define Beep_On     GPIO_BEEP->BSRRL = Pin_BEEP
#define Beep_Off    GPIO_BEEP->BSRRH = Pin_BEEP
#define Beep_TOGGLE GPIO_BEEP->ODR ^= Pin_BEEP

void Beep_Init( void );

#endif
