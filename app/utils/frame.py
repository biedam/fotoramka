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
from utils.photo import Orientation
import logging

logger = logging.getLogger(__name__)


I2C_BUS         = 0x01             #default use I2C1
IMU_ADDRESS     = 0x19             #sensor address 1
SERVO_GPIO      = 12               #GPIO with PWM: 12,13,18,19

VERTICAL_ANGLE = 90
HORIZONTAL_ANGLE = 0
VERT_TO_HOR_SRV = 1400
HOR_TO_VERT_SRV = 1570
STOP_SRV = 1460


#servo zero position is betwean pulsewidth 1430 - 1490, midpoint 1460
#using rotation +/- 50 from midpoint (1410 and 1510) rotation for 90 deg takes about 12s

imu = DFRobot_IIS2DLPC_I2C(I2C_BUS ,IMU_ADDRESS)
#use PiGPIO daemon library to reduce sevo jitter
#my_factory = PiGPIOFactory()

#servo = Servo(SERVO_GPIO, pin_factory=my_factory)


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
        #print(f"Acceleration: ({x}, {y})")
        angle = np.degrees(np.arctan(-x/y))
        if y < 0:
            angle = 180 + angle

        #print(f"Angle: {angle}")
        return angle

    def rotate(self, direction):
        #in horizontal position angle = 0 in vertical position angle = 90
        #servo = 1400 -> rotation from vertical to horizontal
        #servo = 1520 -> rotation from horizontal to vertical
        gpio = pigpio.pi()
        gpio.set_mode(SERVO_GPIO, pigpio.OUTPUT)
        logger.info(f"Rotating to {direction}")
        if direction == Orientation.VERTICAL:
            while self.orientation() < VERTICAL_ANGLE:
                gpio.set_servo_pulsewidth(SERVO_GPIO, HOR_TO_VERT_SRV)
                time.sleep(0.001)
        elif direction == Orientation.HORIZONTAL:
            while self.orientation() > HORIZONTAL_ANGLE:
                gpio.set_servo_pulsewidth(SERVO_GPIO, VERT_TO_HOR_SRV)
                time.sleep(0.001)

        gpio.set_servo_pulsewidth(SERVO_GPIO, STOP_SRV)  # middle position
        gpio.set_servo_pulsewidth(SERVO_GPIO, 0)
        gpio.stop()
        logger.info(f"angle = {self.orientation()}")


            

