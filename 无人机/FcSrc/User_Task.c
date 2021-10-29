#include "User_Task.h"
#include "Ano_Math.h"
#include "Ano_Pid.h"
#include "Ano_Scheduler.h"

#include "Drv_Ctrl.h"
#include "Drv_OpenMV.h"
#include "Drv_Uart.h"

#include "LX_FC_Fun.h"

// 飞行时间
u32 Flag_Time;
// 实时飞行高度, 更改就能控制高度
u8 Height;
// 控制PID工作
u8 _Height_PID_Flag_          = 0;
u8 _Pillar_Distance_PID_Flag_ = 0;

u8 _Line_Ang_PID_Flag_ = 0;
u8 _Line_Y_PID_Flag_   = 0;

u8 _RedLine_Yaw_PID_Flag_   = 0;
u8 _GreenLine_Yaw_PID_Flag_ = 0;

u8 _Circle_PID_Flag_ = 0;
u8 _Dot_PID_Flag_    = 0;
// 蜂鸣器计数
// !: 必须要为偶数, 否则会出现一直发声的问题
u8 Beep_Count = 0;
u8 Beep_Flag  = 0;

s8  GreenPillar_Find_State[2]    = { 0, 0 };
u8  Find_GreenPillar_Times       = 0;
s16 GreenPillar_FirstAppear_Pos  = 0;
u8  Try_To_Find_GreenPillar_Flag = 0;

u8 CounterClockwise_Rotate_Flag = 0;
u8 Clockwise_Rotate_Flag        = 0;

// 用于判定任务的状态, 在完成任务后一定要复位, 否则将出现问题
u8 Task_State = 0;

#define NextStep                                                                         \
    {                                                                                    \
        Task_State++;                                                                    \
        Flag_Time = GetSysRunTimeMs( );                                                  \
    }

void Test_Task( )
{
    if ( Task_State == 0 )
    {
        // #: 解锁飞控并设置标志.
        FC_Unlock( );
        NextStep;
    }
    else if ( Task_State == 1 )
    {
        // #: 进行延时
        if ( GetSysRunTimeMs( ) - Flag_Time >= 2000 )
            NextStep;
    }
    else if ( Task_State == 2 )
    {
        // #: 起飞同时进行定高
        _Height_PID_Flag_ = 1;
        Height            = 70;
        if ( GetSysRunTimeMs( ) - Flag_Time >= 8000 )
            NextStep;
    }
    else if ( Task_State == 3 )
    {
        // #: 旋转对红色杆子进行寻找
        Set_Dps_Yaw( 10 );
        if ( GetSysRunTimeMs( ) - Flag_Time >= 8800 || redline_feature.flag )
        {
            Set_Dps_Yaw( 0 );
            NextStep;
        }
    }
    else if ( Task_State == 4 )
    {
        // #: 进行绕杆的运动
        CounterClockwise_Rotate_Flag = 1;
        if ( GetSysRunTimeMs( ) - Flag_Time >= 40000 )
        {
            CounterClockwise_Rotate_Flag = 0;
            _Height_PID_Flag_            = 0;
            Stop_Motion( );
            NextStep;
        }
    }
    else if ( Task_State == 5 )
    {
        if ( GetSysRunTimeMs( ) - Flag_Time > 5000 )
        {
            OneKey_Land( );
            NextStep;
        }
    }
    else if ( Task_State == 6 )
    {
        if ( GetSysRunTimeMs( ) - Flag_Time > 3000 )
        {
            Task_State    = 0;
            Working_State = 0;
        }
    }
}

void Task( )
{
    if ( Task_State == 0 )
    {
        // #: 解锁飞控并设置标志.
        FC_Unlock( );
        NextStep;
    }
    else if ( Task_State == 1 )
    {
        // #: 进行延时
        if ( GetSysRunTimeMs( ) - Flag_Time >= 2000 )
            NextStep;
    }
    else if ( Task_State == 2 )
    {
        // #: 起飞同时进行定高
        _Height_PID_Flag_ = 1;
        Height            = 60;
        if ( GetSysRunTimeMs( ) - Flag_Time >= 8000 )
            NextStep;
    }
    else if ( Task_State == 3 )
    {
        // #: 旋转对红色杆子进行寻找
        Set_Dps_Yaw( 8 );

        if ( GetSysRunTimeMs( ) - Flag_Time >= 10000 || redline_feature.flag )
        {
            Set_Dps_Yaw( 0 );
            NextStep;
        }
        // // !: 没有找到
        // else if ( GetSysRunTimeMs( ) - Flag_Time >= 15000 )
        // {
        //     _Height_PID_Flag_ = 0;

        //     Stop_Motion( );
        //     Flag_Time  = GetSysRunTimeMs( );
        //     Task_State = 13;
        // }
    }
    else if ( Task_State == 4 )
    {
        // 开始追踪红色杆子(角度)
        _RedLine_Yaw_PID_Flag_ = 1;
        if ( GetSysRunTimeMs( ) - Flag_Time >= 2000 &&
             my_abs( redline_feature.offset ) < 4 )
        {
            _RedLine_Yaw_PID_Flag_ = 0;
            NextStep;
        }
    }
    else if ( Task_State == 5 )
    {
        Set_vel_X( 8 );
        if ( Ctrl_Dst.distance < 70 )
        {
            Set_vel_X( 0 );
            Try_To_Find_GreenPillar_Flag = 1;
            NextStep;
        }
    }
    // else if ( Task_State == 6 )
    // {
    //     // 开始抵近红色杆子
    //     _Pillar_Distance_PID_Flag_ = 1;
    //     if ( Ctrl_Dst.distance < 70 )
    //     {
    //         _Pillar_Distance_PID_Flag_   = 0;
    //         Try_To_Find_GreenPillar_Flag = 1;
    //         NextStep;
    //     }
    // }
    else if ( Task_State == 6 )
    {
        // #: 进行绕杆的运动
        CounterClockwise_Rotate_Flag = 1;
        // #: 此判断用于判定是否完成一圈的旋转
        if ( Find_GreenPillar_Times >= 2 &&
             ( greenline_feature.offset > ( GreenPillar_FirstAppear_Pos + 5 ) &&
               greenline_feature.offset < ( GreenPillar_FirstAppear_Pos + 12 ) ) &&
             greenline_feature.flag )
            NextStep;
    }
    else if ( Task_State == 7 )
    {
        // #: 进一步旋转到合适的角度
        if ( greenline_feature.offset < -40 )
        {
            // 对积分结果进行一次清除
            _Angle_PID_InteClear_Flag_   = 1;
            CounterClockwise_Rotate_Flag = 0;
            Stop_Horizontal_Move( );
            NextStep;
        }
    }
    else if ( Task_State == 8 )
    {
        // #: 向右侧移动一定的距离防止撞击
        Set_vel_Y( -8 );
        if ( GetSysRunTimeMs( ) - Flag_Time >= 10000 )
        {
            Set_vel_Y( 0 );
            NextStep;
        }
    }
    else if ( Task_State == 9 )
    {
        // 先进行角度调整
        _GreenLine_Yaw_PID_Flag_ = 1;
        if ( my_abs( greenline_feature.offset ) < 5 )
        {
            NextStep;
            _GreenLine_Yaw_PID_Flag_ = 0;
        }
    }
    else if ( Task_State == 10 )
    {
        // 向前前进一定的距离, 便于超声波模块的判断
        Set_vel_X( 8 );
        if ( Ctrl_Dst.distance < 100 )
        {
            NextStep;
            Set_vel_X( 0 );
        }
    }
    else if ( Task_State == 11 )
    {
        // 开始抵近绿色的杆子
        _Pillar_Distance_PID_Flag_ = 1;
        // 抵近成功, 准备进行绕杆的运动
        if ( Ctrl_Dst.distance < 60 )
        {
            _Pillar_Distance_PID_Flag_ = 0;
            _GreenLine_Yaw_PID_Flag_   = 0;
            NextStep;
        }
    }
    else if ( Task_State == 12 )
    {
        // 进行顺时针绕杆运动
        Clockwise_Rotate_Flag = 1;
        if ( GetSysRunTimeMs( ) - Flag_Time >= 40000 )
        {
            Clockwise_Rotate_Flag = 0;
            _Height_PID_Flag_     = 0;
            Stop_Motion( );
            // Stop_Horizontal_Move( );
            NextStep;
        }
    }
    // else if ( Task_State == 14 )
    // {
    //     _Circle_PID_Flag_ = 1;
    //     if ( my_abs( circle_feature.X ) < 3 && my_abs( circle_feature.Y ) < 3 )
    //     {
    //         _Circle_PID_Flag_ = 0;
    //         _Height_PID_Flag_ = 0;

    //         Stop_Motion( );
    //         NextStep;
    //     }
    // }
    else if ( Task_State == 13 )
    {
        if ( GetSysRunTimeMs( ) - Flag_Time > 3000 )
        {
            OneKey_Land( );
            NextStep;
        }
    }
    else if ( Task_State == 14 )
    {
        if ( GetSysRunTimeMs( ) - Flag_Time > 4000 )
        {
            Task_State    = 0;
            Working_State = 0;
        }
    }
    // else if ( Task_State == 12 )
    // {
    //     if ( GetSysRunTimeMs( ) - Flag_Time > 5000 )
    //     {
    //         OneKey_Land( );
    //         NextStep;
    //     }
    // }
    // else if ( Task_State == 13 )
    // {
    //     if ( GetSysRunTimeMs( ) - Flag_Time > 3000 )
    //     {
    //         Task_State    = 0;
    //         Working_State = 0;
    //     }
    // }
}
