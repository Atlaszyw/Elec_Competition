# Note: Line detection is done by using the Hough Transform:

import sensor, image, time
import cmath
import math
from pyb import UART

enable_lens_corr = False  # turn on for straighter lines...


def UserLineDataPack(flag, angle, distance):
    line_data = bytearray(
        [0xAA, 0x29, flag, angle >> 8, angle, distance >> 8, distance, 0xFF])
    return line_data


def UserCircleDataPack(flag, Theta, Rho):
    Circle_data = bytearray([0xAA, 0x30, flag, Theta >> 8, Theta, Rho, 0xFF])
    return Circle_data


sensor.reset()
sensor.set_pixformat(sensor.RGB565)  # grayscale is faster
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time=2000)
clock = time.clock()
uart = UART(3, 500000)
uart.init(500000)

while (True):
    clock.tick()
    img = sensor.snapshot()
    if enable_lens_corr: img.lens_corr(1.8)  # for 2.8mm lens...
    """
    `threshold` controls how many lines in the image are found. Only lines with
    edge difference magnitude sums greater than `threshold` are detected...

    More about `threshold` - each pixel in the image contributes a magnitude value
    to a line. The sum of all contributions is the magintude for that line. Then
    when lines are merged their magnitudes are added togheter. Note that `threshold`
    filters out lines with low magnitudes before merging. To see the magnitude of
    un-merged lines set `theta_margin` and `rho_margin` to 0...

    `theta_margin` and `rho_margin` control merging similar lines. If two lines
    theta and rho value differences are less than the margins then they are merged.
    """
    Circles = img.find_circles(threshold=4000,
                               x_margin=5,
                               y_margin=5,
                               r_margin=30)

    Len_Circles = len(Circles)

    if Len_Circles == 0:
        Pack_Circle = UserCircleDataPack(0, 0, 0)
    else:
        # print(Circles)
        z = complex(Circles[0].x() - img.width() / 2,
                    img.height() / 2 - Circles[0].y())
        # print(z)x
        Rho, Theta = cmath.polar(z)
        Theta = Theta * 180 / cmath.pi
        # print(Rho, Theta)
        if Theta <= 90:
            Theta = -Theta + 90
        else:
            Theta = -Theta + 450
        print(Theta, Rho)
        Pack_Circle = UserCircleDataPack(1, int(Theta), int(Rho))

        img.draw_circle(Circles[0].x(),
                        Circles[0].y(),
                        Circles[0].r(),
                        color=(255, 0, 0))
    uart.write(Pack_Circle)

    Lines = img.find_lines(threshold=1000, theta_margin=25, rho_margin=25)
    Len_Lines = len(Lines)
    if Len_Lines == 0:
        Line_Pack = UserLineDataPack(0, 0, 0)
    else:

        Line_Temp = Lines[0]
        # Theta_Temp = 90
        #print(Lines[0])
        if (int(Lines[0].x2()) < 120) and (int(Lines[0].x2()) > 40):
            if (int(Lines[0].x1()) < 120) and (int(Lines[0].x1()) > 40):
                if Lines[0].y2() != Lines[0].y1():
                    ang = math.atan(
                        (Lines[0].x2() - Lines[0].x1()) /
                        (Lines[0].y2() - Lines[0].y1())) * 180 / cmath.pi
                    ang2 = math.atan((img.width() / 2 - Lines[0].x1()) /
                                     60) * 180 / cmath.pi
                    #dev=math.sqrt(((Lines[0].x1()+Lines[0].x2())/2-img.width() / 2)**2+((Lines[0].y1()+Lines[0].y2())/2-img.height() / 2)**2)
                    print(ang, ang2)
                    # for line in Lines:
                    #     if line.theta() > 90:
                    #         theta_err = line.theta() - 180
                    #     else:
                    #         theta_err = line.theta()
                    #     if abs(theta_err) < Theta_Temp:
                    #         Line_Temp = line
                    #         Theta_Temp = theta_err

                    # rho_err = abs(Line_Temp.rho()) - img.width() / 2
                    img.draw_line(Line_Temp.line(), color=(255, 0, 0))
        # print(int(Theta_Temp), int(rho_err))
        # Pack_Line = UserLineDataPack(1, int(Theta_Temp), int(rho_err))

    # uart.write(Pack_Line)
