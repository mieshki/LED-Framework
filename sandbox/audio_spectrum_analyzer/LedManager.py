import socket
import sys
from enum import Enum
import time
import random

# CONFIG
MAX_PACKETS = 255

UDP_IP = "192.168.0.10"
UDP_PORT = 4210

TYPE_HEADER = 0xFE
TYPE_BODY = 0xBB


class Version(Enum):
    TEST = 0
    VERSION1 = 1
    VERSION1_1 = 2


class Type(Enum):
    FULL_FRAME = 0
    LEDS_TO_TURN_ON = 1
    WHOLE_ANIMATION = 2


CURRENT_VERSION = Version.TEST
TYPE = Type.FULL_FRAME


# # # # # # # # # # # # # # # # # # # # # # # # # # #


class LEDFrame:
    rgb = [0] * 768

    def __init__(self):
        self.rgb = [0] * 768

    def fill_all_red(self):
        self.rgb = [0xFF] * 256 + [0x0] * 512

    def fill_all_green(self):
        self.rgb = [0x0] * 256 + [0xFF] * 256 + [0x0] * 256

    def fill_all_blue(self):
        self.rgb = [0x0] * 512 + [0xFF] * 256

    def getTotalSize(self):
        return len(self.rgb)

    def clear(self):
        self.rgb = [0] * 768

    def turnOnLed(self, x, y, z, r, g, b):
        index = int(((64 * z) + (y * 8) + x) / 8)
        position = ((64 * z) + (y * 8) + x) % 8

        # red
        if (r & 0b0001) > 0:
            self.rgb[index] = self.rgb[index] | (1 << position)
        else:
            self.rgb[index] = self.rgb[index] & ~(1 << position)

        if ((r & 0b0010) >> 1) > 0:
            self.rgb[index + 64] = self.rgb[index + 64] | (1 << position)
        else:
            self.rgb[index + 64] = self.rgb[index + 64] & ~(1 << position)

        if ((r & 0b0100) >> 2) > 0:
            self.rgb[index + 128] = self.rgb[index + 128] | (1 << position)
        else:
            self.rgb[index + 128] = self.rgb[index + 128] & ~(1 << position)

        if ((r & 0b1000) >> 3) > 0:
            self.rgb[index + 192] = self.rgb[index + 192] | (1 << position)
        else:
            self.rgb[index + 192] = self.rgb[index + 192] & ~(1 << position)

        # green
        if (g & 0b0001) > 0:
            self.rgb[index + 256] = self.rgb[index + 256] | (1 << position)
        else:
            self.rgb[index + 256] = self.rgb[index + 256] & ~(1 << position)

        if ((g & 0b0010) >> 1) > 0:
            self.rgb[index + 64 + 256] = self.rgb[index + 64 + 256] | (1 << position)
        else:
            self.rgb[index + 64 + 256] = self.rgb[index + 64 + 256] & ~(1 << position)

        if ((g & 0b0100) >> 2) > 0:
            self.rgb[index + 128 + 256] = self.rgb[index + 128 + 256] | (1 << position)
        else:
            self.rgb[index + 128 + 256] = self.rgb[index + 128 + 256] & ~(1 << position)

        if ((g & 0b1000) >> 3) > 0:
            self.rgb[index + 192 + 256] = self.rgb[index + 192 + 256] | (1 << position)
        else:
            self.rgb[index + 192 + 256] = self.rgb[index + 192 + 256] & ~(1 << position)

        # blue
        if (b & 0b0001) > 0:
            self.rgb[index + 512] = self.rgb[index + 512] | (1 << position)
        else:
            self.rgb[index + 512] = self.rgb[index + 512] & ~(1 << position)

        if ((b & 0b0010) >> 1) > 0:
            self.rgb[index + 64 + 512] = self.rgb[index + 64 + 512] | (1 << position)
        else:
            self.rgb[index + 64 + 512] = self.rgb[index + 64 + 512] & ~(1 << position)

        if ((b & 0b0100) >> 2) > 0:
            self.rgb[index + 128 + 512] = self.rgb[index + 128 + 512] | (1 << position)
        else:
            self.rgb[index + 128 + 512] = self.rgb[index + 128 + 512] & ~(1 << position)

        if ((b & 0b1000) >> 3) > 0:
            self.rgb[index + 192 + 512] = self.rgb[index + 192 + 512] | (1 << position)
        else:
            self.rgb[index + 192 + 512] = self.rgb[index + 192 + 512] & ~(1 << position)


    def getData(self, starting_index, length):
        return bytes(self.rgb[starting_index:starting_index + length])

    def updateColumn(self, level, xCord, yCord):
        """ view from top of the matrix. Each 2x2 matrix will map one sound frequency range

                            00 01
                            10 11

           00  10     20  30     40  50     60   70
           01  11     21  31     41  51     61   71

           02  12     22  32     42  52     62   72
           03  13     23  33     43  53     63   73

           04  14     24  34     44  54     64   74
           05  15     25  35     45  55     65   75

           06  16     26  36     46  56     66   76
           07  17     27  37     47  57     67   77

           """

        coordinates = [[xCord * 2, yCord * 2], [xCord * 2 + 1, yCord * 2],
                       [xCord * 2, yCord * 2 + 1], [xCord * 2 + 1, yCord * 2 + 1]]

        for pair in coordinates:
            for zCord in range(0, level):
                self.turnOnLed(pair[0], pair[1], zCord, 15, 0, 0)


class LEDHeader:
    packet_type = bytes([TYPE_HEADER])
    version = 0
    type = 0
    body_size = 0

    def __init__(self, frame_to_send):
        self.type = bytes([Type.FULL_FRAME.value])
        self.version = bytes([Version.VERSION1.value])
        total_size = frame_to_send.getTotalSize()
        self.body_size = bytes([(total_size & 0xFF00) >> 8, total_size & 0xFF])

    def constructPacket(self):
        packet = self.packet_type + self.version + self.type + self.body_size
        print(f'Packet: {packet}')
        return packet


class LEDBody:
    message = bytes([TYPE_BODY])

    def __init__(self, packet_to_send):
        self.message = self.message + packet_to_send

    def constructPacket(self):
        return self.message


def sendHeader(frame_to_send):
    header = LEDHeader(frame_to_send)
    MESSAGE = header.constructPacket()

    print(MESSAGE)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP

    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))


def sendBody(packet_to_send):
    body = LEDBody(packet_to_send)

    MESSAGE = body.constructPacket()
    print(MESSAGE)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP

    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))


def sendBodies(frame_to_send):
    bytes_sent = 0
    bytes_to_send = frame_to_send.getTotalSize()

    while bytes_to_send > 0:
        if bytes_to_send > (MAX_PACKETS - 1):
            packet = frame_to_send.getData(bytes_sent, MAX_PACKETS - 1)
            bytes_sent += MAX_PACKETS - 1
            bytes_to_send -= MAX_PACKETS - 1
        else:
            packet = frame_to_send.getData(bytes_sent, bytes_to_send)
            bytes_sent += bytes_to_send
            bytes_to_send = 0

        sendBody(packet)


def sendFrame(frame_to_send):
    sendHeader(frame_to_send)
    sendBodies(frame_to_send)

    # send header
    # send bodies


def current_milli_time():
    return round(time.time() * 1000)


def color_wheel():
    frame = LEDFrame()
    rr = 1
    gg = 1
    bb = 1
    ranx = 0
    rany = 0
    swiper = 0
    xx = 0
    yy = 0
    zz = 0
    ww = 0

    start = current_milli_time()

    while current_milli_time() - start < 100000:
        swiper = random.randint(0, 3)
        ranx = random.randint(0, 16)
        rany = random.randint(0, 16)

        for xx in range(0, 8):
            for yy in range(0, 8):
                for zz in range(0, 8):
                    frame.turnOnLed(xx, yy, zz, ranx, 0, rany)
            sendFrame(frame)
            time.sleep(0.050)

        ranx = random.randint(0, 16)
        rany = random.randint(0, 16)

        for xx in reversed(range(0, 8)) :
            for yy in range(0, 8):
                for zz in range(0, 8):
                    frame.turnOnLed(xx, yy, zz, ranx, rany, 0)
            sendFrame(frame)
            time.sleep(0.050)

        ranx = random.randint(0, 16)
        rany = random.randint(0, 16)

        for xx in range(0, 8):
            for yy in range(0, 8):
                for zz in range(0, 8):
                    frame.turnOnLed(xx, yy, zz, 0, ranx, rany)
            sendFrame(frame)
            time.sleep(0.050)

        ranx = random.randint(0, 16)
        rany = random.randint(0, 16)
        for xx in reversed(range(0, 8)) :
            for yy in range(0, 8):
                for zz in range(0, 8):
                    frame.turnOnLed(xx, yy, zz, ranx, rany, 0)
            sendFrame(frame)
            time.sleep(0.050)


def brightness_3_colors():
    frame = LEDFrame()
    delay = 0.25

    for brightness in range(0, 16):
        for z in range(0, 8):
            for y in range(0, 8):
                for x in range(0, 8):
                    frame.turnOnLed(x, y, z, brightness, 0, 0)
        sendFrame(frame)
        time.sleep(delay)

    for brightness in range(0, 16):
        for z in range(0, 8):
            for y in range(0, 8):
                for x in range(0, 8):
                    frame.turnOnLed(x, y, z, 0, brightness, 0)
        sendFrame(frame)
        time.sleep(delay)

    for brightness in range(0, 16):
        for z in range(0, 8):
            for y in range(0, 8):
                for x in range(0, 8):
                    frame.turnOnLed(x, y, z, 0, 0, brightness)
        sendFrame(frame)
        time.sleep(delay)


if __name__ == '__main__':
    color_wheel()
    brightness_3_colors()