import time
import random
from colorsys import hsv_to_rgb
import board
from digitalio import DigitalInOut, Direction
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789
from setting import Joystick
import numpy as np

joystick = Joystick()
RABBIT_RUNNING=[Image.open("/home/choisuyeon/ESW/frame_rabbit_running/rabbit_running_1.png").resize((60,60)),
         Image.open("/home/choisuyeon/ESW/frame_rabbit_running/rabbit_running_2.png").resize((60,60)),
         Image.open("/home/choisuyeon/ESW/frame_rabbit_running/rabbit_running_3.png").resize((60,60)),
         Image.open("/home/choisuyeon/ESW/frame_rabbit_running/rabbit_running_4.png").resize((60,60)),
         Image.open("/home/choisuyeon/ESW/frame_rabbit_running/rabbit_running_5.png").resize((60,60))]

screen = Image.new("RGBA", (joystick.width, joystick.height), (255, 255, 255, 0))

screen.paste(RABBIT_RUNNING[0],(0,180),RABBIT_RUNNING[0])
joystick.disp.image(screen)