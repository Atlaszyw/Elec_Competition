/**************************************************
 * 描述    ：任务调度
 ***************************************************/
#include "Ano_Scheduler.h"

#include "Ano_Kalman.h"
#include "Ano_Math.h"
#include "Ano_Pid.h"

#include "Drv_AnoOf.h"
#include "Drv_Beep.h"
#include "Drv_Ctrl.h"
#include "Drv_OpenMV.h"

#include "LX_FC_Fun.h"
#include "User_Task.h"

u8  Working_State = 0;
s16 Y_velo        = 0;
s16 X_velo        = 0;
s16 Z_velo        = 0;

//////////////////////////////////////////////////////////////////////
//用户程序调度器
//////////////////////////////////////////////////////////////////////

// static void Loop_1000Hz(void) //1ms执行一次
// {
// }

// static void Loop_500Hz(void) //2ms执行一次
// {
// }

// static void Loop_200Hz(void) //5ms执行一次
// {
// }

// static void Loop_100Hz(void) //10ms执行一次
// {
// }

// static void Loop_50Hz( void )    // 20ms执行一次
// {
// }

static void Loop_29Hz( void )    // 33ms执行一次
{
    // #: 定高PID
    if ( _Height_PID_Flag_ )
    {
        if ( Height > 160 )
            Height = 160;
        Z_velo = PID_Height_Set( Height, ano_of.of_alt_cm );
        Set_vel_Z( Z_velo );
    }
}

static void Loop_20Hz( void )    // 50ms执行一次
{
    // ##: Y方向PID, 用于巡线
    // if ( _Line_Y_PID_Flag_ && line_feature.flag == 1 )
    // {
    //     Y_velo = _PID_LineYTracking( line_feature.distance ) *
    //     ano_of.of_alt_cm; Set_vel_Y( Y_velo );
    // }

    // ##: 点追踪PID, 用于拐角的追踪
    // if ( _Dot_PID_Flag_ && dot_feature.flag )
    // {
    //     Set_vel_X( -_PID_PointXTracking( dot_feature.Y ) * ano_of.of_alt_cm
    //     ); Set_vel_Y( _PID_PointYTracking( dot_feature.X ) * ano_of.of_alt_cm
    //     );
    // }

    // ##: 角度PID, 用于在巡线时进行角度的标定
    // if ( _Line_Ang_PID_Flag_ && line_feature.flag == 1 )
    // {
    //     Set_Dps_Yaw( _PID_AngleAdjusting( line_feature.angle ) );
    // }


    // 两种方向的绕杆运动
    if ( Clockwise_Rotate_Flag )
    {
        if ( my_abs( greenline_feature.offset ) < 15 && Ctrl_Dst.flag )
        {
            Set_vel_Y( 8 );
            X_velo = -PID_XTracking( 50, Ctrl_Dst.distance );
            Set_vel_X( X_velo );
        }
        else
        {
            Set_vel_Y( 3 );
            X_velo = 0;
            Set_vel_X( 0 );
        }
        Set_Dps_Yaw( -PID_AngleAdjusting( 0, greenline_feature.offset ) );
    }
    else if ( CounterClockwise_Rotate_Flag )
    {
        if ( my_abs( redline_feature.offset ) < 10 && Ctrl_Dst.flag )
        {
            Set_vel_Y( -8 );
            X_velo = -PID_XTracking( 50, Ctrl_Dst.distance );
            Set_vel_X( X_velo );
        }
        else
        {
            Set_vel_Y( -3 );
            X_velo = 0;
            Set_vel_X( 0 );
        }
        Set_Dps_Yaw( -PID_AngleAdjusting( 0, redline_feature.offset ) );
    }

    // 角度调整, 对准立杆
    if ( _GreenLine_Yaw_PID_Flag_ && greenline_feature.flag )
        Set_Dps_Yaw( -PID_AngleAdjusting( 0, greenline_feature.offset ) );
    else if ( _RedLine_Yaw_PID_Flag_ && redline_feature.flag )
        Set_Dps_Yaw( -PID_AngleAdjusting( 0, redline_feature.offset ) );

    // 距离调整, 用于抵近立杆
    if ( _Pillar_Distance_PID_Flag_ && Ctrl_Dst.distance < 200 )
    {
        Set_vel_X( -PID_XTracking( 50, Ctrl_Dst.distance ) );
    }

    // 进行圆心的追踪
    if ( _Circle_PID_Flag_ && circle_feature.flag )
    {
        Set_vel_X( -PID_XTracking( 0, circle_feature.Y ) * ano_of.of_alt_cm );
        Set_vel_Y( PID_YTracking( 0, circle_feature.X ) * ano_of.of_alt_cm );
    }
}

static void Loop_10Hz( void )    // 100ms执行一次
{
    static s8 tempstate = 0;

    // #: 对绿柱子的出现次数进行判别
    if ( Try_To_Find_GreenPillar_Flag )
    {
        tempstate = Judge_Appear( greenline_feature.flag );
        if ( tempstate != 0 )
        {
            GreenPillar_Find_State[0] = GreenPillar_Find_State[1];
            GreenPillar_Find_State[1] = tempstate;
        }
        if ( GreenPillar_Find_State[1] > 0 && GreenPillar_Find_State[0] < 0 )
        {
            if ( Find_GreenPillar_Times == 0 )
                GreenPillar_FirstAppear_Pos = greenline_feature.offset;

            Find_GreenPillar_Times++;
        }
    }
    else
    {
        GreenPillar_Find_State[0] = GreenPillar_Find_State[1] = -1;
    }
}

static void Loop_5Hz( void )    // 200ms执行一次
{
    // #: 工作模式的选择
    if ( Working_State == 1 )
        Test_Task( );
    if ( Working_State == 2 )
        Task( );
}

static void Loop_2Hz( void )    // 500ms执行一次
{
    // 蜂鸣器计数控制并进行报警
    if ( Beep_Count > 0 && Beep_Flag != 0 )
    {
        Beep_TOGGLE;
        Beep_Count--;
        if ( Beep_Count == 0 )
        {
            Beep_Flag = 0;
        }
    }


    // 控制信号接收
    if ( Ctrl_Signal.task_num == 0x01 && Working_State == 0 )
    {
        Ctrl_Signal.task_num = 0x00;
        Working_State        = 1;
    }
    else if ( Ctrl_Signal.task_num == 0x02 && Working_State == 0 )
    {
        Ctrl_Signal.task_num = 0x00;
        Working_State        = 2;
    }
}

//////////////////////////////////////////////////////////////////////
//调度器初始化
//////////////////////////////////////////////////////////////////////
//系统任务配置，创建不同执行频率的“线程”
static sched_task_t sched_tasks[] = {
    // { Loop_1000Hz, 1000, 0, 0 }, { Loop_500Hz, 500, 0, 0 }, { Loop_200Hz, 200, 0, 0 },
    // { Loop_100Hz, 100, 0, 0 },   { Loop_50Hz, 50, 0, 0 },
    { Loop_29Hz, 29, 0, 0 }, { Loop_20Hz, 20, 0, 0 }, { Loop_10Hz, 10, 0, 0 },
    { Loop_5Hz, 5, 0, 0 },   { Loop_2Hz, 2, 0, 0 },
};

//根据数组长度，判断线程数量
#define TASK_NUM ( sizeof( sched_tasks ) / sizeof( sched_task_t ) )

void Scheduler_Setup( void )
{
    uint8_t index = 0;
    //初始化任务表
    for ( index = 0; index < TASK_NUM; index++ )
    {
        //计算每个任务的延时周期数
        sched_tasks[index].interval_ticks = TICK_PER_SECOND / sched_tasks[index].rate_hz;
        //最短周期为1，也就是1ms
        if ( sched_tasks[index].interval_ticks < 1 )
        {
            sched_tasks[index].interval_ticks = 1;
        }
    }
}

//这个函数放到main函数的while(1)中，不停判断是否有线程应该执行
void Scheduler_Run( void )
{
    uint8_t index = 0;
    //循环判断所有线程，是否应该执行

    for ( index = 0; index < TASK_NUM; index++ )
    {
        //获取系统当前时间，单位MS
        uint32_t tnow = GetSysRunTimeMs( );
        //进行判断，如果当前时间减去上一次执行的时间，大于等于该线程的执行周期，则执行线程
        if ( tnow - sched_tasks[index].last_run >= sched_tasks[index].interval_ticks )
        {
            //更新线程的执行时间，用于下一次判断
            sched_tasks[index].last_run = tnow;
            //执行线程函数，使用的是函数指针
            sched_tasks[index].task_func( );
        }
    }
}
/************************END OF FILE************************/
