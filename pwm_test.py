import gpiozero as gz
from time import sleep
from math import sqrt

en = gz.LED(26)
en.off()
motor = gz.PWMOutputDevice(13)

def run_motor_with_axeleration_hz_in_sqr_sec(target_frequency, axeleration):
    '''set axeleration in hz/sec2'''
    
    for f in range(target_frequency):
        motor.frequency = f
        motor.value = 0.5
        sleep(sqrt(1/axeleration))
        print(f)





try:
    run_motor_with_axeleration_hz_in_sqr_sec(3000, 1000)

            # while True:
            #     motor.value = 0.5 # duty cycle, how much time of the period state is high (0-100%)
    pass
except KeyboardInterrupt:
    motor.value = 0
    pass