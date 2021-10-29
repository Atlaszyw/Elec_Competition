/******************************
 * 描述    ：主循环
 ******************************/
#include "Ano_Scheduler.h"
#include "LX_FC_Fun.h"
#include "SysConfig.h"
#include "User_Task.h"

// #define test
#ifdef USE_FULL_ASSERT
void assert_failed( uint8_t* file, uint32_t line )
{
    while ( 1 )
    {
        //当系统出错后，会进入这个死循环
    }
}
#endif

//==============================
int main( void )
{
    //进行所有设备的初始化，并将初始化结果保存
    All_Init( );
    MyDelayMs( 13000 );

#ifdef test
#endif
    // 调度器初始化，系统为裸奔，这里人工做了一个时分调度器
    Scheduler_Setup( );
    while ( 1 )
    {
        // 运行任务调度器，所有系统功能，除了中断服务函数，都在任务调度器内完成
        Scheduler_Run( );
    }
}
/************************END OF FILE************************/
