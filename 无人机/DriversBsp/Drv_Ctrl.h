#include "ANO_LX.h"
#include "Drv_Sys.h"
#include "SysConfig.h"

typedef struct
{
    u8 task_num;
} Ctrl_Sgn_t;

typedef struct
{
    u8  flag;
    u16 distance;
    u16 kal_distance;
} Ctrl_Distance_t;

extern Ctrl_Sgn_t      Ctrl_Signal;
extern Ctrl_Distance_t Ctrl_Dst;

void Ctrl_GetOneByte( u8 bytedata );
