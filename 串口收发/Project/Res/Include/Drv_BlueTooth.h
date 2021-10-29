#include "stm32f4xx.h"

typedef struct
{
    u8 flag;
    u8 Cmd;
} bt_cmd_t;

extern bt_cmd_t BlueTooth_Cmd;

void Send_Bt_Info( void );
void BlueTooth_GetOneByte( u8 bytedata );
