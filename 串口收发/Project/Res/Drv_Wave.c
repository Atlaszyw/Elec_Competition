#include "Drv_Wave.h"
#include "usart.h"

u8 Uts_Buf[3];

u8 Uts_Info[6] = { 0xAA, 0x20, 0x00, 0x00, 0x00, 0xFF };

ultrasound_distance_t Uts_Dst;


static void Ultrasound_Data_Analysis( )
{
    Uts_Dst.flag = 1;
    Uts_Dst.dst  = (u16)( Uts_Buf[0] << 8 | Uts_Buf[1] ) / 10;
}


void Send_Uts_Info( )
{
    // 判断发送标志位
    if ( Uts_Dst.flag != 0 )
    {
        Uts_Dst.flag = 0;
        // 判定信号的有效性
        if ( Uts_Dst.dst > 120 )
            Uts_Info[2] = 0x00;
        else
            Uts_Info[2] = 0x01;

        // 数据提取
        Uts_Info[3] = (u8)( Uts_Dst.dst >> 8 );
        Uts_Info[4] = (u8)( Uts_Dst.dst & 0xFF );

        DrvUart1SendBuf( Uts_Info, 6 );
    }
}

void Ultrasound_GetOneByte( u8 bytedata )
{
    static u8 rec_sta = 0;

    Uts_Buf[rec_sta] = bytedata;

    if ( rec_sta == 0 )
        rec_sta++;
    else if ( rec_sta == 1 )
    {
        Ultrasound_Data_Analysis( );
        rec_sta = 0;
    }
}
