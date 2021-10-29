# Untitled - By: ghfjd - 周五 7月 30 2021

import sensor, image, time, math
from pyb import UART

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time=2000)

clock = time.clock()
uart = UART(3, 500000)
uart.init(500000)


def UserDotDataPack(flag, X, Y):
    Temp_X = int(X)
    Temp_Y = int(Y)

    Cross_data = bytearray(
        [0xAA, 0x31, flag, Temp_X >> 8, Temp_X, Temp_Y >> 8, Temp_Y, 0xFF])
    return Cross_data


Black_threshold = (4, 31, -20, 49, -36, 58)  # 寻线 用  黑色
ROISForLines = {
    'down': (0, 105, 160, 15),  # 横向取样-下方       1
    'middle': (0, 52, 160, 15),  # 横向取样-中间       2
    'up': (0, 0, 160, 15),  # 横向取样-上方       3
    'left': (0, 0, 15, 120),  # 纵向取样-左侧       4
    'right': (145, 0, 15, 120),  # 纵向取样-右侧       5
    'All': (0, 0, 160, 120),  # 全画面取样-全画面    6
}


def UserDirectionDataPack(direction):
    Temp_Direction = int(direction)
    Direction_data = bytearray([0xAA, 0x31, Temp_Direction, 0xFF])
    return Direction_data


DirectionFlag = 0


def find_direction(img):  #判断向左转或向右转
    global ROISForLines
    global DirectionFlag
    roi_blobs_result = {}  # 在各个ROI中寻找色块的结果记录
    for roi_direct in ROISForLines.keys():  #数值复位
        roi_blobs_result[roi_direct] = {'cx': -1, 'cy': -1, 'blob_flag': False}
    for roi_direct, roi in ROISForLines.items():  #每个感兴趣区分别寻找色块
        blobs = img.find_blobs([Black_threshold],
                               roi=roi,
                               merge=True,
                               pixels_area=10)
        if len(blobs) == 0:  #没有色块，继续进行下一次循环
            continue
        largest_blob = max(blobs, key=lambda b: b.pixels())  #找最大的色块
        x, y, width, height = largest_blob[:4]

        if not (width >= 10 and width <= 45 and height >= 10 and height <= 45):
            # 根据色块的长宽进行过滤
            continue
        roi_blobs_result[roi_direct]['cx'] = largest_blob.cx()
        roi_blobs_result[roi_direct]['cy'] = largest_blob.cy()
        roi_blobs_result[roi_direct]['blob_flag'] = True
        img.draw_rectangle((x, y, width, height),
                           color=(0, 255, 255))  #！！！！！！！！！！！！！！！
    # 判断是否需要左转与右转
    DirectionFlag = 0
    if (not roi_blobs_result['up']['blob_flag']
        ) and roi_blobs_result['down']['blob_flag'] and roi_blobs_result[
            'left']['blob_flag'] != roi_blobs_result['right']['blob_flag']:
        if roi_blobs_result['left']['blob_flag']:
            DirectionFlag = 1  #左转
            print("左转")
        if roi_blobs_result['right']['blob_flag']:
            DirectionFlag = 2  #右转
            print("右转")
    return None


def UserLineDataPack(flag, Angle, Distance):
    Temp_Angle = int(Angle)
    Temp_Distance = int(Distance)
    Line_data = bytearray([
        0xAA, 0x29, flag, Temp_Angle >> 8, Temp_Angle, Temp_Distance >> 8,
        Temp_Distance, 0xFF
    ])
    return Line_data


def Line_Theta(Line):  #与Y轴夹角
    if Line.y2() == Line.y1():
        return 90
    angle = math.atan(
        (Line.x1() - Line.x2()) / (Line.y2() - Line.y1())) * 180 / math.pi
    return angle


def Line_Distance(Line):  #直线中点到到图像中点距离
    return (Line.x1() + Line.x2()) / 2 - 80


def CalculateIntersection(line1, line2):  #计算交点，以图像中点为原点
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


def LineCheck(img):  #前进方向巡线，发送角度最小的直线的角度距离，如果有交点以及转向也同时发送
    Lines = img.find_lines(threshold=1200, theta_margin=25, rho_margin=25)
    Len_Lines = len(Lines)
    Min_angle = 180

    if Len_Lines == 0:  #没有直线
        Pack_Line = UserLineDataPack(0, 0, 0)
        uart.write(Pack_Line)
        Pack_Dot = UserDotDataPack(0, 0, 0)
        uart.write(Pack_Dot)
    else:
        Temp_Line = Lines[0]
        for line in Lines:
            if abs(Line_Theta(line)) < Min_angle:  #找出角度最小的直线
                Temp_Line = line
                Min_angle = abs(Line_Theta(line))
        if (abs(Line_Theta(Temp_Line))) > 30:  #如果角度最小的直线仍大于30°，滤除
            Pack_Line = UserLineDataPack(0, 0, 0)
            uart.write(Pack_Line)
        else:  #发送角度最小的线
            Pack_Line = UserLineDataPack(1, Line_Theta(Temp_Line),
                                         Line_Distance(Temp_Line))
            uart.write(Pack_Line)
            img.draw_line(Temp_Line.line(), color=(255, 0, 0))  #！！！！！！！！！！！！
        if (Len_Lines == 2):  #有两条直线，也发送交点坐标,或判断转向
            x, y = CalculateIntersection(Lines[0], Lines[1])
            if (x < img.width() / 2 and x > -(img.width() / 2)
                    and y < img.height() / 2
                    and y > -(img.height() / 2)):  #判断交点是否在图像内
                Pack_Dot = UserDotDataPack(1, x, y)
                uart.write(Pack_Dot)
                print("交点", x, y)
                img.draw_cross(int(x + img.width() / 2),
                               int(img.height() / 2 - y),
                               color=[255, 0, 0])  #！！！
            else:
                Pack_Dot = UserDotDataPack(0, 0, 0)
                uart.write(Pack_Dot)
            find_direction(img)
            Pack_Direction = UserDirectionDataPack(DirectionFlag)
            uart.write(Pack_Direction)


while (True):
    clock.tick()
    img = sensor.snapshot()
    LineCheck(img)
