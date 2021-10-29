# ************************************ @Mardy Bum2021 ***********************************#
# 代码仅供参考，不可运行。
# 2021/7/30更新：修复QRCode类使用不规范。增加新的功能AprilTag实现标记追踪。修改颜色追踪阈值以及部分代码逻辑
# 2021/8/1更新：增加单模板/多模板匹配，特征点匹配。
import sensor, image, time, math, mjpeg, cmath, pyb
from pyb import UART

sensor.reset()
sensor.set_pixformat(sensor.RGB565)  # 设置相机模块的像素模式
sensor.set_framesize(sensor.QQVGA)  # 识别二维码需要VGA或者QVGA
sensor.skip_frames(time=3000)  # 时钟
sensor.set_auto_whitebal(False)  # 若想追踪颜色则关闭白平衡
clock = time.clock()  # 初始化时钟
uart = UART(3, 500000)
uart.init(500000)
# ==============================================LED控制==============================================
led = pyb.LED(3)  # Red LED = 1, Green LED = 2, Blue LED = 3, IR LEDs = 4.
# led.on()            #亮灯
# led.off()
# time.sleep_ms(150)     #延时150ms

# ==============================================Vedio录像============================================
Video_Start_Flag = bytearray([0XAA, 0XAA])
Video_Stop_Flag = bytearray([0XAA, 0XBB])
Photo_State = 0
# m = mjpeg.Mjpeg("example.mjpeg")
# clock.tick()
# m.add_frame(img)
# m.close(clock.fps())
# ===============================================Dot交点=============================================


def UserDotDataPack(flag, X, Y):
    Temp_X = int(X)
    Temp_Y = int(Y)

    Cross_data = bytearray(
        [0xAA, 0x31, flag, Temp_X >> 8, Temp_X, Temp_Y >> 8, Temp_Y, 0xFF])
    return Cross_data


# ===============================================turn转向============================================
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


def find_direction(img):  # 判断向左转或向右转
    global ROISForLines
    global DirectionFlag
    roi_blobs_result = {}  # 在各个ROI中寻找色块的结果记录
    for roi_direct in ROISForLines.keys():  # 数值复位
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

        if not (width >= 3 and width <= 45 and height >= 3 and height <= 45):
            # 根据色块的长宽进行过滤
            continue
        roi_blobs_result[roi_direct]['cx'] = largest_blob.cx()
        roi_blobs_result[roi_direct]['cy'] = largest_blob.cy()
        roi_blobs_result[roi_direct]['blob_flag'] = True
        img.draw_rectangle((x, y, width, height), color=(0, 255, 255))
    # 判断是否需要左转与右转
    DirectionFlag = 0
    if (not roi_blobs_result['up']['blob_flag']
        ) and roi_blobs_result['down']['blob_flag'] and roi_blobs_result[
            'left']['blob_flag'] != roi_blobs_result['right']['blob_flag']:
        if roi_blobs_result['left']['blob_flag']:
            DirectionFlag = 1  #左转
        if roi_blobs_result['right']['blob_flag']:
            DirectionFlag = 2  #右转
    return None


#=========================================Line直线===================================================


def UserLineDataPack(flag, Angle, Distance):
    Temp_Angle = int(Angle)
    Temp_Distance = int(Distance)
    Line_data = bytearray([
        0xAA, 0x29, flag, Temp_Angle >> 8, Temp_Angle, Temp_Distance >> 8,
        Temp_Distance, 0xFF
    ])
    return Line_data


def Line_Theta(Line):  # 与Y轴夹角
    if Line.y2() == Line.y1():
        return 90
    angle = math.atan(
        (Line.x1() - Line.x2()) / (Line.y2() - Line.y1())) * 180 / math.pi
    return angle


def Line_Distance(Line):  # 直线中点到到图像中点距离
    return (Line.x1() + Line.x2()) / 2 - 80


def CalculateIntersection(line1, line2):  # 计算交点，以图像中点为原点
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


def LineCheck(img):  # 前进方向巡线，发送角度最小的直线的角度距离，如果有交点以及转向也同时发送
    Lines = img.find_lines(threshold=1200, theta_margin=25, rho_margin=25)
    Len_Lines = len(Lines)
    Min_angle = 180

    if Len_Lines == 0:  # 没有直线
        Pack_Line = UserLineDataPack(0, 0, 0)
        uart.write(Pack_Line)
        Pack_Dot = UserDotDataPack(0, 0, 0)
        uart.write(Pack_Dot)
    else:
        Temp_Line = Lines[0]
        for line in Lines:
            if abs(Line_Theta(line)) < Min_angle:  # 找出角度最小的直线
                Temp_Line = line
                Min_angle = abs(Line_Theta(line))
        if (abs(Line_Theta(Temp_Line))) > 30:  # 如果角度最小的直线仍大于30°，滤除
            Pack_Line = UserLineDataPack(0, 0, 0)
            uart.write(Pack_Line)
        else:  #发送角度最小的线
            Pack_Line = UserLineDataPack(1, Line_Theta(Temp_Line),
                                         Line_Distance(Temp_Line))
            uart.write(Pack_Line)
            img.draw_line(Temp_Line.line(), color=(255, 0, 0))
        if (Len_Lines == 2):  #有两条直线，也发送交点坐标,或判断转向
            x, y = CalculateIntersection(Lines[0], Lines[1])
            if (x < img.width() / 2 and x > -(img.width() / 2)
                    and y < img.height() / 2
                    and y > -(img.height() / 2)):  #判断交点是否在图像内
                Pack_Dot = UserDotDataPack(1, x, y)
                uart.write(Pack_Dot)
                img.draw_cross(int(x + img.width() / 2),
                               int(img.height() / 2 - y),
                               color=[255, 0, 0])
            else:
                Pack_Dot = UserDotDataPack(0, 0, 0)
                uart.write(Pack_Dot)
            find_direction(img)
            Pack_Direction = UserDirectionDataPack(DirectionFlag)
            uart.write(Pack_Direction)


# ==============================================Circle==============================================
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
            Pack_Circle = UserCircleDataPack(1,
                                             Circles[0].x() - img.width() / 2,
                                             img.height() / 2 - Circles[0].y())
            uart.write(Pack_Circle)


# ============================================QRcode=================================================
QR_State = 0
QR_Start_Flag = bytearray([0XAA, 0XCC])
QR_Stop_Flag = bytearray([0XAA, 0XDD])


def UserQRCodePack(Flag, Message, X, Y):  # X,Y指的是二维码的坐标
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


# ==========================================Barcode条形码=============================================
# 需要测试
# sensor.set_auto_gain(False)
# sensor.set_auto_whitebal(False)
# sensor.set_windowing((640, 80)) 条形码检测需要更高的分辨率才能正常工作，因此应始终以640x480的灰度运行


def barcode_name(code):
    if (code.type() == image.EAN2):
        return "EAN2"
    if (code.type() == image.EAN5):
        return "EAN5"
    if (code.type() == image.EAN8):
        return "EAN8"
    if (code.type() == image.UPCE):
        return "UPCE"
    if (code.type() == image.ISBN10):
        return "ISBN10"
    if (code.type() == image.UPCA):
        return "UPCA"
    if (code.type() == image.EAN13):
        return "EAN13"
    if (code.type() == image.ISBN13):
        return "ISBN13"
    if (code.type() == image.I25):
        return "I25"
    if (code.type() == image.DATABAR):
        return "DATABAR"
    if (code.type() == image.DATABAR_EXP):
        return "DATABAR_EXP"
    if (code.type() == image.CODABAR):
        return "CODABAR"
    if (code.type() == image.CODE39):
        return "CODE39"
    if (code.type() == image.PDF417):
        return "PDF417"
    if (code.type() == image.CODE93):
        return "CODE93"
    if (code.type() == image.CODE128):
        return "CODE128"
    # 以下代码放入主函数
    # codes = img.find_barcodes()
    # for code in codes:
    # img.draw_rectangle(code.rect())
    # print_args = (barcode_name(code), code.payload(), (180 * code.rotation()) / math.pi, code.quality(), clock.fps())
    # print("Barcode %s, Payload \"%s\", rotation %f (degrees), quality %d, FPS %f" % print_args)
    # if not codes:
    # print("FPS %f" % clock.fps())


# ============================================二维码拍照存储=====================================
QRimages_num = 0  # 最好是if QRcode.QRcodemessage==1之后再调用shot images


def Shot_images():
    global QRimages_num
    if QRcode.QRcodemessage == 1:
        if QRimages_num <= 2:
            QRimages_num += 1
            QRimages_name = "QRcode_" + str(QRimages_num)
            sensor.snapshot().save(QRimages_name + ".jpg")
        else:
            QRimages_num = 0
    return None


# ==============================================颜色识别===============================================
# sensor.set_contrast(1)  #设置相机图像对比度。-3至+3
# sensor.set_gainceiling(16)  #设置相机图像增益上限。2, 4, 8, 16, 32, 64, 128。
def UserColorPack(Flag, Color, X, Y):
    TempX = int(X)
    TempY = int(Y)
    Color_data = bytearray(
        [0xAA, 0x33, Flag, Color, TempX >> 8, TempX, TempY >> 8, TempY, 0xFF])
    return Color_data


class Recognition(object):
    flag = 0
    color = 0
    cx = 0
    cy = 0


Recognition = Recognition()
# 红色阈值
red_threshold = (10, 91, 10, 127, -60, 96)
# 绿色阈值
green_threshold = ((3, 100, -83, -19, -2, 110))
# 蓝色阈值
blue_threshold = (40, 97, -68, 26, -64, -27)

# 颜色1: 红色的颜色代码
red_color_code = 1
# 颜色2: 绿色的颜色代码
green_color_code = 2
# 颜色3：蓝色的颜色代码
blue_color_code = 4
# 多颜色混合只需要把数值相加
# 如  blob.code() == 3: # r/g code


def FindMax(blobs):  # 找最大的色块
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
    blobs = img.find_blobs([red_threshold, green_threshold, blue_threshold],
                           area_threshold=500)
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
            Recognition.cx = center_x - img.width() / 2
            Recognition.cy = img.height() / 2 - center_y
        elif color_code == green_color_code:
            img.draw_string(x, y - 10, "green", color=(0x00, 0xFF, 0x00))
            Recognition.flag = 1
            Recognition.color = 2
            Recognition.cx = center_x - img.width() / 2
            Recognition.cy = img.height() / 2 - center_y
        elif color_code == blue_color_code:
            img.draw_string(x, y - 10, "blue", color=(0x00, 0x00, 0xFF))
            Recognition.flag = 1
            Recognition.color = 3
            Recognition.cx = center_x - img.width() / 2
            Recognition.cy = img.height() / 2 - center_y
        else:
            Recognition.flag = 0
            Recognition.color = 0
            Recognition.cx = 0
            Recognition.cy = 0
        Colorpack = UserColorPack(Recognition.flag, Recognition.color,
                                  Recognition.cx, Recognition.cy)
        uart.write(Colorpack)
        #用矩形标记出目标颜色区域
        img.draw_rectangle([x, y, width, height])
        #在目标颜色区域的中心画十字形标记
        img.draw_cross(center_x, center_y)


#=============================================识别矩形框=============================================
Rectangle_State_Counter = 0


def UserRectangleDataPack(flag, X, Y):
    Temp_X = int(X)
    Temp_Y = int(Y)
    Rectangle_data = bytearray(
        [0xAA, 0x34, flag, Temp_X >> 8, Temp_X, Temp_Y >> 8, Temp_Y, 0xFF])
    return Rectangle_data


def Rectanglecheck(img):
    global Rectangle_State_Counter
    Rectangles = img.find_rects(threshold=20000)
    Len_Rectangles = len(Rectangles)

    if Len_Rectangles == 0:
        Rectangle_State_Counter = 0
        Pack_Rectangles = UserRectangleDataPack(0, 0, 0)
        uart.write(Pack_Rectangles)
    else:
        Pack_Rectangle = UserRectangleDataPack(
            1, Rectangles[0].x() + Rectangles[0].w() / 2 - img.width() / 2,
            img.height() / 2 - Rectangles[0].y() - Rectangles[0].h() / 2)
        img.draw_rectangle(Rectangles[0].rect(), color=(255, 0, 0))
        uart.write(Pack_Rectangle)


#=========================================识别AprilTag==============================================
# apriltag标签代码最多支持6个可以同时处理的标签族。
# 返回的标签对象将在标签系列中具有其标签系列和标识。
tag_families = 0
tag_families |= image.TAG16H5  # comment out to disable this family
tag_families |= image.TAG25H7  # comment out to disable this family
tag_families |= image.TAG25H9  # comment out to disable this family
tag_families |= image.TAG36H10  # comment out to disable this family
tag_families |= image.TAG36H11  # comment out to disable this family (default family)
tag_families |= image.ARTOOLKIT  # comment out to disable this family

#标签系列有什么区别？ 那么，例如，TAG16H5家族实际上是一个4x4的方形标签。
#所以，这意味着可以看到比6x6的TAG36H11标签更长的距离。 然而，较低的H值（H5对H11）
#意味着4x4标签的假阳性率远高于6x6标签。 所以，除非你有理由使用其他标签系列，
#否则使用默认族TAG36H11。


def family_name(tag):
    if (tag.family() == image.TAG16H5):
        return "TAG16H5"
    if (tag.family() == image.TAG25H7):
        return "TAG25H7"
    if (tag.family() == image.TAG25H9):
        return "TAG25H9"
    if (tag.family() == image.TAG36H10):
        return "TAG36H10"
    if (tag.family() == image.TAG36H11):
        return "TAG36H11"
    if (tag.family() == image.ARTOOLKIT):
        return "ARTOOLKIT"


class AprilTag(object):
    AprilTag_Flag = 0
    AprilTag_x = 0
    AprilTag_y = 0
    AprilTag_z = 0


def UserAprilTagPack(Flag, X, Y, Z):  #X,Y指的是二维码的坐标
    TempX = int(X)
    TempY = int(Y)
    TempZ = int(Z)
    AprilTag_data = bytearray([
        0xAA, 0x35, Flag, TempX >> 8, TempX, TempY >> 8, TempY, TempZ >> 8,
        TempZ, 0xFF
    ])
    return AprilTag_data


AprilTag = AprilTag()


def ScanAprilTag(img):
    AprilTags = img.find_apriltags(families=tag_families)
    Len_AprilTags = len(AprilTags)
    if Len_AprilTags == 0:
        AprilTag.AprilTag_Flag = 0
        AprilTag.AprilTag_x = 0
        AprilTag.AprilTag_y = 0
        AprilTag.AprilTag_z = 0
    else:
        img.draw_rectangle(AprilTags[0].rect(), color=(255, 0, 0))
        AprilTag.AprilTag_Flag = 1
        AprilTag.AprilTag_x = AprilTags[0].cx(
        ) - img.width() / 2  #二维码中心点的坐标，以图像中心为原点
        AprilTag.AprilTag_y = img.height() / 2 - AprilTags[0].cy()
        AprilTag.AprilTag_z = -(AprilTags[0].z_translation())
        print("识别到AprilTag", "FLAG", AprilTag.AprilTag_Flag, "x",
              AprilTag.AprilTag_x, "y", AprilTag.AprilTag_y, "z",
              AprilTag.AprilTag_z)
        AprilTagPack = UserAprilTagPack(AprilTag.AprilTag_Flag,
                                        AprilTag.AprilTag_x,
                                        AprilTag.AprilTag_y,
                                        AprilTag.AprilTag_z)
        uart.write(AprilTagPack)
    return None


# =============================================模板匹配===============================================
# 一般不会用到，条件比较苛刻要求摄像头静止
# 一定要从不同角度和大小多拍照
# 拍照也要用灰度的图片。
sensor.set_contrast(1)
sensor.set_gainceiling(16)
sensor.set_framesize(sensor.QQVGA)
# sensor.set_windowing(((640-80)//2, (480-60)//2, 80, 60))
sensor.set_pixformat(sensor.GRAYSCALE)
# 使用其他格式可能会导致内存不够

# 单模板使用以下代码
template = image.Image("/pic2.pgm")

r = img.find_template(template, 0.70, step=4,
                      search=SEARCH_EX)  #, roi=(10, 0, 60, 60))
if r:
    img.draw_rectangle(r)

#多模板使用以下代码
templates = ["/0.pgm", "/1.pgm", "/2.pgm", "/6.pgm"]  #保存多个模板
for t in templates:
    template = image.Image(t)
    r = img.find_template(template, 0.70, step=4,
                          search=SEARCH_EX)  #, roi=(10, 0, 60, 60))
    if r:
        img.draw_rectangle(r)
        print(t)
#=============================================特征点识别==============================================
#不要求大小和角度，比模板匹配适用范围更广，缺点是只能识别一种特征点，如果有多个特征需要匹配还是使用模板

sensor.set_contrast(3)
sensor.set_gainceiling(16)
sensor.set_framesize(sensor.VGA)
sensor.set_windowing((320, 240))
sensor.set_pixformat(sensor.GRAYSCALE)

sensor.skip_frames(time=2000)
sensor.set_auto_gain(False, value=100)


def draw_keypoints(img, kpts):
    if kpts:
        print(kpts)
        img.draw_keypoints(kpts)
        img = sensor.snapshot()
        time.sleep_ms(1000)


kpts1 = None
# kpts1保存目标物体的特征，可以从文件导入特征，但是不建议这么做。
# 从文件导入的话kpts1 = image.load_descriptor("/desc.orb")

if (kpts1 == None):  #第一次运行，提取特征点
    kpts1 = img.find_keypoints(max_keypoints=150,
                               threshold=25,
                               scale_factor=1.2)
    draw_keypoints(img, kpts1)
else:  #不是第一次运行或者从文件导入了特征点
    kpts2 = img.find_keypoints(max_keypoints=150,
                               threshold=25,
                               normalized=True)
    if (kpts2):
        match = image.match_descriptor(kpts1, kpts2, threshold=85)
        print(match.count())
        if (match.count() > 2):  #这个地方的值可以根据上面打印的数据来确定
            img.draw_rectangle(match.rect())
            img.draw_cross(match.cx(), match.cy(), size=10)

#==============================================main=================================================

while (True):
    img = sensor.snapshot()
    img.lens_corr(1.8)
    if uart.any():
        a = uart.read()
        if a == Video_Start_Flag:
            Photo_State = 1
        if a == Video_Stop_Flag:
            Photo_State = 2
    if Photo_State == 1:
        m = mjpeg.Mjpeg("example.mjpeg")
        clock.tick()
        m.add_frame(img)
    if Photo_State == 2:
        m.close(clock.fps())
        Photo_State = 0
    Circlecheck(img)
    LineCheck(img)
    ScanQRcode(img)
    ColorRecognition(img)
    ScanAprilTag(img)
