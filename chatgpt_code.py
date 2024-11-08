import time
import random
from colorsys import hsv_to_rgb
import board
from digitalio import DigitalInOut, Direction
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789
from setting import Joystick
import numpy as np

class Rabbit:
    def __init__(self, width, height):
        self.position = np.array([width / 4, height - 100])  # 초기 위치 설정
        self.width = width
        self.height = height
        self.run_images = [
            Image.open('/home/choisuyeon/ESW/frame_rabbit_running/rabbit_running_1.png'),
            Image.open('/home/choisuyeon/ESW/frame_rabbit_running/rabbit_running_2.png'),
            Image.open('/home/choisuyeon/ESW/frame_rabbit_running/rabbit_running_3.png'),
            Image.open('/home/choisuyeon/ESW/frame_rabbit_running/rabbit_running_4.png'),
            Image.open('/home/choisuyeon/ESW/frame_rabbit_running/rabbit_running_5.png')
        ]
        self.slide_images = [
            Image.open('/home/choisuyeon/ESW/frame_rabbit_riding/rabbit_riding_1.png'),
            Image.open('/home/choisuyeon/ESW/frame_rabbit_riding/rabbit_riding_2.png')
        ]
        self.current_image_index = 0
        self.jump_state = False
        self.slide_state = False
        self.gravity = 5
        self.jump_speed = -20
        self.vertical_speed = 0

    def draw(self, draw_surface):
        if self.slide_state:
            image = self.slide_images[self.current_image_index % len(self.slide_images)]
        else:
            image = self.run_images[self.current_image_index % len(self.run_images)]
        draw_surface.paste(image, (int(self.position[0]), int(self.position[1])), image)
        self.current_image_index = (self.current_image_index + 1) % len(self.run_images)

    def update(self):
        if self.position[1] < self.height - 100 or self.vertical_speed < 0:
            self.position[1] += self.vertical_speed
            self.vertical_speed += self.gravity

        if self.position[1] >= self.height - 100:
            self.position[1] = self.height - 100
            self.vertical_speed = 0
            self.jump_state = False

        self.position[0] += 2  # 일정한 속도로 오른쪽으로 이동

    def jump(self):
        if not self.jump_state and self.position[1] == self.height - 100:
            self.jump_state = True
            self.vertical_speed = self.jump_speed

    def slide(self):
        if not self.slide_state:
            self.slide_state = True
            self.position[1] += 20  # 아래로 이동하여 슬라이드 효과
            time.sleep(0.2)
            self.position[1] -= 20
            self.slide_state = False

class Background:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.image = Image.open('/home/choisuyeon/ESW/background.png').resize((width, height))
        self.offset = 0
        self.carrots = []

    def update(self):
        self.offset -= 2
        if self.offset <= -self.width:
            self.offset = 0

        # 랜덤으로 당근 생성
        if random.randint(1, 100) > 98:  # 낮은 확률로 당근 생성
            carrot_x = self.width + random.randint(10, 100)
            carrot_y = self.height - 120
            self.carrots.append([carrot_x, carrot_y])

        # 당근 이동
        for carrot in self.carrots:
            carrot[0] -= 2  # 왼쪽으로 이동

        # 화면을 벗어난 당근 제거
        self.carrots = [carrot for carrot in self.carrots if carrot[0] > -50]

    def draw(self, draw_surface):
        draw_surface.paste(self.image, (self.offset, 0))
        draw_surface.paste(self.image, (self.offset + self.width, 0))
        carrot_image = Image.open('/home/choisuyeon/ESW/carrot.png').resize((30, 30))
        for carrot in self.carrots:
            draw_surface.paste(carrot_image, (carrot[0], carrot[1]), carrot_image)

joystick = Joystick()
rabbit = Rabbit(joystick.width, joystick.height)
background = Background(joystick.width, joystick.height)
screen = Image.new("RGBA", (joystick.width, joystick.height), (255, 255, 255, 0))

offset = 0

while True:
    if not joystick.button_U.value:
        rabbit.jump()
    if not joystick.button_D.value:
        rabbit.slide()

    background.update()
    background.draw(screen)
    rabbit.update()
    rabbit.draw(screen)
    joystick.disp.image(screen)
      # 세 번째 인자는 투명도 적용
    
    time.sleep(0.01)
