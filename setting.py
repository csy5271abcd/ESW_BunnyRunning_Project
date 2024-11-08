import time
import random
from colorsys import hsv_to_rgb
import board
from digitalio import DigitalInOut, Direction
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789


class Joystick:
    def __init__(self):
        self.cs_pin = DigitalInOut(board.CE0)
        self.dc_pin = DigitalInOut(board.D25)
        self.reset_pin = DigitalInOut(board.D24)
        self.BAUDRATE = 24000000

        self.spi = board.SPI()
        self.disp = st7789.ST7789(
                    self.spi,
                    height=240,
                    y_offset=80,
                    rotation=180,
                    cs=self.cs_pin,
                    dc=self.dc_pin,
                    rst=self.reset_pin,
                    baudrate=self.BAUDRATE,
                    )

        # Input pins:
        self.button_A = DigitalInOut(board.D5)
        self.button_A.direction = Direction.INPUT

        self.button_B = DigitalInOut(board.D6)
        self.button_B.direction = Direction.INPUT

        self.button_L = DigitalInOut(board.D27)
        self.button_L.direction = Direction.INPUT

        self.button_R = DigitalInOut(board.D23)
        self.button_R.direction = Direction.INPUT

        self.button_U = DigitalInOut(board.D17)
        self.button_U.direction = Direction.INPUT

        self.button_D = DigitalInOut(board.D22)
        self.button_D.direction = Direction.INPUT

        self.button_C = DigitalInOut(board.D4)
        self.button_C.direction = Direction.INPUT

        # Turn on the Backlight
        self.backlight = DigitalInOut(board.D26)
        self.backlight.switch_to_output()
        self.backlight.value = True

        # Create blank image for drawing.
        # Make sure to create image with mode 'RGB' for color.
        self.width = self.disp.width
        self.height = self.disp.height



joystick = Joystick()

my_image = Image.new("RGB", (joystick.width, joystick.height))
my_draw = ImageDraw.Draw(my_image)

"""my_draw.rectangle((0, 0, joystick.width, joystick.height), fill = (135, 206, 235,100))
#좌표는 동그라미의 왼쪽 위, 오른쪽 아래 점 (x1, y1, x2, y2)
joystick.disp.image(my_image)
"""

background = Image.new("RGBA", (joystick.width, joystick.height), (255, 255,255, 100))  # 배경 이미지 생성
foreground = Image.open('/home/choisuyeon/ESW/background.png').resize((240,220)) # 앞쪽 이미지 불러오기

# (100, 150) 위치에 앞쪽 이미지를 배경 이미지에 붙여넣기
background.paste(foreground, (0, 0), foreground)  # 세 번째 인자는 투명도 적용
joystick.disp.image(background)

rabbit_image = Image.open("/home/choisuyeon/ESW/frame_rabbit_running/rabbit_running_1.png").resize((60,60)) # 디스플레이 크기에 맞는 이미지 생성
background.paste(rabbit_image, (0, 170), rabbit_image)  
joystick.disp.image(background)

star_image = Image.open("/home/choisuyeon/ESW/star.png").resize((30,30)) # 디스플레이 크기에 맞는 이미지 생성
background.paste(star_image, (45, 120), star_image)  
joystick.disp.image(background)



