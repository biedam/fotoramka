#=============================================================================
#============================ FOTORAMKA project ==============================
#=============================================================================
# author            : biedam
# notes             : 
# license           : MIT
#=============================================================================

from .DFRobot_LIS2DW12 import *
import time
import sys
import numpy as np
#from gpiozero.pins.pigpio import PiGPIOFactory
#from gpiozero import Servo
import pigpio

I2C_BUS         = 0x01             #default use I2C1
IMU_ADDRESS     = 0x19             #sensor address 1
SERVO_GPIO      = 12               #GPIO with PWM: 12,13,18,19

#servo zero position is betwean pulsewidth 1430 - 1490, midpoint 1460
#using rotation +/- 50 from midpoint (1410 and 1510) rotation for 90 deg takes about 12s

imu = DFRobot_IIS2DLPC_I2C(I2C_BUS ,IMU_ADDRESS)
#use PiGPIO daemon library to reduce sevo jitter
#my_factory = PiGPIOFactory()

#servo = Servo(SERVO_GPIO, pin_factory=my_factory)
gpio = pigpio.pi()
gpio.set_mode(SERVO_GPIO, pigpio.OUTPUT)

class Frame:
    

    def __init__(self):
        print('Initialization of IMU')
        imu.begin()
        imu.soft_reset()
        imu.set_range(imu.RANGE_2G)
        imu.contin_refresh(True)
        imu.set_data_rate(imu.RATE_200HZ)
        imu.set_filter_path(imu.LPF)
        imu.set_filter_bandwidth(imu.RATE_DIV_4)
        imu.set_power_mode(imu.CONT_LOWPWRLOWNOISE2_14BIT)     

    def orientation(self):
        x = imu.read_acc_x()
        y = imu.read_acc_y()
        print(f"Acceleration: ({x}, {y})")
        angle = np.degrees(np.arctan(x/y))
        print(f"Angle: {angle}")
        return angle

    def rotate(self, direction):
        #servo.value = 0
        #servo.value = direction
        #time.sleep(0.5)
        #servo.value = 0
        gpio.set_servo_pulsewidth(SERVO_GPIO, direction)  # środek
        time.sleep(1)
        gpio.set_servo_pulsewidth(SERVO_GPIO, 1500)  # "prawa"
        # wyłącz serwo
        gpio.set_servo_pulsewidth(SERVO_GPIO, 0)
        gpio.stop()

            

