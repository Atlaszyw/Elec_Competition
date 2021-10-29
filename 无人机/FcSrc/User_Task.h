#ifndef __USER_TASK_H
#define __USER_TASK_H

#include "SysConfig.h"

// 飞行时间
extern u32 Flag_Time;
// 实时飞行高度, 更改就能控制高度
extern u8 Height;
// 控制PID工作
extern u8 _Height_PID_Flag_;
extern u8 _Pillar_Distance_PID_Flag_;

extern u8 _Line_Ang_PID_Flag_;
extern u8 _Line_Y_PID_Flag_;

extern u8 _RedLine_Yaw_PID_Flag_;
extern u8 _GreenLine_Yaw_PID_Flag_;

extern u8 _Circle_PID_Flag_;
extern u8 _Dot_PID_Flag_;
// 蜂鸣器计数
// !: 必须要为偶数, 否则会出现一直发声的问题
extern u8 Beep_Count;
extern u8 Beep_Flag;

extern s8  GreenPillar_Find_State[2];
extern u8  Find_GreenPillar_Times;
extern s16 GreenPillar_FirstAppear_Pos;
extern u8  Try_To_Find_GreenPillar_Flag;

extern u8 CounterClockwise_Rotate_Flag;
extern u8 Clockwise_Rotate_Flag;

void Task( void );
void Test_Task( void );
#endif
