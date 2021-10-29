#include "Drv_OpenMV.h"

u8 openmv_buf[20];
// 0x29:直线 0x30:点 0x31:圆 0x32:二维码 0x33:红线 0x34:绿线
// openmv 1:下视摄像头  2:前视摄像头
// 点信息
opmv_dot_t dot_feature;
// 直线信息
opmv_line_t line_feature;
// 圆信息
opmv_circle_t circle_feature;
// 二维码信息, 包含暂存建
opmv_qrcode_t qrcode_feature;
opmv_qrcode_t qrcode_feature_get;
// 两种颜色色块数据
opmv_redline_t   redline_feature;
opmv_greenline_t greenline_feature;

static void OpenMVNo1_Data_Analysis( )
{
    if ( openmv_buf[1] == 0x30 )
    {
        dot_feature.flag = openmv_buf[2];
        dot_feature.X    = (s16)( openmv_buf[3] << 8 | openmv_buf[4] );
        dot_feature.Y    = (s16)( openmv_buf[5] << 8 | openmv_buf[6] );
    }
    else if ( openmv_buf[1] == 0x31 )
    {
        line_feature.flag     = openmv_buf[2];
        line_feature.angle    = (s16)( openmv_buf[3] << 8 | openmv_buf[4] );
        line_feature.distance = (s16)( openmv_buf[5] << 8 | openmv_buf[6] );
    }
    else if ( openmv_buf[1] == 0x32 )
    {
        circle_feature.flag = openmv_buf[2];
        circle_feature.X    = (s16)( openmv_buf[3] << 8 | openmv_buf[4] );
        circle_feature.Y    = (s16)( openmv_buf[5] << 8 | openmv_buf[6] );
    }
}

static void OpenMVNo2_Data_Analysis( )
{
    if ( openmv_buf[1] == 0x32 )
    {
        qrcode_feature.flag    = openmv_buf[2];
        qrcode_feature.message = openmv_buf[3];
        if ( qrcode_feature.flag == 1 )
        {
            qrcode_feature_get = qrcode_feature;
        }
    }
    else if ( openmv_buf[1] == 0x33 )
    {
        redline_feature.flag   = openmv_buf[2];
        redline_feature.offset = (s16)( openmv_buf[3] << 8 | openmv_buf[4] );
    }
    else if ( openmv_buf[1] == 0x34 )
    {
        greenline_feature.flag   = openmv_buf[2];
        greenline_feature.offset = (s16)( openmv_buf[3] << 8 | openmv_buf[4] );
    }
}

void OpenMVNo1_GetOneByte( u8 bytedata )
{
    static u8 rec_sta = 0;
    static u8 objtype = 0;

    openmv_buf[rec_sta] = bytedata;

    if ( rec_sta == 0 )
    {
        if ( bytedata == 0xAA )
        {
            rec_sta++;
        }
        else
        {
            rec_sta = 0;
        }
    }
    else if ( rec_sta == 1 )
    {
        if ( bytedata == 0x29 )
        {
            rec_sta++;
            objtype = 1;
            return;
        }
        else if ( bytedata == 0x30 )
        {
            rec_sta++;
            objtype = 2;
            return;
        }
        else if ( bytedata == 0x31 )
        {
            rec_sta++;
            objtype = 3;
            return;
        }
        else if ( bytedata == 0x32 )
        {
            rec_sta++;
            objtype = 4;
            return;
        }
        else
        {
            rec_sta = 0;
            objtype = 0;
            return;
        }
    }
    if ( rec_sta >= 2 )
    {
        if ( objtype == 1 )
        {
            if ( rec_sta <= 6 )
            {
                rec_sta++;
            }
            else if ( rec_sta == 7 )
            {
                if ( bytedata != 0xFF )
                {
                    rec_sta = 0;
                    objtype = 0;
                }
                else
                {
                    OpenMVNo1_Data_Analysis( );
                    rec_sta = 0;
                    objtype = 0;
                }
            }
        }
        else if ( objtype == 2 )
        {
            if ( rec_sta <= 6 )
            {
                rec_sta++;
            }
            else if ( rec_sta == 7 )
            {
                if ( bytedata != 0xFF )
                {
                    rec_sta = 0;
                    objtype = 0;
                }
                else
                {
                    OpenMVNo1_Data_Analysis( );
                    rec_sta = 0;
                    objtype = 0;
                }
            }
        }
        else if ( objtype == 3 )
        {
            if ( rec_sta <= 6 )
            {
                rec_sta++;
            }
            else if ( rec_sta == 7 )
            {
                if ( bytedata != 0xFF )
                {
                    rec_sta = 0;
                    objtype = 0;
                }
                else
                {
                    OpenMVNo1_Data_Analysis( );
                    rec_sta = 0;
                    objtype = 0;
                }
            }
        }
    }
}

void OpenMVNo2_GetOneByte( u8 bytedata )
{
    static u8 rec_sta   = 0;
    static u8 objtype   = 0;
    openmv_buf[rec_sta] = bytedata;

    if ( rec_sta == 0 )
    {
        if ( bytedata == 0xAA )
            rec_sta++;
        else
            rec_sta = 0;
    }
    else if ( rec_sta == 1 )
    {
        if ( bytedata == 0x32 )
        {
            rec_sta++;
            objtype = 1;
            return;
        }
        if ( bytedata == 0x33 )
        {
            rec_sta++;
            objtype = 2;
            return;
        }
        if ( bytedata == 0x34 )
        {
            rec_sta++;
            objtype = 3;
            return;
        }
    }
    else if ( rec_sta >= 2 )
    {
        if ( objtype == 1 )
        {
            if ( rec_sta <= 3 )
            {
                rec_sta++;
            }
            else if ( rec_sta == 4 )
            {
                if ( bytedata != 0xFF )
                {
                    rec_sta = 0;
                    objtype = 0;
                }
                else
                {
                    OpenMVNo2_Data_Analysis( );
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
                    OpenMVNo2_Data_Analysis( );
                    rec_sta = 0;
                    objtype = 0;
                }
            }
        }
        else if ( objtype == 3 )
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
                    OpenMVNo2_Data_Analysis( );
                    rec_sta = 0;
                    objtype = 0;
                }
            }
        }
    }
}
