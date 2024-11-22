# 필요한 라이브러리 import 
import time
import random
from colorsys import hsv_to_rgb
import board
from digitalio import DigitalInOut, Direction
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789
from setting import Joystick # Joystick 클래스는 설정 파일에서 불러옴

# 필요한 이미지 불러오기
# Rabbit 애니메이션 이미지 (달리기, 라이딩, 점프 등)
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

# Rabbit 성공/실패 애니메이션 이미지
RABBIT_SUCCESS=[Image.open(f"/home/choisuyeon/ESW/frame_rabbit_success/rabbit_success_{i}.png").resize((240, 240)) for i in range(1, 13+1)]
RABBIT_FAILURE=[Image.open(f"/home/choisuyeon/ESW/frame_rabbit_failure/rabbit_failure_{i}.png").resize((240, 240)) for i in range(1, 30+1)]

# 장애물 및 아이템 이미지
SMALL_CACTUS=[Image.open("/home/choisuyeon/ESW/cactus/SmallCactus1.png").resize((60,60)),
              Image.open("/home/choisuyeon/ESW/cactus/SmallCactus2.png").resize((60,60))]

DOGS=[Image.open("/home/choisuyeon/ESW/dog_hammer.png").resize((60,60)),
        Image.open("/home/choisuyeon/ESW/fence.png").resize((60,60))]


CARROT=Image.open("/home/choisuyeon/ESW/carrot.png").resize((30,30))
STAR=Image.open("/home/choisuyeon/ESW/star.png").resize((30,30))
PLANE=Image.open("/home/choisuyeon/ESW/plane.png").resize((40,40))

BG=Image.open("/home/choisuyeon/ESW/background.png").resize((240,240))

# Rabbit 클래스
class Rabbit:
    X_POS = 20  # 토끼는 제자리에서 동작 (x좌표:20, y좌표:180)
    Y_POS = 180 # Rabbit의 기본 Y 좌표 (달리기 상태)
   
    GROUND_LEVEL = 180  # 땅의 Y 좌표(최저 높이)
    JUMP_VEL = 5 # 점프 시 초기 속도 (위로 올라가는 속도)

    """Rabbit 객체의 초기화"""
    # Rabbit 동작 상태
    def __init__(self):
         # Rabbit의 동작 상태에 따른 애니메이션 및 이미지
        self.run_img = RABBIT_RUNNING # 달리기 애니메이션
        self.jump_img = RABBIT_JUMPING  # 점프 이미지
        self.down_img = RABBIT_JUMPING  # 하강 시 이미지
        self.riding_img = RABBIT_RIDING # 별 획득 후 라이딩 애니메이션
        self.slide_img = RABBIT_SLIDING  # 슬라이딩 이미지

        # Rabbit 동작 상태를 나타내는 플래그 (True일 경우 해당 동작 활성화)
        self.rabbit_down = False  # 하강 중인지 여부
        self.rabbit_run = True # 달리는 중인지 여부
        self.rabbit_jump = False # 점프 중인지 여부
        self.rabbit_slide=False  # 슬라이딩 중인지 여부
        self.riding_mode = False  # 별 충돌로 인한 라이딩 모드
        self.riding_timer = 0  # 라이딩 지속 시간

         # Rabbit 동작 시 애니메이션 프레임 관리
        self.step_index = 0 # 현재 애니메이션 프레임의 인덱스
        self.jump_vel = self.JUMP_VEL  # 점프 시 속도
        self.fall_vel = 19  # 하강 시 속도
        self.image = self.run_img[0] # 초기 이미지 (달리기 상태의 첫 번째 프레임)
        self.rabbit_x = self.X_POS  # Rabbit의 X 좌표
        self.rabbit_y = self.Y_POS # Rabbit의 Y 좌표
    
    """Rabbit 상태 업데이트"""
    def update(self):
        # Rabbit의 상태에 따라 동작을 수행
        if self.riding_mode:  # 라이딩 모드일 경우 라이딩 애니메이션 유지
            self.ride()
        elif self.rabbit_jump: # 점프 중일 경우
            self.jump() 
        elif self.rabbit_down:  # 하강 중일 경우
            self.fall()  
        elif self.rabbit_slide:# 슬라이딩 중일 경우
            self.slide()
        elif self.rabbit_run:  # 달리기 중일 경우
            self.run()

    def run(self):
        """달리기 동작"""
        frame_count = len(self.run_img)  # 애니메이션 프레임 수
         # 애니메이션 프레임 순환
        self.image = self.run_img[self.step_index // 5 % frame_count] # 5 프레임당 이미지 전환 ->유효한 프레임 인덱스 유지
        self.step_index += 1 # 다음 프레임으로 이동


    def jump(self):
        """점프 동작"""
        if self.rabbit_jump: 
            self.image = self.jump_img # 점프 이미지를 설정
            self.rabbit_y -= self.jump_vel * 6 # 점프 속도에 따라 Y 좌표 감소 (위로 이동)
            self.jump_vel -= 1 # 점프 속도 감소 (중력 효과)
            # 점프 최고점 도달 후
            if self.jump_vel < -self.JUMP_VEL:  # 초기 점프 속도의 반대 방향으로 이동 시
                self.rabbit_jump = False # 점프 상태 종료
                self.rabbit_run = True # 달리기 상태로 복귀
                self.jump_vel = self.JUMP_VEL # 점프 속도 초기화
                self.rabbit_y = self.Y_POS # Rabbit의 Y 좌표 초기화

    def fall(self):
        """하강 동작"""
        self.image = self.down_img # 하강 이미지를 설정
        # 땅에 도달할 때까지 Y 좌표를 증가 (아래로 이동)
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
                self.rabbit_y -= 5  # 슬라이드 위치로 이동
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
        if self.riding_mode:  # 라이딩 모드일 경우
            self.riding_timer -= 1  # 타이머 감소
            if self.riding_timer <= 0: # 타이머 종료 시
                self.riding_mode = False  # 라이딩 모드 종료
                self.rabbit_run = True  # 라이딩 종료 후 런 상태로 복귀    

    def draw(self, canvas):
        """Rabbit 이미지 그리기"""
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

    

# Obstacle 클래스 및 하위 클래스
class Obstacle:
    """
    게임 내 장애물을 정의하는 기본 클래스.
    각 장애물의 위치, 이미지, 동작(이동, 화면 표시)을 관리.
    """
    def __init__(self, x, y, images):
        """
        초기화 메서드.
        :param x: 장애물의 초기 X 좌표.
        :param y: 장애물의 초기 Y 좌표.
        :param images: 장애물 이미지 리스트 (랜덤으로 선택됨).
        """
        self.x = x # 장애물의 X 좌표
        self.y = y  # 장애물의 Y 좌표
        self.images = images # 장애물의 이미지 리스트
        self.image = random.choice(self.images) # 이미지 리스트에서 랜덤 선택

    def move(self, speed=5):
        """
        장애물을 왼쪽으로 이동시키는 메서드.
        :param speed: 장애물의 이동 속도 (기본값: 5).
        """
        self.x -= speed # X 좌표를 속도만큼 감소시켜 왼쪽으로 이동

    def draw(self, canvas):
        """
        장애물을 화면에 표시하는 메서드.
        :param canvas: 장애물을 그릴 캔버스.
        """
        # 장애물 이미지를 X, Y 위치에 그리기
        canvas.paste(self.image, (int(self.x), int(self.y)), self.image)

    def is_off_screen(self):
        """
        장애물이 화면 밖으로 나갔는지 확인하는 메서드.
        :return: 화면 밖으로 나갔으면 True, 아니면 False.
        """
        # 장애물의 오른쪽 끝이 화면의 왼쪽 끝보다 작으면 화면 밖
        return self.x + self.image.width < 0

# 작은 선인장을 나타내는 클래스
class SmallCactus(Obstacle):
    """
    작은 선인장 장애물 클래스.
    Obstacle 클래스를 상속받아 SmallCactus의 고유 속성을 정의.
    """
    def __init__(self, x):
        # 상위 Obstacle 클래스의 초기화 메서드 호출
        # Y 좌표를 180으로 고정, 이미지 리스트는 SMALL_CACTUS 사용
        super().__init__(x, 180, SMALL_CACTUS)

# 사냥개,fence 를 나타내는 클래스
class Dogs(Obstacle):
    def __init__(self, x):
        # 상위 Obstacle 클래스의 초기화 메서드 호출
        # Y 좌표를 180으로 고정, 이미지 리스트는 DOGS 사용
        super().__init__(x, 180, DOGS)

# Plane Class
class Plane:
    def __init__(self, canvas_width, canvas_height):
        self.x = random.randint(0, canvas_width )
        self.y = random.randint(30,canvas_height-90)
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
        self.x = random.randint(0, canvas_width)
        self.y = random.randint(50,canvas_height-60)
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
        self.y = random.randint(50, canvas_height-60)
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
        self.image = image # 배경으로 사용할 이미지
        self.width = width # 배경 이미지의 너비
        self.height = height # 배경 이미지의 높이
        self.x1 = 0 # 첫 번째 배경 이미지의 초기 x 좌표
        self.x2 = width # 두 번째 배경 이미지의 초기 x 좌표 (첫 번째 이미지 오른쪽에 위치)

    def move(self, speed=2):
        """
        배경 이미지를 왼쪽으로 이동시킴 (스크롤 효과)

        매개변수:
        - speed: 이동 속도 (기본값: 2)
        """
        self.x1 -= speed  # 첫 번째 배경 이미지를 왼쪽으로 이동
        self.x2 -= speed # 두 번째 배경 이미지를 왼쪽으로 이동
        # 첫 번째 배경 이미지가 화면 밖으로 나가면, 두 번째 이미지 뒤로 위치 재조정
        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width

          # 두 번째 배경 이미지가 화면 밖으로 나가면, 첫 번째 이미지 뒤로 위치 재조정
        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width

    def draw(self, canvas):
        """
        배경 이미지를 캔버스에 그려줌 (두 개의 배경 이미지를 순서대로 출력)

        매개변수:
        - canvas: 이미지를 그릴 캔버스 객체
        """
        canvas.paste(self.image, (self.x1, 0)) # 첫 번째 배경 이미지 출력
        canvas.paste(self.image, (self.x2, 0))  # 두 번째 배경 이미지 출력


# Collision Detection
def check_collision(entity1, entity2):
    # 첫 번째 객체(entity1)의 경계 상자 정의 (x1, y1, x2, y2)
    entity1_box = (entity1.rabbit_x, # 경계 상자의 왼쪽 x 좌표
                    entity1.rabbit_y, # 경계 상자의 위쪽 y 좌표
                   entity1.rabbit_x + entity1.image.width, # 경계 상자의 오른쪽 x 좌표
                   entity1.rabbit_y + entity1.image.height # 경계 상자의 아래쪽 y 좌표
                   )
     # 두 번째 객체(entity2)의 경계 상자 정의 (x1, y1, x2, y2)
    entity2_box = (entity2.x, # 경계 상자의 왼쪽 x 좌표
                   entity2.y, # 경계 상자의 위쪽 y 좌표
                   entity2.x + entity2.image.width, # 경계 상자의 오른쪽 x 좌표
                   entity2.y + entity2.image.height # 경계 상자의 아래쪽 y 좌표
                   )

    # 두 경계 상자가 겹치는지 확인 (충돌 여부 계산)
    return (
        entity1_box[0] < entity2_box[2] and # entity1의 왼쪽이 entity2의 오른쪽 안에 있는지
        entity1_box[2] > entity2_box[0] and # entity1의 오른쪽이 entity2의 왼쪽 안에 있는지
        entity1_box[1] < entity2_box[3] and # entity1의 위쪽이 entity2의 아래쪽 안에 있는지
        entity1_box[3] > entity2_box[1] # entity1의 아래쪽이 entity2의 위쪽 안에 있는지
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

def is_safe_to_add_object(new_x, objects, min_distance=100):
    """새 객체가 기존 객체와 최소 거리 이상 떨어져 있는지 확인"""
    for obj in objects:
        if abs(new_x - obj.x) < min_distance:
            return False
    return True

def check_restart(joystick):
    """button_A를 눌렀을 때 True를 반환"""
    return not joystick.button_A.value  # button_A가 눌렸을 때 False에서 True로 전환


def game_loop():
    joystick = Joystick() # Joystick 객체 생성
    start_animation(joystick)  # 게임 시작 애니메이션 호출
    while True:
        # 초기 상태 설정
        rabbit = Rabbit() # Rabbit 객체 생성
        background = Background(BG, 240, 240)  # 배경 이미지 설정
        obstacles = [] # 장애물 리스트
        planes=[]  # 비행기 장애물 리스트
        carrots = [] # 당근 아이템 리스트
        stars = [] # 별 아이템 리스트

        canvas = Image.new("RGB", (joystick.width, joystick.height)) # 화면 캔버스(도화지) 생성
        draw = ImageDraw.Draw(canvas)   # 캔버스에 그리기 객체 생성
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        font_large = ImageFont.truetype(font_path, 30)  # 글씨 크기 30 설정

        # 게임 초기 변수 설정
        health = 10 # 체력 초기값
        distance = 8000 # 초기 거리 (8000m, 8km)
        game_speed = 15 # 초기 게임 속도
        game_running = True  # 게임 진행 상태 플래그
        success = False # 성공 여부
        fail = False # 실패 여부

        while game_running: # 게임이 실행 중일 때
            # Rabbit의 상태 업데이트
            rabbit.handle_input(joystick) # 사용자 입력 처리
            rabbit.update() # Rabbit 상태 업데이트
            rabbit.update_riding_timer()  # 별 충돌로 인한 라이딩 상태 타이머 업데이트

            if rabbit.riding_mode:
                game_speed = 50  # 라이딩 모드일 때 속도 증가
            else:
                game_speed = 20  # 기본 속도

            # 거리 감소 (Riding 상태에서는 50씩 감소, 일반 상태에서는 10씩 감소)
            if rabbit.riding_mode:
                distance -= 50
            else:
                distance -= 10  

            # 장애물 생성
            if random.randint(1, 100) < 5: # 5% 확률로 장애물 생성
                new_x = 240
                if is_safe_to_add_obstacle(new_x, obstacles): # 장애물 간 최소 거리 유지
                    if random.choice([True, False]): # 50% 확률로 장애물 유형 선택
                        obstacles.append(SmallCactus(new_x))
                    else:
                        obstacles.append(Dogs(new_x))

            # 당근 생성
            if random.randint(1, 100) < 6: # 6% 확률로 당근 생성
                new_x = 240
                if is_safe_to_add_object(new_x, carrots, min_distance=50): # 당근 간 최소 거리 유지  # 최소 간격 설정
                    carrots.append(Carrot(240, 240))

            # 별 생성
            if random.randint(1, 100) < 2: # 2% 확률로 별 생성
                new_x = 240
                if is_safe_to_add_object(new_x, stars, min_distance=150): # 별 간 최소 거리 유지
                    stars.append(Star(240, 240))

            # 비행기 생성
            if random.randint(1, 100) < 4: # 4% 확률로 비행기 생성
                new_x = 240
                if is_safe_to_add_object(new_x, planes, min_distance=150): # 비행기 간 최소 거리 유지
                    planes.append(Plane(240, 240))

             # 배경 이동
            background.move(game_speed)

            # 장애물, 아이템 등 게임 오브젝트 이동
            for obstacle in obstacles:
                obstacle.move(5)

            for plane in planes:
                plane.move(5)

            for carrot in carrots:
                carrot.move(5)
            
            for star in stars:
                star.move(5)

            # Riding 상태가 아닐 때 충돌 처리
            if not rabbit.riding_mode:
                for obstacle in obstacles: # 장애물 충돌
                    if check_collision(rabbit, obstacle):
                        health -= 2  # 체력 감소
                        obstacles.remove(obstacle) # 충돌한 장애물 제거

                for carrot in carrots: # 당근 충돌
                    if check_collision(rabbit, carrot): 
                        health += 1 # 체력 증가
                        carrots.remove(carrot) # 충돌한 당근 제거

                for plane in planes: # 비행기 충돌
                    if check_collision(rabbit,plane):
                        health-=3  # 체력 감소
                        planes.remove(plane) # 충돌한 비행기 제거
   

            # 별과 충돌 시 Riding 모드 활성화
            for star in stars:
                if check_collision(rabbit, star):
                    health+=3 # 체력 증가
                    rabbit.activate_riding_mode(duration=20)  # 20 loop 동안 Riding 모드 활성화
                    stars.remove(star) # 충돌한 별 제거

            # 화면에 그리기
            background.draw(canvas) # 배경 그리기
            rabbit.draw(canvas) # Rabbit 그리기
            for obstacle in obstacles: # 장애물 그리기 (obstacle list에 존재)
                obstacle.draw(canvas)
            for plane in planes:  # 비행기 장애물 그리기(planes list에 존재)
                plane.draw(canvas)
            for carrot in carrots: # 당근 아이템 그리기(carots list에 존재)
                carrot.draw(canvas)
            for star in stars: # 별 아이템 그리기(starts list에 존재)
                star.draw(canvas)


            # 체력 표시
            draw.text((50, 10), f"Health: {health}", fill="white", font=font_large)

            # 화면 밖으로 나간 오브젝트 제거
            obstacles = [ob for ob in obstacles if not ob.is_off_screen()]
            planes=[plane for plane in planes if not plane.is_off_screen()]
            carrots = [carrot for carrot in carrots if not carrot.is_off_screen()]
            stars = [star for star in stars if not star.is_off_screen()]

            # 게임 종료 조건
            if health <= 0: # 체력이 0 이하일 때
                draw.text((20, 100), "Game Over", fill="red", align="center", font=font_large)
                joystick.disp.image(canvas)
                time.sleep(2)
                success = False
                fail = True
                game_running = False  # 게임 종료
            elif distance <= 0: # 목표 거리를 달성했을 때
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
                game_running = False  # 게임 종료

            # 화면 업데이트
            joystick.disp.image(canvas)

            # 게임 종료 후 성공/실패 애니메이션 출력
            if not game_running:
                if success:
                    play_animation_loop(success=True, joystick=joystick)
                elif fail:
                    play_animation_loop(success=False, joystick=joystick)
                time.sleep(3)
                break

        # 게임 재시작 대기 (Button A 누를 때까지 대기)
        while not check_restart(joystick):
            canvas = Image.new("RGB", (joystick.width, joystick.height))
            draw = ImageDraw.Draw(canvas)  # 텍스트 그리기 객체 생성
            draw.text((20, 100), "Press A", fill="yellow", font=font_large)
            draw.text((20, 150), "To Restart", fill="yellow", font=font_large)
            joystick.disp.image(canvas)
            time.sleep(0.1)

        # Restart 게임 루프(게임 상태 초기화)
        continue

game_loop()