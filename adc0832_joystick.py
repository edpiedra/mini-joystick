import RPi.GPIO as GPIO 
import time, math 

class ADC0832():
    
    def __init__(self):
        self.ADC_CS = 17
        self.ADC_CLK = 18
        self.ADC_DIO = 27
        
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.ADC_CS, GPIO.OUT)
        GPIO.setup(self.ADC_CLK, GPIO.OUT)
        
    def _get_result(self, channel):
        GPIO.setup(self.ADC_DIO, GPIO.OUT)
        GPIO.output(self.ADC_CS, GPIO.LOW)
        GPIO.output(self.ADC_CLK, GPIO.LOW)
        
        GPIO.output(self.ADC_DIO, GPIO.HIGH); time.sleep(0.000002)
        GPIO.output(self.ADC_CLK, GPIO.HIGH); time.sleep(0.000002)
        GPIO.output(self.ADC_CLK, GPIO.LOW)
        
        GPIO.output(self.ADC_DIO, GPIO.HIGH); time.sleep(0.000002)
        GPIO.output(self.ADC_CLK, GPIO.HIGH); time.sleep(0.000002)
        GPIO.output(self.ADC_CLK, GPIO.LOW)

        GPIO.output(self.ADC_DIO, channel); time.sleep(0.000002)
        
        GPIO.output(self.ADC_CLK, GPIO.HIGH)
        GPIO.output(self.ADC_DIO, GPIO.HIGH); time.sleep(0.000002)
        GPIO.output(self.ADC_CLK, GPIO.LOW)
        GPIO.output(self.ADC_DIO, GPIO.HIGH); time.sleep(0.000002)
        
        dat1 = 0
        for i in range(0,8):
            GPIO.output(self.ADC_CLK, GPIO.HIGH); time.sleep(0.000002)
            GPIO.output(self.ADC_CLK, GPIO.LOW); time.sleep(0.000002)
            GPIO.setup(self.ADC_DIO, GPIO.IN)
            dat1 = dat1 << 1 | GPIO.input(self.ADC_DIO)
            
        dat2 = 0
        for i in range(0,8):
            dat2 = dat2 | GPIO.input(self.ADC_DIO) << i
            GPIO.output(self.ADC_CLK, GPIO.HIGH); time.sleep(0.000002)
            GPIO.output(self.ADC_CLK, GPIO.LOW); time.sleep(0.000002)
            
        GPIO.output(self.ADC_CS, GPIO.HIGH)
        GPIO.setup(self.ADC_DIO, GPIO.OUT)
        
        if dat1==dat2:
            return dat1
            
        else:
            return 0
        
    def _destroy(self):
        GPIO.cleanup()
        
class Joystick():
    
    def __init__(self):
        self.adc = ADC0832()
        self.button = 40
        GPIO.setup(self.button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        self.right_pan = 140
        self.right_tilt = 50
        self.left_pan = 10
        self.left_tilt = 80
        self.pan_max_step = 10
        self.tilt_max_step = 10
        
    def _retrieve_differential_speed(self):
        x = self.adc._get_result(1)
        y = self.adc._get_result(0)
        
        print("raw:", x, y)
        
        x = (((255-x) - 128) / 128)
        y = ((255-y) - 128) / 128
        
        if 0.1 > x > -0.1: x=0
        if 0.1 > y > -0.1: y=0
        
        if not(x==0):
            deg = math.atan(abs(y)/abs(x)) * 90 / (math.pi/2)
        else:
            deg = 90
            
        print("deg:", deg)
        
        if deg >= 45:
            primary_motor_speed = y
        elif (x>=0 and y>=0) or (x<0 and y<0):
            primary_motor_speed = x
        else:
            primary_motor_speed = -x
            
        secondary_motor_proportion = (deg-45) / 45
        secondary_motor_speed = primary_motor_speed * secondary_motor_proportion
        
        if (y>=0 and x>=0) or (y<0 and x<0):
            left_wheel_speed = primary_motor_speed
            right_wheel_speed = secondary_motor_speed
        else:
            right_wheel_speed = primary_motor_speed
            left_wheel_speed = secondary_motor_speed
            
        print(left_wheel_speed, right_wheel_speed)
            
        return left_wheel_speed, right_wheel_speed
    
    def _destroy(self):
        self.adc._destroy()
