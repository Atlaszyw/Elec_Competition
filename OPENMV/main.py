import sensor, image, time, math, mjpeg
from pyb import UART

# ==============================Dot=================================


def UserDotDataPack(flag, X, Y):
    Temp_X = int(X)
    Temp_Y = int(Y)

    Cross_data = bytearray(
        [0xAA, 0x31, flag, Temp_X >> 8, Temp_X, Temp_Y >> 8, Temp_Y, 0xFF])
    return Cross_data


# ==============================Line================================

Line_State_Counter = 0
Line_Distance_Counter = 0


def UserLineDataPack(flag, Angle, Distance):
    Temp_Angle = int(Angle)
    Temp_Distance = int(Distance)

    Line_data = bytearray([
        0xAA, 0x29, flag, Temp_Angle >> 8, Temp_Angle, Temp_Distance >> 8,
        Temp_Distance, 0xFF
    ])
    return Line_data


def Line_Theta(Line):
    if Line.y2() == Line.y1():
        return 90
    angle = math.atan(
        (Line.x1() - Line.x2()) / (Line.y2() - Line.y1())) * 180 / math.pi
    return angle


def Line_Distance(Line):
    return (Line.x1() + Line.x2()) / 2 - 80


def CalculateIntersection(line1, line2):
    a1 = line1.y2() - line1.y1()
    b1 = line1.x1() - line1.x2()
    c1 = line1.x2() * line1.y1() - line1.x1() * line1.y2()

    a2 = line2.y2() - line2.y1()
    b2 = line2.x1() - line2.x2()
    c2 = line2.x2() * line2.y1() - line2.x1() * line2.y2()
    if (a1 * b2 - a2 * b1) != 0 and (a2 * b1 - a1 * b2) != 0:
        cross_x = int((b1 * c2 - b2 * c1) / (a1 * b2 - a2 * b1))
        cross_y = int((c1 * a2 - c2 * a1) / (a1 * b2 - a2 * b1))

        cross_x = cross_x - 80
        cross_y = 60 - cross_y
        return (cross_x, cross_y)
    else:
        return (0, 0)


def LineCheck(img):
    global Line_State_Counter
    global Line_Distance_Counter

    Lines = img.find_lines(threshold=1200,
                           theta_margin=25,
                           rho_margin=25,
                           roi=ROIS)
    Len_Lines = len(Lines)
    Min_angle = 180

    if Len_Lines == 0:
        Pack_Line = UserLineDataPack(0, 0, 0)
        uart.write(Pack_Line)
        Pack_Dot = UserDotDataPack(0, 0, 0)
        uart.write(Pack_Dot)
        Line_State_Counter = 0
        Line_Distance_Counter = 0
    else:
        Temp_Line = Lines[0]
        for line in Lines:
            if abs(Line_Theta(line)) < Min_angle:
                Temp_Line = line
                Min_angle = abs(Line_Theta(line))

        if (abs(Line_Theta(Temp_Line)) > 30):
            Line_State_Counter = 0
            Line_Distance_Counter = 0
            Pack_Line = UserLineDataPack(0, 0, 0)
            uart.write(Pack_Line)
        else:
            img.draw_line(Temp_Line.line(), [255, 0, 0], 2)

            if Line_State_Counter < 3:
                Line_State_Counter = Line_State_Counter + 1
                Line_Distance_Counter = Line_Distance_Counter + Line_Distance(
                    Temp_Line)

            else:
                Line_Distance_Counter = Line_Distance_Counter / 3
                print(Line_Distance_Counter, Line_Distance(Temp_Line))
                Pack_Line = UserLineDataPack(1, Line_Theta(Temp_Line),
                                             Line_Distance_Counter)
                uart.write(Pack_Line)

                Line_State_Counter = 0
                Line_Distance_Counter = 0

        if (Len_Lines == 1):
            Pack_Dot = UserDotDataPack(0, 0, 0)
            uart.write(Pack_Dot)

        elif (Len_Lines == 2):
            x, y = CalculateIntersection(Lines[0], Lines[1])
            if (x < 80 and x > -80 and y < 60 and y > -60):
                Pack_Dot = UserDotDataPack(1, x, y)
                uart.write(Pack_Dot)
                img.draw_cross(x + 80, -y + 60, 5, color=[255, 0, 0])
            else:
                Pack_Dot = UserDotDataPack(0, 0, 0)
                uart.write(Pack_Dot)
        elif (Len_Lines >= 3):
            Pack_Dot = UserDotDataPack(0, 0, 0)
            uart.write(Pack_Dot)


# ==============================Circle==============================

Circle_State_Counter = 0
Circle_Center_x = 0
Circle_Center_y = 0
Circle_Center_r = 0


def UserCircleDataPack(flag, X, Y):
    Temp_X = int(X)
    Temp_Y = int(Y)
    Circle_data = bytearray(
        [0xAA, 0x30, flag, Temp_X >> 8, Temp_X, Temp_Y >> 8, Temp_Y, 0xFF])
    return Circle_data


def Circlecheck(img):
    global Circle_State_Counter
    global Circle_Center_x
    global Circle_Center_y
    global Circle_Center_r
    Circles = img.find_circles(threshold=2200,
                               x_margin=8,
                               y_margin=8,
                               r_margin=30)
    Len_Circles = len(Circles)
    if Len_Circles == 0:
        Circle_State_Counter = 0
        Pack_Circle = UserCircleDataPack(0, 0, 0)
        uart.write(Pack_Circle)

    else:
        if Circle_State_Counter < 2:
            Circle_State_Counter = Circle_State_Counter + 1
            Circle_Center_x = Circle_Center_x + Circles[0].x()
            Circle_Center_y = Circle_Center_y + Circles[0].y()
            Circle_Center_r = Circle_Center_r + Circles[0].r()
        else:
            Circle_Center_x = Circle_Center_x / 2
            Circle_Center_y = Circle_Center_y / 2
            Circle_Center_r = Circle_Center_r / 2
            print(Circle_Center_x, Circle_Center_y, Circle_Center_y)
            img.draw_circle(int(Circle_Center_x),
                            int(Circle_Center_y),
                            int(Circle_Center_r),
                            color=(255, 0, 0))
            Pack_Circle = UserCircleDataPack(1, Circle_Center_x - 80,
                                             60 - Circle_Center_y)
            uart.write(Pack_Circle)
            Circle_Center_r = 0
            Circle_Center_y = 0
            Circle_Center_x = 0
            Circle_State_Counter = 0


# =====================检测红色色块==========================
# sensor.set_contrast(1)  #设置相机图像对比度。-3至+3
# sensor.set_gainceiling(16)  #设置相机图像增益上限。2, 4, 8, 16, 32, 64, 128。
# def UserColorPack(Flag, Color, X, Y):
# TempX = int(X)
# TempY = int(Y)
# Color_data = bytearray([
# 0xAA, 0x32, Flag, Color, TempX >> 8, TempX, TempY >> 8, TempY, 0xFF
# ])
# return Color_data


class Recognition(object):
    flag = 0
    cx = 0
    cy = 0


Recognition = Recognition()
# 红色阈值
red_threshold = (28, 54, 18, 81, -60, 78)

# 颜色1: 红色的颜色代码
red_color_code = 1


def FindMax(blobs):  #找最大的色块
    max_size = 1
    if blobs:
        max_blob = 0
        for blob in blobs:
            blob_size = blob.w() * blob.h()
            if ((blob_size > max_size) & (blob_size > 100)):
                if (math.fabs(blob.w() / blob.h() - 1) <
                        2.0):  #色块形状限制,根据物体形状改变
                    max_blob = blob
                    max_size = blob.w() * blob.h()
        return max_blob


def ColorRecognition(img):
    blobs = img.find_blobs([red_threshold], area_threshold=1)
    max_blob = FindMax(blobs)  #找到最大的那个
    if max_blob:  #如果找到了目标颜色
        x = max_blob[0]  #或max_blob.x()
        y = max_blob[1]
        width = max_blob[2]  # 色块矩形的宽度
        height = max_blob[3]  # 色块矩形的高度
        center_x = max_blob[5]  # 色块中心点x值
        center_y = max_blob[6]  # 色块中心点y值
        color_code = max_blob[8]  # 颜色代码
        #颜色识别
        if color_code == red_color_code:
            img.draw_string(x, y - 10, "red", color=(0xFF, 0x00, 0x00))
            Recognition.flag = 1
            Recognition.color = 1
            Recognition.cx = (center_x - img.width() / 2) * 0.3
            Recognition.cy = (img.height() / 2 - center_y) * 0.3
            img.draw_rectangle([x, y, width, height])
            #在目标颜色区域的中心画十字形标记
            img.draw_cross(center_x, center_y)
    else:
        Recognition.flag = 0
        Recognition.color = 0
        Recognition.cx = 0
        Recognition.cy = 0
    Colorpack = UserCircleDataPack(Recognition.flag, Recognition.cx,
                                   Recognition.cy)
    print("Colorpack", Recognition.flag, Recognition.cx, Recognition.cy)
    uart.write(Colorpack)
    #用矩形标记出目标颜色区域


# =====================Variable===========================
ROIS = (20, 0, 120, 120)
Start_Flag = bytearray([0XAA, 0XAA])
Stop_Flag = bytearray([0XAA, 0XBB])
Circle_Start_Flag = bytearray([0xAA, 0xCC])
Circle_Stop_Flag = bytearray([0xAA, 0xDD])
Task_Flag = bytearray([0xAA, 0xFF])
uart = UART(3, 500000)
uart.init(500000)

sensor.reset()
sensor.set_pixformat(sensor.RGB565)  # 设置相机模块的像素模式
sensor.set_framesize(sensor.QVGA)  # 设置相机分辨率160*120
sensor.skip_frames(time=3000)  # 时钟
sensor.set_auto_whitebal(False)  # 若想追踪颜色则关闭白平衡
clock = time.clock()  # 初始化时钟
Photo_State = 0
Circle_State = 0
Task_State = 0
# ========================main=============================
while (True):
    clock.tick()
    img = sensor.snapshot()
    if uart.any():
        a = uart.read()
        if a == Start_Flag:
            Photo_State = 1
            m = mjpeg.Mjpeg("Video.mjpeg")
        elif a == Stop_Flag:
            Photo_State = 2
        #if a == Circle_Start_Flag:
        #Circle_State = 1
        #elif a == Circle_Stop_Flag:
        #Circle_State = 0
        #if a == Task_Flag:
        #if Task_State==0:
        #sensor.set_framesize(sensor.QVGA)  # 设置相机分辨率160*120
        #Task_State=3
        #if Task_State==3:
        #sensor.set_framesize(sensor.QQVGA)  # 设置相机分辨率160*120
        #Task_State=0
    #if Task_State==0:
    #img = sensor.snapshot()
    #Circlecheck(img)
    #LineCheck(img)
    #if Task_State==3:
    #img = sensor.snapshot()
    #ColorRecognition(img)
    ColorRecognition(img)
    if Photo_State == 1:
        clock.tick()
        m.add_frame(img)
    elif Photo_State == 2:
        m.close(clock.fps())
        Photo_State = 0
# ***************** End of File *******************
