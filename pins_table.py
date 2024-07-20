# import gpiod


# class Pins():
#     def __init__(self):
#         self.motor_step = 26
#         self.motor_dir = 19
#         self.motor_enable = 13

#         self.button_stop = 14
#         self.button = 5
#         self.switch_out = 8
#         self.switch_in = 6

#         self.switch_x = 25

#         self.motor_x_step = 22
#         self.motor_x_dir = 27
#         self.motor_x_enable = 17

#         self.motor_y_step = 4
#         self.motor_y_dir = 3
#         self.motor_y_enable = 2

#         self.motor_z_step = 21
#         self.motor_z_dir = 20
#         self.motor_z_enable = 16

#         self.motor_p1_step = 18
#         self.motor_p1_dir = 15
        
#         self.motor_p2_step = 23
#         self.motor_p2_dir = 24

#         self.motor_p1p2_enable = 7

#         self.chip = gpiod.Chip("/dev/gpiochip4")
#         self.req = self.chip.request_lines(consumer="rpi-acloud-gpio-basic",
#             config = {
#                 self.button: gpiod.LineSettings(direction = gpiod.line.Direction.OUTPUT),
#                 self.button_stop: gpiod.LineSettings(direction = gpiod.line.Direction.OUTPUT),
                
#                 self.switch_out: gpiod.LineSettings(direction = gpiod.line.Direction.OUTPUT),
#                 self.switch_in: gpiod.LineSettings(direction = gpiod.line.Direction.OUTPUT),
#                 self.switch_x: gpiod.LineSettings(direction = gpiod.line.Direction.OUTPUT),

#                 self.motor_step: gpiod.LineSettings(direction = gpiod.line.Direction.OUTPUT),
#                 self.motor_dir: gpiod.LineSettings(direction = gpiod.line.Direction.OUTPUT),
#                 self.motor_enable: gpiod.LineSettings(direction = gpiod.line.Direction.OUTPUT),

#                 self.motor_x_step: gpiod.LineSettings(direction = gpiod.line.Direction.OUTPUT),
#                 self.motor_x_dir: gpiod.LineSettings(direction = gpiod.line.Direction.OUTPUT),
#                 self.motor_x_enable: gpiod.LineSettings(direction = gpiod.line.Direction.OUTPUT),

#                 self.motor_y_step: gpiod.LineSettings(direction = gpiod.line.Direction.OUTPUT),
#                 self.motor_y_dir: gpiod.LineSettings(direction = gpiod.line.Direction.OUTPUT),
#                 self.motor_y_enable: gpiod.LineSettings(direction = gpiod.line.Direction.OUTPUT),

#                 self.motor_z_step: gpiod.LineSettings(direction = gpiod.line.Direction.OUTPUT),
#                 self.motor_z_dir: gpiod.LineSettings(direction = gpiod.line.Direction.OUTPUT),
#                 self.motor_z_enable: gpiod.LineSettings(direction = gpiod.line.Direction.OUTPUT),

#                 self.motor_p1_step: gpiod.LineSettings(direction = gpiod.line.Direction.OUTPUT),
#                 self.motor_p1_dir: gpiod.LineSettings(direction = gpiod.line.Direction.OUTPUT),

#                 self.motor_p2_step: gpiod.LineSettings(direction = gpiod.line.Direction.OUTPUT),
#                 self.motor_p2_dir: gpiod.LineSettings(direction = gpiod.line.Direction.OUTPUT),

#                 self.motor_p1p2_enable: gpiod.LineSettings(direction = gpiod.line.Direction.OUTPUT),
#             })


#     def get_value(self, pin, log = False):
#         if self.req.get_value(pin) == gpiod.line.Value.ACTIVE:
#             if log: print(f'pin: {pin} - ON')
#             return True
#         elif self.req.get_value(pin) == gpiod.line.Value.INACTIVE:
#             if log: print(f'pin: {pin} - OFF')
#             return False


#     def set_value(self, pin, value):
#         if value == True:
#             self.req.set_value(pin, gpiod.line.Value.ACTIVE)
#         else:
#             self.req.set_value(pin, gpiod.line.Value.INACTIVE)


# pins = Pins()


# import RPi.GPIO as GPIO

# class Pins():
#     def __init__(self):
#         self.motor_step = 26
#         self.motor_dir = 19
#         self.motor_enable = 13

#         self.button_stop = 14
#         self.button = 5
#         self.switch_out = 8
#         self.switch_in = 6

#         self.switch_x = 25

#         self.motor_x_step = 22
#         self.motor_x_dir = 27
#         self.motor_x_enable = 17

#         self.motor_y_step = 4
#         self.motor_y_dir = 3
#         self.motor_y_enable = 2

#         self.motor_z_step = 21
#         self.motor_z_dir = 20
#         self.motor_z_enable = 16

#         self.motor_p1_step = 18
#         self.motor_p1_dir = 15
         
#         self.motor_p2_step = 23
#         self.motor_p2_dir = 24

#         self.motor_p1p2_enable = 7

#         GPIO.setmode(GPIO.BCM)
#         GPIO.setwarnings(False)

#         pins = [
#             self.button, self.button_stop, self.switch_out, self.switch_in, self.switch_x,
#             self.motor_step, self.motor_dir, self.motor_enable,
#             self.motor_x_step, self.motor_x_dir, self.motor_x_enable,
#             self.motor_y_step, self.motor_y_dir, self.motor_y_enable,
#             self.motor_z_step, self.motor_z_dir, self.motor_z_enable,
#             self.motor_p1_step, self.motor_p1_dir,
#             self.motor_p2_step, self.motor_p2_dir,
#             self.motor_p1p2_enable
#         ]

#         for pin in pins:
#             GPIO.setup(pin, GPIO.OUT)

#     def get_value(self, pin, log=False):
#         value = GPIO.input(pin)
#         if value == GPIO.HIGH:
#             if log: print(f'pin: {pin} - ON')
#             return True
#         elif value == GPIO.LOW:
#             if log: print(f'pin: {pin} - OFF')
#             return False

#     def set_value(self, pin, value):
#         GPIO.output(pin, GPIO.HIGH if value else GPIO.LOW)

# pins = Pins()

# import gpiod

# class GPIODController:
#     def __init__(self, chip_name):
#         self.chip = gpiod.Chip(chip_name)
#         self.release_all_lines()

#     def release_all_lines(self):
#         for line_offset in range(self.chip.num_lines()):
#             line = self.chip.get_line(line_offset)
#             if line.is_requested():
#                 line.release()

#     def set_pin_value(self, pin_number, value):
#         line = self.chip.get_line(pin_number)
#         if not line.is_requested():
#             line.request(consumer="GPIODController", type=gpiod.LINE_REQ_DIR_OUT, default_val=0)
#         line.set_value(value)

#     def get_pin_value(self, pin_number):
#         line = self.chip.get_line(pin_number)
#         if not line.is_requested():
#             line.request(consumer="GPIODController", type=gpiod.LINE_REQ_DIR_OUT, default_val=0)
#         return line.get_value()

# # ������ �������������
# if __name__ == "__main__":
#     chip_name = "gpiochip4"  # ��� GPIO-����, �������� "gpiochip0"
#     pin_number = 17  # ����� GPIO-����, � ������� �� ������ ��������

#     controller = GPIODController(chip_name)

#     # ��������� �������� ����
#     controller.set_pin_value(pin_number, 1)

#     # ��������� �������� ����
#     value = controller.get_pin_value(pin_number)
#     print(f"Current pin value: {value}")

#     while True: 
#         value = controller.get_pin_value(25)
#         print(f"Current pin value: {value}")



import gpiod
import gpiozero as gz


class Pins():
    def __init__(self):
        self.chip = gpiod.Chip('gpiochip4')

        self.release_all_lines()
    
        self.motor_step = gz.PWMOutputDevice(13)

        self.motor_dir = self.pin_init(19)
        self.motor_enable = self.pin_init(26)

        self.button_stop = self.pin_init(14)
        self.button = self.pin_init(5)
        self.switch_out = self.pin_init(8)
        self.switch_in = self.pin_init(6)

        self.switch_x = self.pin_init(25)

        self.motor_x_step = self.pin_init(22)
        self.motor_x_dir = self.pin_init(27)
        self.motor_x_enable = self.pin_init(17)

        self.motor_y_step = self.pin_init(4)
        self.motor_y_dir = self.pin_init(3)
        self.motor_y_enable = self.pin_init(2)

        self.motor_z_step = self.pin_init(21)
        self.motor_z_dir = self.pin_init(20)
        self.motor_z_enable = self.pin_init(16)

        self.motor_p1_step = self.pin_init(18)
        self.motor_p1_dir = self.pin_init(15)
        
        self.motor_p2_step = self.pin_init(23)
        self.motor_p2_dir = self.pin_init(24)

        self.motor_p1p2_enable = self.pin_init(7)


    def release_all_lines(self):
        for line_offset in range(self.chip.num_lines()):
            line = self.chip.get_line(line_offset)
            if line.is_requested():
                line.release()


    def pin_init(self, pin_number):
        line = self.chip.get_line(pin_number)
        if not line.is_requested():
            line.request(consumer="GPIODController", type=gpiod.LINE_REQ_DIR_OUT, default_val=0)
        
        return line


pins = Pins()

import time 

if __name__ == "__main__":

    i = 0 
    value = 0

    while True: 
        value = pins.switch_x.get_value()
        print(f"Current pin value: {value}")

        pins.motor_x_enable.set_value(value)

        time.sleep(0.05)
