#找圆+找矩形框。找圆使用的是找色块的方法
# Untitled - By: ghfjd - 周日 7月 25 2021

import sensor, image, time,math
from pyb import UART
uart = UART(3, 500000)
uart.init(500000)
#==============================================识别矩形==============================================
Rectangle_State_Counter = 0

def UserRectangleDataPack(flag, X, Y):
    Temp_X = int(X)
    Temp_Y = int(Y)
    Rectangle_data = bytearray(
        [0xAA, 0x34, flag, Temp_X >> 8, Temp_X, Temp_Y >> 8, Temp_Y, 0xFF])
    return Rectangle_data


def Rectanglecheck(img):
    global Rectangle_State_Counter
    Rectangles = img.find_rects(threshold=40000)
    Len_Rectangles= len(Rectangles)

    if Len_Rectangles == 0:
        Rectangle_State_Counter = 0
        Pack_Rectangles = UserRectangleDataPack(0, 0, 0)
        uart.write(Pack_Rectangles)
    else:
        Pack_Rectangle = UserRectangleDataPack(1, Rectangles[0].x()+Rectangles[0].w()/2-img.width()/2,
                                               img.height()/2 - Rectangles[0].y()-Rectangles[0].h()/2)
        img.draw_rectangle(Rectangles[0].rect(), color = (255, 0, 0))
        uart.write(Pack_Rectangle)
#==============================================识别圆================================================
#sensor.set_contrast(1)  #设置相机图像对比度。-3至+3
#sensor.set_gainceiling(16)  #设置相机图像增益上限。2, 4, 8, 16, 32, 64, 128。
def UserColorPack(Flag, X, Y):
    TempX = int(X)
    TempY = int(Y)
    Color_data = bytearray([
        0xAA, 0x33, Flag, TempX >> 8, TempX, TempY >> 8, TempY, 0xFF
    ])
    return Color_data


class Recognition(object):
    flag = 0
    color = 0
    cx = 0
    cy = 0


Recognition = Recognition()
# 红色阈值
red_threshold = (40, 91, 34, 127, -60, 96)
# 绿色阈值
green_threshold = (42, 100, -84, -26, -2, 108)
# 蓝色阈值
blue_threshold = (40, 97, -68, 26, -64, -27)

black_threshold=(0, 25, -32, 2, 3, 23)

def FindMax(blobs):   #找最大的色块
    max_size = 1
    if blobs:
        max_blob = 0
        for blob in blobs:
            blob_size = blob.w() * blob.h()
            if ((blob_size > max_size) & (blob_size > 1)):
                if (math.fabs(blob.w() / blob.h() - 1) < 2.0):  #色块形状限制,根据物体形状改变
                    max_blob = blob
                    max_size = blob.w() * blob.h()
        return max_blob


def ColorRecognition(img):
    blobs = img.find_blobs([black_threshold
    ],area_threshold=1000)
    max_blob = FindMax(blobs)  #找到最大的那个
    if max_blob:  #如果找到了目标颜色
        x = max_blob[0]    #或max_blob.x()
        y = max_blob[1]
        width = max_blob[2]  # 色块矩形的宽度
        height = max_blob[3]  # 色块矩形的高度
        center_x = max_blob[5]  # 色块中心点x值
        center_y = max_blob[6]  # 色块中心点y值
        color_code = max_blob[8]  # 颜色代码
        Recognition.flag = 1
        Recognition.cx = center_x -img.width()/2
        Recognition.cy = img.height()/2-center_y
        img.draw_rectangle([x, y, width, height])
        img.draw_cross(center_x, center_y)
    else:
        Recognition.flag = 0
        Recognition.color = 0
        Recognition.cx = 0
        Recognition.cy = 0
    Colorpack= UserColorPack(Recognition.flag,Recognition.cx,Recognition.cy)
    uart.write(Colorpack)
        #用矩形标记出目标颜色区域


sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 2000)

clock = time.clock()

while(True):
    clock.tick()
    img = sensor.snapshot().lens_corr(1.8)
    Rectanglecheck(img)
    ColorRecognition(img)
