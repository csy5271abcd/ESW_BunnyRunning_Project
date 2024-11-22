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

# 게임 설정
background_color = (0,0,0)  # 하얀색 배경
font = ImageFont.load_default()

# Global Constants
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
RABBIT_SLIDING=Image.open("/home/choisuyeon/ESW/rabbit_sliding.png").resize((60,60))

SMALL_CACTUS=[Image.open("/home/choisuyeon/ESW/cactus/SmallCactus1.png").resize((40,40)),
              Image.open("/home/choisuyeon/ESW/cactus/SmallCactus2.png").resize((40,40)),
              Image.open("/home/choisuyeon/ESW/cactus/SmallCactus3.png").resize((40,40))]

LARGE_CACTUS=[Image.open("/home/choisuyeon/ESW/cactus/LargeCactus1.png").resize((60,60)),
              Image.open("/home/choisuyeon/ESW/cactus/LargeCactus2.png").resize((60,60)),
              Image.open("/home/choisuyeon/ESW/cactus/LargeCactus3.png").resize((60,60))]

DOG=[Image.open("/home/choisuyeon/ESW/frame_dog_running/dog_running_1.png").resize((60,60)),
         Image.open("/home/choisuyeon/ESW/frame_dog_running/dog_running_2.png").resize((60,60)),
         Image.open("/home/choisuyeon/ESW/frame_dog_running/dog_running_3.png").resize((60,60)),
         Image.open("/home/choisuyeon/ESW/frame_dog_running/dog_running_4.png").resize((60,60)),
         Image.open("/home/choisuyeon/ESW/frame_dog_running/dog_running_5.png").resize((60,60)),
         Image.open("/home/choisuyeon/ESW/frame_dog_running/dog_running_6.png").resize((60,60)),
         Image.open("/home/choisuyeon/ESW/frame_dog_running/dog_running_7.png").resize((60,60)),
         Image.open("/home/choisuyeon/ESW/frame_dog_running/dog_running_8.png").resize((60,60))]


CARROT=Image.open("/home/choisuyeon/ESW/carrot.png").resize((30,30))
STAR=Image.open("/home/choisuyeon/ESW/star.png").resize((30,30))

BG=Image.open("/home/choisuyeon/ESW/background.png").resize((240,240))

command="unknown"

class Rabbit():
    X_POS=20
    Y_POS=170
    Y_POS_SLIDE=180
    JUMP_VEL=3.5

    def __init__(self):
        self.slide_img=RABBIT_SLIDING
        self.run_img=RABBIT_RUNNING
        self.jump_img=RABBIT_JUMPING

        self.rabbit_slide=False
        self.rabbit_run=True
        self.rabbit_jump=False

        
        self.jump_vel=self.JUMP_VEL
        self.image=self.run_img[0]

        
        self.run_image_index=0

        self.rabbit_x=self.X_POS
        self.rabbit_y=self.Y_POS

    def update(self,command):
        if self.rabbit_slide:
            self.slide()

        if self.rabbit_run:
            self.run()
            
        if self.rabbit_jump:
            self.jump()

        

        if command == 'up_pressed' and not self.rabbit_jump:
            self.rabbit_slide=False
            self.rabbit_run=False
            self.rabbit_jump=True
        elif command == 'down_pressed' and not self.rabbit_jump:
            self.rabbit_slide=True
            self.rabbit_run=False
            self.rabbit_jump=False
        elif not(self.rabbit_jump or command == 'down_pressed'):
            self.rabbit_slide=False
            self.rabbit_run=True
            self.rabbit_jump=False

    def slide(self):
        self.image=self.slide_img
                   
        self.rabbit_x=self.X_POS
        self.rabbit_y=self.Y_POS_SLIDE
            

    def run(self):
        self.image= self.run_img[self.run_image_index % len(self.run_img)]
        self.run_image_index = (self.run_image_index + 1) % len(self.run_img)
            
        self.rabbit_x=self.X_POS
        self.rabbit_y=self.Y_POS
            

    def jump(self):
        self.image=self.jump_img
        if self.rabbit_jump:
            self.rabbit_y-=self.jump_vel*4
            self.jump_vel-=0.8

        if self.jump_vel<-self.JUMP_VEL:
            self.rabbit_jump=False
            self.jump_vel=self.JUMP_VEL


    def draw(self,SCREEN):
        SCREEN.paste(SCREEN,(self.rabbit_x,self.rabbit_y),SCREEN)
        
        




global game_speed,x_pos_bg,y_pos_bg,obstacles


    
    
game_speed=8

x_pos_bg=0
y_pos_bg=0
points=0
    
obstacles=[]
death_count=0


while True:
    
    screen = Image.new("RGBA", (joystick.width, joystick.height), (255, 255, 255))
    
    screen.paste(BG,(0,0),BG)
    screen.paste(RABBIT_RUNNING[0],(0,180),RABBIT_RUNNING[0])
    joystick.disp.image(screen)
    
    
    '''
    if not joystick.button_U.value:
        command='up_pressed'
    if not joystick.button_D.value:
        command='down_pressed'

    player.update(command)
    player.draw(screen)
        
    joystick.disp.image(screen)
    
    
    '''
    
        



