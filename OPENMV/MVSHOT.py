# 您可以使用OpenMV Cam来录制mjpeg文件。 您可以为记录器对象提供JPEG帧
# 或RGB565 /灰度帧。 一旦你完成了一个Mjpeg文件的录制，你可以使用VLC
# 来播放它。 如果你在Ubuntu上，那么内置的视频播放器也可以工作。
# AA AA ->START
# AA BB ->STOP
import sensor, image, time, mjpeg, pyb
from pyb import UART

uart = UART(3, 115200)  # i使用给定波特率初始化
mystart = bytearray([0XAA, 0XAA])
mystop = bytearray([0XAA, 0XBB])
print(mystart)
print(mystop)
RED_LED_PIN = 1
BLUE_LED_PIN = 3
von = 0
enable_lens_corr = False  # turn on for straighter lines...

sensor.reset()  # 初始化sensor

sensor.set_pixformat(sensor.RGB565)  # or sensor.GRAYSCALE
# 设置图像色彩格式，有RGB565色彩图和GRAYSCALE灰度图两种

sensor.set_framesize(sensor.QVGA)  # or sensor.QQVGA (or others)
# 设置图像像素大小

sensor.skip_frames(time=2000)  # 让新的设置生效
clock = time.clock()  # 跟踪FPS帧率

pyb.LED(RED_LED_PIN).on()
sensor.skip_frames(30)  # 给用户一个时间来准备

pyb.LED(RED_LED_PIN).off()
pyb.LED(BLUE_LED_PIN).on()

m = mjpeg.Mjpeg("example3.mjpeg"
                )  #mjpeg.Mjpeg(filename, width=Auto, height=Auto)创建一个mjpeg对象，
#filename为保存mjpeg动图的文件路径

while 1:
    if uart.any():
        a = uart.read()
        print(a)
        if a == mystart:
            von = 1
        if a == mystop:
            von = 2
    if von == 1:
        print("You're on camera!")
        clock.tick()
        m.add_frame(sensor.snapshot()
                    )  #mjpeg.add_frame(image, quality=50)，向mjpeg视频中中添加图片，
        print(clock.fps())  #quality为视频压缩质量。
    if von == 2:
        break

m.close(clock.fps())
pyb.LED(BLUE_LED_PIN).off()
print("Done! Reset the camera to see the saved recording.")
