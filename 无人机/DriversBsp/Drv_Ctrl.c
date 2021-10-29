#include "Drv_Ctrl.h"
#include "Ano_Kalman.h"

u8 Ctrl_Buf[6];
// #: 控制信号接收格式: 0xAA 0x28 num 0xFF
// #: 距离信号接收格式: 0xAA 0x20 flag distance 0xFF

Ctrl_Sgn_t      Ctrl_Signal;
Ctrl_Distance_t Ctrl_Dst;

static void Ctrl_Data_Analysis( )
{
    if ( Ctrl_Buf[1] == 0x28 )
    {
        Ctrl_Signal.task_num = Ctrl_Buf[2];
    }
    else if ( Ctrl_Buf[1] == 0x20 )
    {
        Ctrl_Dst.flag         = Ctrl_Buf[2];
        Ctrl_Dst.distance     = (u16)( Ctrl_Buf[3] << 8 | Ctrl_Buf[4] );
        Ctrl_Dst.kal_distance = kalmanFilter( &KFP_Distance, Ctrl_Dst.distance );
    }
}

void Ctrl_GetOneByte( u8 bytedata )
{
    static u8 rec_sta = 0;
    static u8 objtype = 0;

    Ctrl_Buf[rec_sta] = bytedata;

    if ( rec_sta == 0 )
    {
        if ( bytedata == 0xAA )
            rec_sta++;
        else
            rec_sta = 0;
    }
    else if ( rec_sta == 1 )
    {
        if ( bytedata == 0x20 )
        {
            rec_sta++;
            objtype = 2;
            return;
        }
        if ( bytedata == 0x28 )
        {
            rec_sta++;
            objtype = 1;
            return;
        }
    }
    else if ( rec_sta >= 2 )
    {
        if ( objtype == 1 )
        {
            if ( rec_sta <= 2 )
            {
                rec_sta++;
            }
            else if ( rec_sta == 3 )
            {
                if ( bytedata != 0xFF )
                {
                    rec_sta = 0;
                    objtype = 0;
                }
                else
                {
                    Ctrl_Data_Analysis( );
                    rec_sta = 0;
                    objtype = 0;
                }
            }
        }
        else if ( objtype == 2 )
        {
            if ( rec_sta <= 4 )
            {
                rec_sta++;
            }
            else if ( rec_sta == 5 )
            {
                if ( bytedata != 0xFF )
                {
                    rec_sta = 0;
                    objtype = 0;
                }
                else
                {
                    Ctrl_Data_Analysis( );
                    rec_sta = 0;
                    objtype = 0;
                }
            }
        }
    }
}
