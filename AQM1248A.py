# LCD Graphic module AQM1248A for Raspberry Pi/Python3
import RPi.GPIO as GPIO
import spidev
from time import sleep
from PIL import Image
from PIL import ImageOps
from PIL import ImageDraw
from PIL import ImageFont

# ref) https://sakura87.net/archives/2171
# ref) https://github.com/nobukuma/MicroPythonSushiRotator

class LCD:
    ''' LCD graphic module AQM1248A library '''

    # LCD SETTING
    WIDTH = 128
    HEIGHT = 48
    PAGE_COUNT = 6

    # DEBUG
    cnt = 0
    DEBUG = False

    def __init__(self, rs_port=24, cs_port=8, reset_port=23):
        ''' Init Object '''
        # set member
        self.rs_port = rs_port
        self.cs_port = cs_port
        self.reset_port = reset_port
        
        # init GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(rs_port, GPIO.OUT)
        GPIO.setup(cs_port, GPIO.OUT)
        GPIO.setup(reset_port, GPIO.OUT)
        
        # init SPI
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 1000000 

        self.init_lcd()


    def send_command(self, command):
        GPIO.output(self.rs_port, GPIO.LOW)
        # GPIO.output(self.cs_port, GPIO.LOW)
        self.spi.xfer([command])
        # GPIO.output(self.rs_port, GPIO.HIGH)
        # GPIO.output(self.cs_port, GPIO.HIGH)
        if self.DEBUG:
            print( "{0:04X}: {1:04X}".format(self.cnt, command) )
        self.cnt += 1

    def send_command_list(self, command_list, interval=0):
        for cmd in command_list:
            self.send_command(cmd)
            if interval > 0:
                sleep(interval / 1000)
        
    def send_data(self, data):
        GPIO.output(self.rs_port, GPIO.HIGH)
        # GPIO.output(self.cs_port, GPIO.LOW)
        self.spi.xfer(data)
        # GPIO.output(self.rs_port, GPIO.HIGH)
        # GPIO.output(self.cs_port, GPIO.HIGH)
        if self.DEBUG:
            print("data=", data, ":", len(data))

    def select_page(self, page):
        self.send_command(0xB0 | (page & 0xF))
        
    def select_col(self, col):
        self.send_command(0x00 | (col & 0xF)) # SET COLUMN LOWER
        self.send_command(0x10 | ((col >> 4) & 0xF)) # SET COLUMN UPPER
    
    def reset(self):
        ''' Reset LCD '''
        GPIO.output(self.reset_port, GPIO.LOW)
        sleep(0.1)
        GPIO.output(self.reset_port, GPIO.HIGH)

    def init_lcd(self):
        ''' init LCD '''
        # CS Chip Select Low
        GPIO.output(self.cs_port, GPIO.LOW)
        # Reset
        self.reset()
        sleep(0.002)
        # 液晶初期化コマンド送信
        # 表示オフ→ADC設定→Common Output設定→バイアス設定
        self.send_command_list([0xAE, 0xA0, 0xC8, 0xA3])
        # 内部レギュレーターをオンにする
        self.send_command_list([0x2C, 0x2E, 0x2F], 2)
        # コントラスト設定
        self.send_command_list([0x23,0x81, 0x1C])
        # 表示設定
        # 全点灯オフ→スタートライン →通常表示→表示オン
        self.send_command_list([0xA4, 0x40, 0xA6, 0xAF])
        #
        # 液晶カーソル初期化
        # self.send_command_list([0xB0, 0x10, 0x00])
        #
        self.clear_display()

    def set_contrast(self, v = 0x1C):
        ''' set contrast level (0-0x3F) '''
        self.send_command_list([0x23, 0x81, (v & 0x3F)])

    def make_image_buffer(self, image):
        ''' set image data '''
        # size
        (w, h) = image.size
        if w != self.WIDTH or h != self.HEIGHT:
            image = image.resize((WIDTH, HEIGHT))
            (w, h) = image.size
        # grayscale
        image = ImageOps.grayscale(image)
        idata = list(image.getdata())
        c2 = lambda v : 0 if v >= 128 else 1
        buf = [0] * (self.PAGE_COUNT * self.WIDTH)
        for page in range(0, self.PAGE_COUNT):
            for col in range(0, self.WIDTH):
                i = page * self.WIDTH + col
                v = c2(idata[(page * 8) * w + col])
                for j in range(1, 8):
                    v |= c2(idata[(page * 8 + j) * w + col]) << j
                buf[i] = v
        return buf

    def show_buffer(self, buf):
        ''' show image '''
        for page in range(0, self.PAGE_COUNT):
            self.select_page(page)
            self.select_col(0)
            i1 = page * self.WIDTH
            i2 = (page + 1) * self.WIDTH
            self.send_data(buf[i1:i2])

    def show(self, image):
        ''' show image '''
        self.send_command(0xAE)
        buf = self.make_image_buffer(image)
        self.show_buffer(buf)
        self.send_command(0xAF)

    def clear_display(self):
        buf = [0] * (self.PAGE_COUNT * self.WIDTH)
        self.show_buffer(buf)
        
    def full_display(self):
        buf = [255] * (self.PAGE_COUNT * self.WIDTH)
        self.show_buffer(buf)

    def close(self):
        self.spi.close()

# --- test code ---
def test1():
    disp = LCD()
    disp.full_display()
    disp.close()

def test2():
    # draw png image
    disp = LCD()
    image = Image.open('test.png')
    disp.show(image)
    disp.close()

def test3():
    # font drawing
    path = '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf'
    # text
    disp = LCD()
    image = Image.new('1', (disp.WIDTH, disp.HEIGHT), 0)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0,0,disp.WIDTH, disp.HEIGHT), outline=1, fill=1)
    f = ImageFont.truetype(path, 20, encoding='unic')
    draw.text((0,  0), "Raspberry Pi", font=f, fill=0)
    draw.text((0, 24), "夏目漱石", font=f, fill=0)
    disp.show(image)
    disp.close()

# test code
if __name__ == '__main__':
    test3()


