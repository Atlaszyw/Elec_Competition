#include "Drv_BlueTooth.h"
#include "usart.h"

u8 BlueTooth_Buf[6];

// #: 距离信号接收格式: 0xAA 0x20 cmd 0xFF
u8       Bt_Info[4] = { 0xAA, 0x10, 0x00, 0xFF };
bt_cmd_t BlueTooth_Cmd;

static void BlueTooth_Data_Analysis( )
{
    if ( BlueTooth_Buf[1] == 0x10 )
    {
        BlueTooth_Cmd.Cmd  = BlueTooth_Buf[2];
        BlueTooth_Cmd.flag = 1;
    }
}

void Send_Bt_Info( )
{
    // 判断发送标志位
    if ( BlueTooth_Cmd.flag != 0 )
    {
        BlueTooth_Cmd.flag = 0;
        // 数据提取
        Bt_Info[2] = BlueTooth_Cmd.Cmd;
        DrvUart1SendBuf( Bt_Info, 4 );
    }
}

void BlueTooth_GetOneByte( u8 bytedata )
{
    static u8 rec_sta = 0;

    BlueTooth_Buf[rec_sta] = bytedata;

    if ( rec_sta == 0 )
    {
        if ( bytedata == 0xAA )
            rec_sta++;
        else
            rec_sta = 0;
    }
    else if ( rec_sta == 1 && bytedata == 0x10 )
    {
        rec_sta++;
    }
    else if ( rec_sta == 2 )
    {
        rec_sta++;
    }
    else if ( rec_sta == 3 )
    {
        if ( bytedata != 0xFF )
        {
            rec_sta = 0;
        }
        else
        {
            BlueTooth_Data_Analysis( );
            rec_sta = 0;
        }
    }
}
