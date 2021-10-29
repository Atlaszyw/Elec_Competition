# ************************************ (C) COPYRIGHT 2019 ANO ***********************************#
import sensor, image, time, math, mjpeg, cmath
from pyb import UART
# 初始化镜头
# 串口数据打包格式0xAA, 0x29, flag, angle >> 8,angle, distance >> 8, distance,
# T_ms, 0x00
# Line.flag 1,直线 2.左转 3.右转
# Line.angle 两直线夹角
# Line.distance   是直线：中间区域最大色块到横坐标中点位置
# 交点坐标crossx,crossy=0,0阈值20 左右可能比较合适？
ROIS = (30, 0, 100, 120)
Start_Flag = bytearray([0XAA, 0XAA])
Stop_Flag = bytearray([0XAA, 0XBB])
Dot_Flag = bytearray([0XAA, 0XCC])
Line_Flag = bytearray([0XAA, 0XDD])
Color_Flag = bytearray([0XAA, 0XEE])
QRCode_Flag = bytearray([0XAA, 0XFF])
Photo_Flag = bytearray([0XAA, 0X00])
uart = UART(3, 115200)
uart.init(115200)
sensor.reset()
sensor.set_pixformat(sensor.RGB565)  # 设置相机模块的像素模式
sensor.set_framesize(sensor.VGA)  # 设置相机分辨率160*120
sensor.skip_frames(time=3000)  # 时钟
sensor.set_auto_whitebal(False)  # 若想追踪颜色则关闭白平衡
clock = time.clock()  # 初始化时钟
Photo_State = 0
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
            if abs(Line_Theta(line) < Min_angle):
                Temp_Line = line
                Min_angle = abs(Line_Theta(line))

        if (abs(Line_Theta(Temp_Line)) > 30):
            Pack_Line = UserLineDataPack(0, 0, 0)
            uart.write(Pack_Line)
        else:
            Pack_Line = UserLineDataPack(1, Line_Theta(Temp_Line),
                                         Line_Distance(Temp_Line))
            uart.write(Pack_Line)

        if (Len_Lines == 2):
            x, y = CalculateIntersection(Lines[0], Lines[1])
            if (x < 80 and x > -80 and y < 60 and y > -60):
                Pack_Dot = UserDotDataPack(1, x, y)
                uart.write(Pack_Dot)
            else:
                Pack_Dot = UserDotDataPack(0, 0, 0)
                uart.write(Pack_Dot)


# ==============================Circle==============================

Circle_State_Counter = 0


def UserCircleDataPack(flag, X, Y):
    Temp_X = int(X)
    Temp_Y = int(Y)
    Circle_data = bytearray(
        [0xAA, 0x30, flag, Temp_X >> 8, Temp_X, Temp_Y >> 8, Temp_Y, 0xFF])
    return Circle_data


def Circlecheck(img):
    global Circle_State_Counter

    Circles = img.find_circles(threshold=4000,
                               x_margin=5,
                               y_margin=5,
                               r_margin=30,
                               roi=ROIS)
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


#================================QRcode========================================
def UserQRCodePack(Flag, Message, X, Y):  #X,Y指的是二维码的坐标
    TempX = int(X)
    TempY = int(Y)

    QR_data = bytearray([
        0xAA, 0x32, Flag, Message, TempX >> 8, TempX, TempY >> 8, TempY, 0xFF
    ])
    return QR_data


class QRcode(object):
    QRcodemessage = 0


QRcode = QRcode()


def ScanQRcode(img):
    QRCodes = img.find_qrcodes()
    Len_QRCodes = len(QRCodes)
    if Len_QRCodes == 0:
        QRcode.QRcodemessage = 0
        QRcode_x = 0
        QRcode_y = 0
        QRMessage = 0
    else:
        img.draw_rectangle(QRCodes[0].rect(), color=255)
        QRcode.QRcodemessage = 1
        QRcode_x = QRCodes[0].x(
        ) + QRCodes[0].w() / 2 - 160  #二维码中心点的坐标，以图像中心为原点
        QRcode_y = 120 - (QRCodes[0].y() + QRCodes[0].h() / 2)

        print('二维码信息', QRCodes[0].payload(), QRcode_x, QRcode_y)
        if QRCodes[0].payload() == "5":
            QRMessage = 0x05
        if QRCodes[0].payload() == "6":
            QRMessage = 0x06
        if QRCodes[0].payload() == "7":
            QRMessage = 0x07
        if QRCodes[0].payload() == "8":
            QRMessage = 0x08
        if QRCodes[0].payload() == "9":
            QRMessage = 0x09
        if QRCodes[0].payload() == "10":
            QRMessage = 0x0A
        if QRCodes[0].payload() == "向右高度60":
            QRMessage = 0x3C
        if QRCodes[0].payload() == "向左高度70":
            QRMessage = 0x46
    Messagepack = UserQRCodePack(QRcode.QRcodemessage, QRMessage, QRcode_x,
                                 QRcode_y)
    uart.write(Messagepack)
    return None


#========================main=============================

while (True):
    img = sensor.snapshot()
    if uart.any():
        a = uart.read()
        if a == Start_Flag:
            Photo_State = 1
        if a == Stop_Flag:
            Photo_State = 2
    if Photo_State == 1:
        m = mjpeg.Mjpeg("example.mjpeg")
        clock.tick()
        # mjpeg.add_frame(image, quality=50)，向mjpeg视频中中添加图片，
        # quality为视频压缩质量。
        m.add_frame(img)
    if Photo_State == 2:
        m.close(clock.fps())
        Photo_State = 0
    Circlecheck(img)
    LineCheck(img)
    ScanQRcode(img)

# ************************************ (C) COPYRIGHT 2019 ANO ***********************************#
