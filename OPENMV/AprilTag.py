# AprilTags 标记追踪例程
#
# 这个例子展示了OpenMV Cam的功能，可以检测OpenMV Cam M7上的April标签。 M4版本无法检测april标签。

import sensor, image, time, math
from pyb import UART

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.VGA)  # 如果分辨率太高，内存可能会溢出…
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)  # 必须关闭此功能，以防止图像冲洗…
sensor.set_auto_whitebal(False)  # 必须关闭此功能，以防止图像冲洗…
clock = time.clock()
uart = UART(3, 500000)
uart.init(500000)
# 注意！与find_qrcodes不同，find_apriltags方法不需要对镜像进行镜头校正。

QR_State = 0
QR_Start_Flag = bytearray([0XAA, 0XCC])
QR_Stop_Flag = bytearray([0XAA, 0XDD])


def UserQRCodePack(Flag, Message, X, Y):  #X,Y指的是二维码的坐标
    TempX = int(X)
    TempY = int(Y)

    QR_data = bytearray([
        0xAA, 0x32, Flag, Message, TempX >> 8, TempX, TempY >> 8, TempY, 0xFF
    ])
    return QR_data


class QRcode(object):

    QRcode_Flag = 0
    QRcode_x = 0
    QRcode_y = 0
    QRMessage = 0


QRcode = QRcode()


def ScanQRcode(img):
    QRCodes = img.find_qrcodes()
    Len_QRCodes = len(QRCodes)
    if Len_QRCodes == 0:
        QRcode.QRcode_Flag = 0
        QRcode.QRcode_x = 0
        QRcode.QRcode_y = 0
        QRcode.QRMessage = 0
    else:
        img.draw_rectangle(QRCodes[0].rect(), color=255)
        QRcode.QRcode_Flag = 1
        QRcode.QRcode_x = QRCodes[0].x(
        ) + QRCodes[0].w() / 2 - img.width() / 2  #二维码中心点的坐标，以图像中心为原点
        QRcode.QRcode_y = img.height() / 2 - (QRCodes[0].y() +
                                              QRCodes[0].h() / 2)

        print('二维码信息', QRCodes[0].payload(), QRcode.QRcode_x, QRcode.QRcode_y)
        if QRCodes[0].payload() == "5":
            QRcode.QRMessage = 0x05
        if QRCodes[0].payload() == "6":
            QRcode.QRMessage = 0x06
        if QRCodes[0].payload() == "7":
            QRcode.QRMessage = 0x07
        if QRCodes[0].payload() == "8":
            QRcode.QRMessage = 0x08
        if QRCodes[0].payload() == "9":
            QRcode.QRMessage = 0x09
        if QRCodes[0].payload() == "10":
            QRcode.QRMessage = 0x0A
        if QRCodes[0].payload() == "向右高度60":
            QRcode.QRMessage = 0x3C
        if QRCodes[0].payload() == "向左高度70":
            QRcode.QRMessage = 0x46
    Messagepack = UserQRCodePack(QRcode.QRcode_Flag, QRcode.QRMessage,
                                 QRcode.QRcode_x, QRcode.QRcode_y)
    uart.write(Messagepack)
    return None


while (True):
    clock.tick()
    img = sensor.snapshot()
    ScanQRcode(img)
