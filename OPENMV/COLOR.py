# Untitled - By: ghfjd - 周六 7月 24 2021

import sensor, image, time, pyb
from pyb import UART

Find_Red_Flag = bytearray([0XAA, 0X11])
Find_Green_Flag = bytearray([0XAA, 0X22])
#===============================================LED================================================
Red_Led = pyb.LED(1)  # Red LED = 1, Green LED = 2, Blue LED = 3, IR LEDs = 4.
Green_Led = pyb.LED(2)


#================================================找杆===============================================
def UserColorPackRed(Flag, X):
    TempX = int(X)
    Color_data = bytearray([0xAA, 0x33, Flag, TempX >> 8, TempX, 0xFF])
    return Color_data


def UserColorPackGreen(Flag, X):
    TempX = int(X)
    Color_data = bytearray([0xAA, 0x34, Flag, TempX >> 8, TempX, 0xFF])
    return Color_data


class RecognitionRed(object):
    flag = 0
    cx = 0
    cy = 0


class RecognitionGreen(object):
    flag = 0
    cx = 0
    cy = 0


RecognitionRed = RecognitionRed()
RecognitionGreen = RecognitionGreen()
# 红色阈值
red_threshold = (10, 91, 15, 127, -60, 96)
# 绿色阈值
green_threshold = ((3, 100, -83, -26, -2, 110))


def FindMax(blobs):  #找最大的色块
    max_size = 1
    if blobs:
        max_blob = 0
        for blob in blobs:
            blob_size = blob.w() * blob.h()
            if ((blob_size > max_size) & (blob_size > 100)):  #对最小的色块面积进行限制
                #if (math.fabs(blob.w() / blob.h() - 1) < 2.0):  #色块形状限制,根据物体形状改变
                max_blob = blob
                max_size = blob.w() * blob.h()
        return max_blob


def ColorRecognition(img):
    global Green_Led_Flag
    global Red_Led_Flag
    if Red_Color_Flag == 1:
        Red_blobs = img.find_blobs([red_threshold], area_threshold=200)
        Red_max_blob = FindMax(Red_blobs)
    if Green_Color_Flag == 1:
        Green_blobs = img.find_blobs([green_threshold], area_threshold=200)
        Green_max_blob = FindMax(Green_blobs)  #找到最大的那个
    if Green_max_blob:  #如果找到了目标颜色
        Green_x = Green_max_blob[0]  #或max_blob.x()
        Green_y = Green_max_blob[1]
        Green_width = Green_max_blob[2]  # 色块矩形的宽度
        Green_height = Green_max_blob[3]  # 色块矩形的高度
        Green_center_x = Green_max_blob[5]  # 色块中心点x值
        Green_center_y = Green_max_blob[6]  # 色块中心点y值
        Green_color_code = Green_max_blob[8]  # 颜色代码
        RecognitionGreen.flag = 1
        RecognitionGreen.cx = Green_center_x - img.width() / 2
        RecognitionGreen.cy = img.height() / 2 - Green_center_y
        img.draw_rectangle([Green_x, Green_y, Green_width, Green_height])
        #在目标颜色区域的中心画十字形标记
        img.draw_cross(Green_center_x, Green_center_y)
        if Green_Led_Flag == 0:
            Green_Led_Flag = 1
            Green_Led.on()
            time.sleep_ms(150)  #延时150ms
            Green_Led.off()
            time.sleep_ms(150)  #延时150ms
            Green_Led.on()
            time.sleep_ms(150)  #延时150ms
            Green_Led.off()
            time.sleep_ms(150)  #延时150ms
            Green_Led.on()
            time.sleep_ms(150)  #延时150ms
            Green_Led.off()
            time.sleep_ms(150)  #延时150ms
    else:
        Green_Led_Flag = 0
        RecognitionGreen.flag = 0
        RecognitionGreen.color = 0
        RecognitionGreen.cx = 0
        RecognitionGreen.cy = 0

    if Red_max_blob:  #如果找到了目标颜色
        Red_x = Red_max_blob[0]  #或max_blob.x()
        Red_y = Red_max_blob[1]
        Red_width = Red_max_blob[2]  # 色块矩形的宽度
        Red_height = Red_max_blob[3]  # 色块矩形的高度
        Red_center_x = Red_max_blob[5]  # 色块中心点x值
        Red_center_y = Red_max_blob[6]  # 色块中心点y值
        Red_color_code = Red_max_blob[8]  # 颜色代码
        RecognitionRed.flag = 1
        RecognitionRed.cx = Red_center_x - img.width() / 2
        RecognitionRed.cy = img.height() / 2 - Red_center_y
        #颜色识别
        img.draw_rectangle([Red_x, Red_y, Red_width, Red_height])
        #在目标颜色区域的中心画十字形标记
        img.draw_cross(Red_center_x, Red_center_y)
        if Red_Led_Flag == 0:
            Red_Led_Flag = 1
            Red_Led.on()
            time.sleep_ms(150)  #延时150ms
            Red_Led.off()
            time.sleep_ms(150)  #延时150ms
            Red_Led.on()
            time.sleep_ms(150)  #延时150ms
            Red_Led.off()
            time.sleep_ms(150)  #延时150ms
            Red_Led.on()
            time.sleep_ms(150)  #延时150ms
            Red_Led.off()
            time.sleep_ms(150)  #延时150ms
    else:
        Red_Led_Flag = 0
        RecognitionRed.flag = 0
        RecognitionRed.color = 0
        RecognitionRed.cx = 0
        RecognitionRed.cy = 0
    ColorpackRed = UserColorPackRed(RecognitionRed.flag,
                                    -(int)((RecognitionRed.cx) * 0.5))
    ColorpackGreen = UserColorPackGreen(RecognitionGreen.flag,
                                        -(int)((RecognitionGreen.cx) * 0.5))
    print(-(int)((RecognitionRed.cx) * 0.5))
    print(-(int)((RecognitionGreen.cx) * 0.5))
    uart.write(ColorpackRed)
    uart.write(ColorpackGreen)
    #用矩形标记出目标颜色区域


#=======================================找杆结束===============================================

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)
#sensor.set_contrast(1)  #设置相机图像对比度。-3至+3
#sensor.set_gainceiling(16)  #设置相机图像增益上限。2, 4, 8, 16, 32, 64, 128。
clock = time.clock()
uart = UART(3, 500000)
uart.init(500000)
Red_Color_Flag = 1
Green_Color_Flag = 1
Red_Led_Flag = 0
Green_Led_Flag = 0
while (True):
    clock.tick()
    if uart.any():
        a = uart.read()
        if a == Find_Red_Flag:
            if Red_Color_Flag == 0:
                Red_Color_Flag = 1
            if Red_Color_Flag == 1:
                Red_Color_Flag = 0
        if a == Find_Green_Flag:
            if Green_Color_Flag == 0:
                Green_Color_Flag = 1
            if Green_Color_Flag == 1:
                Green_Color_Flag = 0
    img = sensor.snapshot()
    ColorRecognition(img)
