import time
import random
from colorsys import hsv_to_rgb
import board
from digitalio import DigitalInOut, Direction
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789
from setting import Joystick
import numpy as np

joystick=Joystick()
back_image = Image.new("RGBA", (joystick.width, joystick.height), (255, 255,255, 100))  # 배경 이미지 생성
fore_image = Image.open('/home/choisuyeon/ESW/background.png').resize((240,220)) # 앞쪽 이미지 불러오기

back_image.paste(fore_image, (0, 0), fore_image)  # 세 번째 인자는 투명도 적용
joystick.disp.image(back_image)
offset=0

def background_update():
        """
        배경을 업데이트하여 오른쪽에서 왼쪽으로 이동시킵니다.
        """
        global offset
        offset-= 2  # 왼쪽으로 이동
        if offset <= -joystick.width:
            offset = 0  # 배경이 화면을 넘어가면 초기화

        back_image.paste(fore_image, (offset, 0), fore_image)  # 세 번째 인자는 투명도 적용
        joystick.disp.image(back_image)


class Rabbit:
    def __init__(self, width, height):
        # 초기 위치 설정
        self.x=0  # 화면의 바닥 근처에 위치
        self.y=170
        self.width = width
        self.height = height
        
        
        self.jump_state = False  # 점프 여부
        
        self.gravity = 5  # 중력 효과
        self.jump_speed = -20  # 점프 초기 속도
        self.vertical_speed = 0  # 현재 수직 속도

    def run_draw(self):
        """
        토끼의 현재 프레임을 그립니다.
        """
        for i in range(1,5+1):
            rabbit_image = Image.open(f"/home/choisuyeon/ESW/frame_rabbit_running/rabbit_running_{i}.png").resize((60,60)) 
            back_image.paste(fore_image, (offset, 0), fore_image)  # 세 번째 인자는 투명도 적용
            back_image.paste(rabbit_image, (0, 170-i*10), rabbit_image)  
            joystick.disp.image(back_image)

        

    def update(self):
        """
        토끼의 위치 및 상태를 업데이트합니다.
        """
        # 중력 적용
        if self.y < self.height - 100 or self.vertical_speed < 0:
            self.y += self.vertical_speed
            self.vertical_speed += self.gravity

        # 땅에 도달하면 위치 고정 및 속도 초기화
        if self.y >= self.height - 100:
            self.y = self.height - 100
            self.vertical_speed = 0
            self.jump_state = False

        # 오른쪽으로 이동
        self.x += 5  # 일정 속도로 오른쪽으로 이동
        if self.x > self.width:
            self.x = -50  # 화면을 넘어가면 왼쪽으로 다시 나타남

    
    


# 테스트용 코드
if __name__ == "__main__":
    # 화면 크기 설정
    screen_width =240
    screen_height = 240
    
    # 토끼 객체 생성
    rabbit = Rabbit(screen_width, screen_height)

    
    

    # 토끼와 배경을 그려보기 (애니메이션 테스트)
    for _ in range(100):  # 예제 루프 100번 실행
        
        rabbit.update()
        rabbit.run_draw()  # 토끼 그리기
        
        
        background_update()
        
        
