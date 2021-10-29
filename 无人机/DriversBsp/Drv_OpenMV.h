#include "ANO_LX.h"
#include "Drv_Sys.h"
#include "SysConfig.h"

typedef struct
{
    // #: 直线数据
    u8  flag;
    s16 angle;
    s16 distance;
} opmv_line_t;

typedef struct
{
    // #: 点数据
    u8  flag;
    s16 X;
    s16 Y;
} opmv_dot_t;

typedef struct
{
    // #: 圆数据
    u8  flag;
    s16 X;
    s16 Y;
} opmv_circle_t;

typedef struct
{
    // #: 二维码数据
    u8 flag;
    u8 message;
} opmv_qrcode_t;

typedef struct
{
    // #: 红色块数据
    u8  flag;
    s16 offset;
} opmv_redline_t;

typedef struct
{
    // #: 红色块数据
    u8  flag;
    s16 offset;
} opmv_greenline_t;

extern opmv_qrcode_t    qrcode_feature;
extern opmv_qrcode_t    qrcode_feature_get;
extern opmv_line_t      line_feature;
extern opmv_circle_t    circle_feature;
extern opmv_dot_t       dot_feature;
extern opmv_redline_t   redline_feature;
extern opmv_greenline_t greenline_feature;

void OpenMVNo1_GetOneByte( u8 bytedata );
void OpenMVNo2_GetOneByte( u8 bytedata );
