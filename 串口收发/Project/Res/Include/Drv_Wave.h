#include "stm32f4xx.h"

typedef struct
{
    u8  flag;
    u8  warning;
    u16 dst;
} ultrasound_distance_t;

extern ultrasound_distance_t Uts_Dst;

void Send_Uts_Info( void );
void Ultrasound_GetOneByte( u8 bytedata );
