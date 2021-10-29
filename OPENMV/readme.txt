主要参考ALL2这个文件和匿名给的代码。其他代码可以作为参考，不一定规范。


1.AprilTag文件夹里生成的是用来调试的AprilTag
2.OPENMV-Pan..是控制电机+pid追踪
3.openmv整理是匿名给的代码
4.ALL2是我觉得所有会用到的代码。应该都是各种功能的最终版本，比较规范了，是个大杂烩不要运行，要用的话新开个文件粘贴出来。
5.AprilTag如其名
6.bottom巡线+找圆
7.CirandRECT 找圆+矩形 找圆用的find_circle
8.cirandrecrcolorver 找圆+矩形 找圆用的find_blob
9.DETECT  巡线+找圆古早版，参考意义不大
10.DETECT4 巡线+找圆+扫描二维码 OPENMV跑不动。扫描二维码要用VGA画质。找圆一般QQVGA不然很卡。建议扫码和巡线用两个OPENMV。
11.DetectQRcode 同上
12.LineFollowingTest 寻线+交点+转向判断
13.main 巡线+找圆+找色块
14.match 特征点检测
15. MVSHOT 串口命令录制视频
16.OPENMV2_2:扫描二维码+舵机控制
17.template_matching ：模板匹配。插卡存照片才能用哦。具体看教程，要求很多。