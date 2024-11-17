import time
import random
from colorsys import hsv_to_rgb
import board
from digitalio import DigitalInOut, Direction
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789
from setting import Joystick


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

RABBIT_SUCCESS=[Image.open(f"/home/choisuyeon/ESW/frame_rabbit_success/rabbit_success_{i}.png").resize((240, 240)) for i in range(1, 13+1)]

RABBIT_FAILURE=[Image.open(f"/home/choisuyeon/ESW/frame_rabbit_failure/rabbit_failure_{i}.png").resize((240, 240)) for i in range(1, 30+1)]

SMALL_CACTUS=[Image.open("/home/choisuyeon/ESW/cactus/SmallCactus1.png").resize((60,60)),
              Image.open("/home/choisuyeon/ESW/cactus/SmallCactus2.png").resize((60,60))]

DOGS=[Image.open("/home/choisuyeon/ESW/dog_hammer.png").resize((60,60)),
        Image.open("/home/choisuyeon/ESW/fence.png").resize((60,60))]


CARROT=Image.open("/home/choisuyeon/ESW/carrot.png").resize((30,30))
STAR=Image.open("/home/choisuyeon/ESW/star.png").resize((30,30))

BG=Image.open("/home/choisuyeon/ESW/background.png").resize((240,240))

# Rabbit Class
class Rabbit:
    X_POS = 20
    Y_POS = 180
    Y_POS_SLIDE = 240
    JUMP_VEL = 6

    def __init__(self):
        self.run_img = RABBIT_RUNNING
        self.jump_img = RABBIT_JUMPING
        self.slide_img = RABBIT_SLIDING
        self.rabbit_slide = False
        self.rabbit_run = True
        self.rabbit_jump = False
        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.rabbit_x = self.X_POS
        self.rabbit_y = self.Y_POS

    def update(self):
        if self.rabbit_jump:
            self.jump()
        elif self.rabbit_slide:
            self.slide()
        elif self.rabbit_run:
            self.run()

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.step_index += 1
        self.step_index %= len(self.run_img) * 5

    def slide(self):
        if self.rabbit_slide:
            self.image = self.slide_img
            self.rabbit_y = self.Y_POS_SLIDE
        else:
            self.rabbit_y = self.Y_POS

    def jump(self):
        if self.rabbit_jump:
            self.image = self.jump_img
            self.rabbit_y -= self.jump_vel * 5
            self.jump_vel -= 1
            if self.jump_vel < -self.JUMP_VEL:
                self.rabbit_jump = False
                self.rabbit_run = True
                self.jump_vel = self.JUMP_VEL
                self.rabbit_y = self.Y_POS

    def draw(self, canvas):
        canvas.paste(self.image, (int(self.rabbit_x), int(self.rabbit_y)), self.image)

    def handle_input(self, joystick):
        if not joystick.button_U.value:  # Jump
            if not self.rabbit_jump:
                self.rabbit_jump = True
                self.rabbit_run = False
                self.rabbit_slide = False
        elif not joystick.button_R.value:  # Slide
            self.rabbit_slide = True
            self.rabbit_run = False
            self.rabbit_jump = False
        else:  # Run
            self.rabbit_run = True
            self.rabbit_slide = False
            self.rabbit_jump = False

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

# LargeCactus Class
class Dogs(Obstacle):
    def __init__(self, x):
        super().__init__(x, 180, DOGS)

# Carrot Class
class Carrot:
    def __init__(self, canvas_width, canvas_height):
        self.x = random.randint(0, canvas_width )
        self.y = random.randint(0, canvas_height)
        self.image = CARROT

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
    for _ in range(3):  # 애니메이션 3번 반복
        for frame in frames:
            temp_canvas = new_canvas.copy()  # 도화지 복사
            temp_canvas.paste(frame, (0, 0))  # 프레임을 중앙에 출력
            joystick.disp.image(temp_canvas)  # 화면에 출력
            time.sleep(0.1)  # 프레임 전환 속도


# Main Game Loop
def game_loop():
    joystick = Joystick()
    rabbit = Rabbit()
    background = Background(BG, 240, 240)
   
    obstacles = []
    carrots = []

    canvas = Image.new("RGB", (joystick.width, joystick.height))
    draw = ImageDraw.Draw(canvas)  # 텍스트 그리기 객체 생성
      # 폰트 설정
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_large = ImageFont.truetype(font_path, 30)  # 글씨 크기 30 설정
    

    health = 10
    distance = 10000  
    game_running = True
    success_frames = RABBIT_SUCCESS  # 성공 애니메이션 프레임
    failure_frames = RABBIT_FAILURE  # 실패 애니메이션 프레임
    

    while game_running:
        rabbit.handle_input(joystick)
        rabbit.update()

        
        distance -= 10  # Decrease distance by 10m per loop

        if random.randint(1, 100) < 5:
            if random.choice([True, False]):
                obstacles.append(SmallCactus(240))
            else:
                obstacles.append(Dogs(240))

        if random.randint(1, 100) < 6:
            carrots.append(Carrot(240, 240))

        background.move(20)
        for obstacle in obstacles:
            obstacle.move(15)
        for carrot in carrots:
            carrot.move(15)

        for obstacle in obstacles:
            if check_collision(rabbit, obstacle):
                health -= 2
                obstacles.remove(obstacle)

        for carrot in carrots:
            if check_collision(rabbit, carrot):
                health += 1
                carrots.remove(carrot)

        background.draw(canvas)
        rabbit.draw(canvas)
        for obstacle in obstacles:
            obstacle.draw(canvas)
        for carrot in carrots:
            carrot.draw(canvas)

        draw.text((50, 10), f"Health: {health}", fill="white", font=font_large)

        obstacles = [ob for ob in obstacles if not ob.is_off_screen()]
        carrots = [carrot for carrot in carrots if not carrot.is_off_screen()]

        

         # 게임 종료 조건
        if health <= 0:
            draw.text((20, 100), "Game Over", fill="red", align="center", font=font_large)
            joystick.disp.image(canvas)  # 메시지 출력
            time.sleep(2)  # 메시지 잠깐 표시
            success = False
            fail = True
            game_running = False
        elif distance <= 0:
            if health > 0:
                draw.text((20, 100), "SUCCESS", fill="green", align="center", font=font_large)
                joystick.disp.image(canvas)  # 메시지 출력
                time.sleep(2)  # 메시지 잠깐 표시
                success = True
                fail = False
            else:
                draw.text((20, 100), "Game Over", fill="red", align="center", font=font_large)
                joystick.disp.image(canvas)  # 메시지 출력
                time.sleep(2)  # 메시지 잠깐 표시
                success = False
                fail = True
            game_running = False

        # 화면 업데이트
        joystick.disp.image(canvas)

        if not game_running:
            if success:
                play_animation_loop(success=True, joystick=joystick)  # 성공 애니메이션 출력
            elif fail:
                play_animation_loop(success=False, joystick=joystick)  # 실패 애니메이션 출력
            time.sleep(3)  # 종료 후 3초 대기
            break
    
    



game_loop()