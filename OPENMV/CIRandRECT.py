#找圆+找矩形框
# Untitled - By: ghfjd - 周日 7月 25 2021

import sensor, image, time
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
Circle_State_Counter = 0

def UserCircleDataPack(flag, X, Y):
    Temp_X = int(X)
    Temp_Y = int(Y)
    Circle_data = bytearray(
        [0xAA, 0x30, flag, Temp_X >> 8, Temp_X, Temp_Y >> 8, Temp_Y, 0xFF])
    return Circle_data


def Circlecheck(img):
    global Circle_State_Counter
    Circles = img.find_circles(threshold=6000,x_margin=5,y_margin=5,r_margin=30)
    Len_Circles = len(Circles)

    if Len_Circles == 0:
        Circle_State_Counter = 0
        Pack_Circle = UserCircleDataPack(0, 0, 0)
        uart.write(Pack_Circle)
    else:
        if Circle_State_Counter < 5:
            Circle_State_Counter = Circle_State_Counter + 1
        else:
            img.draw_circle(Circles[0].x(),
                            Circles[0].y(),
                            Circles[0].r(),
                            color=(255, 0, 0))
            Pack_Circle = UserCircleDataPack(1, Circles[0].x() - img.width()/2,
                                             img.height()/2- Circles[0].y())
            uart.write(Pack_Circle)



sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 2000)

clock = time.clock()

while(True):
    clock.tick()
    img = sensor.snapshot().lens_corr(1.8)
    Rectanglecheck(img)
    Circlecheck(img)
