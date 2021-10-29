# Untitled - By: ghfjd - 周一 7月 19 2021
#有舵机控制
import sensor, image, time, mjpeg, pyb
from pyb import UART

Redled = pyb.LED(1)
Greenled = pyb.LED(2)
Blueled = pyb.LED(3)

#==============================================Video================================================
Video_Start_Flag = bytearray([0XAA, 0XAA])
Video_Stop_Flag = bytearray([0XAA, 0XBB])
Photo_State = 0

#==============================================Servo================================================
Servo_Reset = bytearray([0XAA, 0X11])

s1 = pyb.Servo(1)  #在P7引脚创建servo对象
s2 = pyb.Servo(2)  #在P8引脚创建servo对象
#或者s2 = pyb.Servo(2)
#s1.angle(45,1500)
# =============================================QRcode===============================================
QR_State = 0
QR_Groundcounter = 0
QR_Start_Flag = bytearray([0XAA, 0XCC])
QR_Stop_Flag = bytearray([0XAA, 0XDD])


def UserQRCodePack(Flag, Message):
    #TempX = int(X)
    #TempY = int(Y)

    QR_data = bytearray([0xAA, 0x32, Flag, Message, 0xFF])
    return QR_data


class QRcode(object):
    QRcodemessage = 0


QRcode = QRcode()


def ScanQRcode(img):
    global QR_Groundcounter
    Sendtimes = 1
    QRCodes = img.find_qrcodes()
    Len_QRCodes = len(QRCodes)
    if Len_QRCodes == 0:
        QRcode.QRcodemessage = 0
        QRMessage = 0
    else:
        img.draw_rectangle(QRCodes[0].rect(), color=255)
        QRcode.QRcodemessage = 1
        #QRcode_x=QRCodes[0].x()+QRCodes[0].w()/2-img.width()/2       #二维码中心点的坐标，以图像中心为原点
        #QRcode_y=img.height()/2-(QRCodes[0].y()+QRCodes[0].h()/2)
        print('二维码信息', QRCodes[0].payload())
        if QRCodes[0].payload() == "5":
            QRMessage = 0x05
            #s2.angle(100,1500)
        if QRCodes[0].payload() == "6":
            QRMessage = 0x06
            #s2.angle(100,1500)
        if QRCodes[0].payload() == "7":
            QRMessage = 0x07
            #s2.angle(100,1500)
        if QRCodes[0].payload() == "8":
            QRMessage = 0x08
            #s2.angle(100,1500)
        if QRCodes[0].payload() == "9":
            QRMessage = 0x09
            #s2.angle(100,1500)
        if QRCodes[0].payload() == "10":
            QRMessage = 0x0A
            #s2.angle(100,1500)
        if QRCodes[0].payload() == "向右高度60":
            QRMessage = 0x3C
            #s2.angle(-10,1500)
        if QRCodes[0].payload() == "向左高度70":
            QRMessage = 0x46
            #s2.angle(-10,1500)
        if QR_Groundcounter == Sendtimes:
            if QRMessage == 0x3C or QRMessage == 0x46:
                s2.angle(-10, 1500)
            else:
                s2.angle(100, 1500)
            QR_Groundcounter = 0
        if QR_Groundcounter < Sendtimes:
            QR_Groundcounter = QR_Groundcounter + 1
        Messagepack = UserQRCodePack(QRcode.QRcodemessage, QRMessage)
        uart.write(Messagepack)
        uart.write(Messagepack)
        uart.write(Messagepack)
        uart.write(Messagepack)
        uart.write(Messagepack)
        uart.write(Messagepack)
        uart.write(Messagepack)
        uart.write(Messagepack)
        uart.write(Messagepack)
        uart.write(Messagepack)
        uart.write(Messagepack)
    Messagepack = UserQRCodePack(QRcode.QRcodemessage, QRMessage)
    uart.write(Messagepack)
    return None


#==================================QRcodeEnd===================================
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.VGA)
sensor.skip_frames(time=2000)
uart = UART(3, 500000)
uart.init(500000)  #记得改！！！！！！！！！！！！！！！！
clock = time.clock()
s1.angle(-7, 1500)
s2.angle(-10, 1500)
Redled.on()
Greenled.on()
Blueled.on()  #亮灯
while (True):
    clock.tick()
    #img = sensor.snapshot().lens_corr(1.8)
    #img.binary([(54, 255)])
    img = sensor.snapshot()
    if uart.any():
        a = uart.read()
        if a == Servo_Reset:
            s1.angle(-7, 1000)
            QR_Groundcounter = 0
        #if a == Video_Start_Flag
        #Photo_State = 1
        #m = mjpeg.Mjpeg("Video_Openmv2.mjpeg")
        #if a == Video_Stop_Flag:
        #Photo_State = 2
    #if Photo_State == 1:
    #clock.tick()
    #m.add_frame(img, quality=70)
    #elif Photo_State == 2:
    #m.close(clock.fps())
    #Photo_State = 0
    ScanQRcode(img)
