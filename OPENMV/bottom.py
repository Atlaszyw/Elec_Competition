#巡线+找圆

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
    else:
        Temp_Line = Lines[0]
        for line in Lines:
            if abs(Line_Theta(line)) < Min_angle:
                Temp_Line = line
                Min_angle = abs(Line_Theta(line))

        if (abs(Line_Theta(Temp_Line)) > 30):
            Pack_Line = UserLineDataPack(0, 0, 0)
            uart.write(Pack_Line)
        else:
            img.draw_line(Temp_Line.line(), [255, 0, 0], 2)
            Pack_Line = UserLineDataPack(1, Line_Theta(Temp_Line),
                                         Line_Distance(Temp_Line))
            uart.write(Pack_Line)

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


def UserCircleDataPack(flag, X, Y):
    """
    用于打包圆的数据

    Arguments:
        flag {int} -- 检测是否有圆
        X {int} -- X坐标
        Y {int} -- Y坐标

    Returns:
        bytearray -- 数据包
    """
    Temp_X = int(X)
    Temp_Y = int(Y)
    Circle_data = bytearray(
        [0xAA, 0x30, flag, Temp_X >> 8, Temp_X, Temp_Y >> 8, Temp_Y, 0xFF])
    return Circle_data


def Circlecheck(img):
    global Circle_State_Counter

    Circles = img.find_circles(threshold=3500,
                               x_margin=5,
                               y_margin=5,
                               r_margin=30)
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
            Pack_Circle = UserCircleDataPack(1, Circles[0].x() - 80,
                                             60 - Circles[0].y())
            uart.write(Pack_Circle)


# =====================Variable===========================
ROIS = (30, 0, 100, 120)
Start_Flag = bytearray([0XAA, 0XAA])
Stop_Flag = bytearray([0XAA, 0XBB])
Circle_Start_Flag = bytearray([0xAA, 0xCC])
Circle_Stop_Flag = bytearray([0xAA, 0xDD])

uart = UART(3, 500000)
uart.init(500000)

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)  # 设置相机模块的像素模式
sensor.set_framesize(sensor.QQVGA)  # 设置相机分辨率160*120
sensor.skip_frames(time=3000)  # 时钟
sensor.set_auto_whitebal(False)  # 若想追踪颜色则关闭白平衡
clock = time.clock()  # 初始化时钟
Photo_State = 0
Circle_State = 0
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

        if a == Circle_Start_Flag:
            Circle_State = 1
        elif a == Circle_Stop_Flag:
            Circle_State = 0

    # if Circle_State == 1:
    Circlecheck(img)

    LineCheck(img)

    if Photo_State == 1:
        clock.tick()
        # mjpeg.add_frame(image, quality=50)，向mjpeg视频中中添加图片，
        # quality为视频压缩质量。
        m.add_frame(img, quality=70)
    elif Photo_State == 2:
        m.close(clock.fps())
        Photo_State = 0
# ***************** End of File *******************
