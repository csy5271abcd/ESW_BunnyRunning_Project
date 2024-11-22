# 필요한 라이브러리 import 
import time
import random
from colorsys import hsv_to_rgb
import board
from digitalio import DigitalInOut, Direction
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789
from setting import Joystick

# 필요한 이미지 불러오기
RABBIT_RUNNING=[Image.open("/home/choisuyeon/ESW/frame_rabbit_running/rabbit_running_1.png").resize((60,60)),
         Image.open("/home/choisuyeon/ESW/frame_rabbit_running/rabbit_running_2.png").resize((60,60)),
         Image.open("/home/choisuyeon/ESW/frame_rabbit_running/rabbit_running_3.png").resize((60,60)),
         Image.open("/home/choisuyeon/ESW/frame_rabbit_running/rabbit_running_4.png").resize((60,60)),
         Image.open("/home/choisuyeon/ESW/frame_rabbit_running/rabbit_running_5.png").resize((60,60))]
RABBIT_RIDING=[Image.open("/home/choisuyeon/ESW/frame_rabbit_riding/rabbit_riding_1.png").resize((60,60)),
         Image.open("/home/choisuyeon/ESW/frame_rabbit_riding/rabbit_riding_2.png").resize((60,60)),
         Image.open("/home/choisuyeon/ESW/frame_rabbit_riding/rabbit_riding_3.png").resize((60,60)),
         Image.open("/home/choisuyeon/ESW/frame_rabbit_riding/rabbit_riding_4.png").resize((60,60)),
         Image.open("/home/choisuyeon/ESW/frame_rabbit_riding/rabbit_riding_5.png").resize((60,60)),
         Image.open("/home/choisuyeon/ESW/frame_rabbit_riding/rabbit_riding_6.png").resize((60,60)),
         Image.open("/home/choisuyeon/ESW/frame_rabbit_riding/rabbit_riding_7.png").resize((60,60)),
         Image.open("/home/choisuyeon/ESW/frame_rabbit_riding/rabbit_riding_8.png").resize((60,60))]

RABBIT_JUMPING=Image.open("/home/choisuyeon/ESW/rabbit_jumping.png").resize((60,60))
RABBIT_SLIDING=Image.open("/home/choisuyeon/ESW/rabbit_sliding.png").resize((60,40))
RABBIT_EATING=[Image.open(f"/home/choisuyeon/ESW/frame_rabbit_eating/frame_rabbit_eating_{i:04d}.png").resize((240, 240)) for i in range(0, 64+1)]

RABBIT_SUCCESS=[Image.open(f"/home/choisuyeon/ESW/frame_rabbit_success/rabbit_success_{i}.png").resize((240, 240)) for i in range(1, 13+1)]

RABBIT_FAILURE=[Image.open(f"/home/choisuyeon/ESW/frame_rabbit_failure/rabbit_failure_{i}.png").resize((240, 240)) for i in range(1, 30+1)]

SMALL_CACTUS=[Image.open("/home/choisuyeon/ESW/cactus/SmallCactus1.png").resize((60,60)),
              Image.open("/home/choisuyeon/ESW/cactus/SmallCactus2.png").resize((60,60))]

DOGS=[Image.open("/home/choisuyeon/ESW/dog_hammer.png").resize((60,60)),
        Image.open("/home/choisuyeon/ESW/fence.png").resize((60,60))]


CARROT=Image.open("/home/choisuyeon/ESW/carrot.png").resize((30,30))
STAR=Image.open("/home/choisuyeon/ESW/star.png").resize((30,30))
PLANE=Image.open("/home/choisuyeon/ESW/plane.png").resize((40,40))

BG=Image.open("/home/choisuyeon/ESW/background.png").resize((240,240))

# Rabbit Class
class Rabbit:
    X_POS = 20  # 토끼는 제자리에서 동작 (x좌표:20, y좌표:180)
    Y_POS = 180
   
    GROUND_LEVEL = 180  # 땅의 Y 좌표
    JUMP_VEL = 5 # 올라간 다음 내려올 경우 5씩 감소

    def __init__(self):
        self.run_img = RABBIT_RUNNING # Rabbit class attribute로 필요한 프레임 이미지를 불러옴
        self.jump_img = RABBIT_JUMPING
        self.down_img = RABBIT_JUMPING
        self.riding_img = RABBIT_RIDING
        self.slide_img = RABBIT_SLIDING

        self.rabbit_down = False  
        self.rabbit_run = True
        self.rabbit_jump = False
        self.rabbit_slide=False
        self.riding_mode = False  # 별 충돌로 인한 라이딩 모드
        self.riding_timer = 0  # 라이딩 지속 시간

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.fall_vel = 19  # rabbit_down일 경우 하강 속도 증가
        self.image = self.run_img[0]
        self.rabbit_x = self.X_POS
        self.rabbit_y = self.Y_POS

    def update(self):
        if self.riding_mode:  # 라이딩 모드일 경우 라이딩 애니메이션 유지
            self.ride()
        elif self.rabbit_jump:
            self.jump()
        elif self.rabbit_down:
            self.fall()  # 하강 동작 호출
        elif self.rabbit_slide:
            self.slide()
        elif self.rabbit_run:
            self.run()

    def run(self):
        """달리기 동작"""
        frame_count = len(self.run_img)  # 애니메이션 프레임 수
        self.image = self.run_img[self.step_index // 5 % frame_count]  # 유효한 프레임 인덱스 유지
        self.step_index += 1


    def jump(self):
        """점프 동작"""
        if self.rabbit_jump:
            self.image = self.jump_img
            self.rabbit_y -= self.jump_vel * 5
            self.jump_vel -= 1
            if self.jump_vel < -self.JUMP_VEL:
                self.rabbit_jump = False
                self.rabbit_run = True
                self.jump_vel = self.JUMP_VEL
                self.rabbit_y = self.Y_POS

    def fall(self):
        """하강 동작"""
        self.image = self.down_img
        if self.rabbit_y < self.GROUND_LEVEL:
            self.rabbit_y += self.fall_vel  # 하강 속도만큼 Y 좌표 증가
        else:
            self.rabbit_y = self.GROUND_LEVEL  # 땅에 도달하면 멈춤
            self.rabbit_down = False  # 하강 상태 종료
            self.rabbit_run = True  # 다시 런 상태로 복귀

    def slide(self):
        """현재 Y좌표를 기준으로 슬라이드 동작"""
        if self.rabbit_slide:
            if not hasattr(self, "original_y"):  # 슬라이드 시작 시 Y좌표 저장
                self.original_y = self.rabbit_y  # 현재 Y좌표를 저장
                self.rabbit_y -= 10  # 슬라이드 위치로 이동
                self.slide_start_time = time.time()  # 슬라이드 시작 시간 기록

            self.image = self.slide_img

            # 슬라이드 상태를 2초 동안 유지
            if time.time() - self.slide_start_time > 2:  # 2초 경과 후 슬라이드 상태 종료
                self.rabbit_slide = False
                self.rabbit_y = self.original_y  # 원래 Y좌표로 복귀
                del self.original_y  # 저장된 Y좌표 초기화
        else:
            if hasattr(self, "original_y"):  # 슬라이드 종료 후 Y좌표 초기화
                del self.original_y


    def ride(self):
        """라이딩 동작"""
        frame_count = len(self.riding_img)  # 애니메이션 프레임 수
        self.image = self.riding_img[self.step_index // 5 % frame_count]  # 유효한 프레임 인덱스 유지
        self.step_index += 1

    def activate_riding_mode(self, duration):
        """별 충돌로 라이딩 모드 활성화"""
        self.riding_mode = True
        self.riding_timer = duration

    def update_riding_timer(self):
        """라이딩 타이머 업데이트"""
        if self.riding_mode:
            self.riding_timer -= 1
            if self.riding_timer <= 0:
                self.riding_mode = False  # 라이딩 모드 종료
                self.rabbit_run = True  # 라이딩 종료 후 런 상태로 복귀    

    def draw(self, canvas):
        canvas.paste(self.image, (int(self.rabbit_x), int(self.rabbit_y)), self.image)

    def handle_input(self, joystick):
        """입력 처리"""
        if not joystick.button_U.value:  # Jump
            self.rabbit_jump = True
            self.rabbit_run = False
            self.rabbit_down = False
            self.rabbit_slide=False

        elif not joystick.button_D.value:  # Fall
            self.rabbit_down = True
            self.rabbit_run = False
            self.rabbit_jump = False
            self.rabbit_slide=False

        elif not joystick.button_R.value:  # Slide
            self.rabbit_slide = True
            self.rabbit_run = False
            self.rabbit_jump = False
            self.rabbit_down=False

        else:  # Run
            self.rabbit_run = True
            self.rabbit_down = False
            self.rabbit_jump = False 
            self.rabbit_slide=False   

    

# Obstacle Base Class
class Obstacle:
    def __init__(self, x, y, images):
        self.x = x
        self.y = y
        self.images = images
        self.image = random.choice(self.images)

    def move(self, speed=5):
        self.x -= speed

    def draw(self, canvas):
        canvas.paste(self.image, (int(self.x), int(self.y)), self.image)

    def is_off_screen(self):
        return self.x + self.image.width < 0

# SmallCactus Class
class SmallCactus(Obstacle):
    def __init__(self, x):
        super().__init__(x, 180, SMALL_CACTUS)

# Dog Class
class Dogs(Obstacle):
    def __init__(self, x):
        super().__init__(x, 180, DOGS)

# Plane Class
class Plane:
    def __init__(self, canvas_width, canvas_height):
        self.x = random.randint(0, canvas_width )
        self.y = random.randint(50,150)
        self.image = PLANE

    def move(self, speed=5):
        self.x -= speed

    def draw(self, canvas):
        canvas.paste(self.image, (int(self.x), int(self.y)), self.image)

    def is_off_screen(self):
        return self.x + self.image.width < 0
    
# Carrot Class
class Carrot:
    def __init__(self, canvas_width, canvas_height):
        self.x = random.randint(0, canvas_width )
        self.y = random.randint(50,canvas_height)
        self.image = CARROT

    def move(self, speed=5):
        self.x -= speed

    def draw(self, canvas):
        canvas.paste(self.image, (int(self.x), int(self.y)), self.image)

    def is_off_screen(self):
        return self.x + self.image.width < 0

# Star Class
class Star:
    def __init__(self, canvas_width, canvas_height):
        self.x = random.randint(0, canvas_width)
        self.y = random.randint(50, canvas_height)
        self.image = STAR

    def move(self, speed=5):
        self.x -= speed

    def draw(self, canvas):
        canvas.paste(self.image, (int(self.x), int(self.y)), self.image)

    def is_off_screen(self):
        return self.x + self.image.width < 0

# Background Class
class Background:
    def __init__(self, image, width, height):
        self.image = image
        self.width = width
        self.height = height
        self.x1 = 0
        self.x2 = width

    def move(self, speed=2):
        self.x1 -= speed
        self.x2 -= speed
        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width
        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width

    def draw(self, canvas):
        canvas.paste(self.image, (self.x1, 0))
        canvas.paste(self.image, (self.x2, 0))


# Collision Detection
def check_collision(entity1, entity2):
    entity1_box = (entity1.rabbit_x, entity1.rabbit_y,
                   entity1.rabbit_x + entity1.image.width,
                   entity1.rabbit_y + entity1.image.height)

    entity2_box = (entity2.x, entity2.y,
                   entity2.x + entity2.image.width,
                   entity2.y + entity2.image.height)

    return (
        entity1_box[0] < entity2_box[2] and
        entity1_box[2] > entity2_box[0] and
        entity1_box[1] < entity2_box[3] and
        entity1_box[3] > entity2_box[1]
    )

def play_animation_loop(success, joystick):
    """성공 또는 실패 상태에 따라 애니메이션 출력"""
    canvas_width = joystick.width
    canvas_height = joystick.height
    frames = RABBIT_SUCCESS if success else RABBIT_FAILURE  # 성공/실패 프레임 선택

    # 새로운 도화지 생성
    new_canvas = Image.new("RGB", (canvas_width, canvas_height), "black")
    for _ in range(2):  # 애니메이션 3번 반복
        for frame in frames:
            temp_canvas = new_canvas.copy()  # 도화지 복사
            temp_canvas.paste(frame, (0, 0))  # 프레임을 중앙에 출력
            joystick.disp.image(temp_canvas)  # 화면에 출력
            time.sleep(0.1)  # 프레임 전환 속도

def start_animation(joystick):
    """게임 시작 애니메이션과 텍스트 한 문장씩 빠르게 표시"""
    canvas_width = joystick.width
    canvas_height = joystick.height
    frames = RABBIT_EATING  # 애니메이션 프레임 리스트
    messages = [
        " I'm a rabbit.",
        " I need to",
        " steal carrots",
        " from the ",
        " farmer's field.",
        " I must make ",
        " it back",
        " to my burrow.",
        " The farmer is",
        " chasing me!!!"
    ]

    # 새로운 도화지 생성
    new_canvas = Image.new("RGB", (canvas_width, canvas_height), "black")
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_large = ImageFont.truetype(font_path, 30)  # 글씨 크기 25로 설정

    for message in messages:
        for frame in frames:
            # 현재 프레임을 새로운 도화지에 복사
            temp_canvas = new_canvas.copy()
            temp_canvas.paste(frame, (0, 0))  # 프레임을 화면 중앙에 출력

            # 텍스트 추가
            draw = ImageDraw.Draw(temp_canvas)
            text_x, text_y = 0, 0  # 텍스트 위치를 좌상단 (0, 0)으로 설정
            draw.text((text_x, text_y), message, fill="black", font=font_large)

            # 디스플레이에 출력
            joystick.disp.image(temp_canvas)
            time.sleep(1)  # 프레임 전환 속도를 0.1초로 더 빠르게 조정
            break  # 각 프레임에서 메시지는 한 번만 출력하고 넘어감

    # 모든 메시지가 출력된 후 함수 종료 -> 게임 시작



def is_safe_to_add_obstacle(new_x, obstacles, min_distance=100):
    """새 장애물이 기존 장애물과 최소 거리 이상 떨어져 있는지 확인"""
    for obstacle in obstacles:
        if abs(new_x - obstacle.x) < min_distance:
            return False
    return True

def check_restart(joystick):
    """button_A를 눌렀을 때 True를 반환"""
    return not joystick.button_A.value  # button_A가 눌렸을 때 False에서 True로 전환


def game_loop():
    joystick = Joystick()
    start_animation(joystick)  # 게임 시작 애니메이션 호출
    while True:
        # 초기 상태 설정
        rabbit = Rabbit()
        background = Background(BG, 240, 240)
        obstacles = []
        planes=[]
        carrots = []
        stars = []

        canvas = Image.new("RGB", (joystick.width, joystick.height))
        draw = ImageDraw.Draw(canvas)  # 텍스트 그리기 객체 생성
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        font_large = ImageFont.truetype(font_path, 30)  # 글씨 크기 30 설정

        health = 10
        distance = 8000
        game_speed = 15
        game_running = True
        success = False
        fail = False

        while game_running:
            rabbit.handle_input(joystick)
            rabbit.update()
            rabbit.update_riding_timer()  # 라이딩 타이머 업데이트

            if rabbit.riding_mode:
                game_speed = 50  # 라이딩 모드일 때 속도 증가
            else:
                game_speed = 20  # 기본 속도

            # Riding 상태일 때 distance 50씩 감소
            if rabbit.riding_mode:
                distance -= 50
            else:
                distance -= 10  # 일반 상태에서는 10씩 감소

            # 장애물 생성
            if random.randint(1, 100) < 5:
                new_x = 240
                if is_safe_to_add_obstacle(new_x, obstacles):
                    if random.choice([True, False]):
                        obstacles.append(SmallCactus(new_x))
                    else:
                        obstacles.append(Dogs(new_x))

            # 당근 생성
            if random.randint(1, 100) < 6:
                carrots.append(Carrot(240, 240))

            # 별 생성
            if random.randint(1, 100) < 2:
                stars.append(Star(240, 240))

            # 비행기 생성
            if random.randint(1,100) <5:
                carrots.append(Plane(240,240))

            background.move(game_speed)

            for obstacle in obstacles:
                obstacle.move(game_speed)

            for plane in planes:
                plane.move(game_speed)

            for carrot in carrots:
                carrot.move(game_speed)
            
            for star in stars:
                star.move(game_speed)

            # Riding 상태가 아닐 때 충돌 처리
            if not rabbit.riding_mode:
                for obstacle in obstacles:
                    if check_collision(rabbit, obstacle):
                        health -= 2
                        obstacles.remove(obstacle)

                for carrot in carrots:
                    if check_collision(rabbit, carrot):
                        health += 1
                        carrots.remove(carrot)

                for plane in planes:
                    if check_collision(rabbit,carrot):
                        health-=3
                        planes.remove(plane)

                

            # Riding 상태에서 별 충돌 처리
            for star in stars:
                if check_collision(rabbit, star):
                    rabbit.activate_riding_mode(duration=20)  # 라이딩 모드 
                    stars.remove(star)

            background.draw(canvas)
            rabbit.draw(canvas)
            for obstacle in obstacles:
                obstacle.draw(canvas)
            for plane in planes:
                plane.draw(canvas)
            for carrot in carrots:
                carrot.draw(canvas)
            for star in stars:
                star.draw(canvas)

            draw.text((50, 10), f"Health: {health}", fill="white", font=font_large)

            obstacles = [ob for ob in obstacles if not ob.is_off_screen()]
            planes=[plane for plane in planes if not plane.is_off_screen()]
            carrots = [carrot for carrot in carrots if not carrot.is_off_screen()]
            stars = [star for star in stars if not star.is_off_screen()]

            # 게임 종료 조건
            if health <= 0:
                draw.text((20, 100), "Game Over", fill="red", align="center", font=font_large)
                joystick.disp.image(canvas)
                time.sleep(2)
                success = False
                fail = True
                game_running = False
            elif distance <= 0:
                if health > 0:
                    draw.text((30, 100), "SUCCESS~!!", fill="green", align="center", font=font_large)
                    joystick.disp.image(canvas)
                    time.sleep(2)
                    success = True
                    fail = False
                else:
                    draw.text((20, 100), "Game Over", fill="red", align="center", font=font_large)
                    joystick.disp.image(canvas)
                    time.sleep(2)
                    success = False
                    fail = True
                game_running = False

            joystick.disp.image(canvas)

            if not game_running:
                if success:
                    play_animation_loop(success=True, joystick=joystick)
                elif fail:
                    play_animation_loop(success=False, joystick=joystick)
                time.sleep(3)
                break

        # button_A를 기다리는 루프
        while not check_restart(joystick):
            canvas = Image.new("RGB", (joystick.width, joystick.height))
            draw = ImageDraw.Draw(canvas)  # 텍스트 그리기 객체 생성
            draw.text((20, 100), "Press A", fill="yellow", font=font_large)
            draw.text((20, 150), "To Restart", fill="yellow", font=font_large)
            joystick.disp.image(canvas)
            time.sleep(0.1)

        # Restart 게임 루프
        continue

game_loop()