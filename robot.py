import asyncio
import math
import time

from motor import Motor
from pins_table import pins

from camera import camera
from neuron import neuron
from interface import interface
from pumps import pump_station

from wrapper import _timing


class Axis:
	def __init__(self, name_axis, motor):
		self.print_on = True

		self.name_axis = name_axis

		self.motor = motor

		self.distance_move = 0
		self.ready = False

		self.limit_min = 0
		self.limit_max = 0
		self.error_limit = False

		self.arm_lenght = 1

		self.angle_0 = 0
		self.angle = 0
		self.delta_angle = 0
		self.step_angle = 0.15

		self.step_distance = 0

		self.direction_real = True
		self.direction_distance = True

		self.x0 = 0
		self.y0 = 0
		self.z0 = 0
		self.x = 0
		self.y = 0
		self.z = 0

		self.d1 = 0


	
	def angle_real(self):
		if self.direction_real:
			angle_real = self.angle_0 - self.motor.value * self.step_angle
		else:
			angle_real = self.angle_0 - self.motor.value * self.step_angle

		print(f'angle_real {self.name_axis}: {angle_real}')
		print(f'angle_real {self.name_axis} motor value: {self.motor.value}')

		return angle_real


	def distance_angle(self, angle):
		delta_angle = self.angle_real() - angle

		delta_angle = round(delta_angle, 1)

		return delta_angle


	def angle_to_step(self, angle):
		if self.print_on: 
			print('angle_to_step, input:', angle)

		delta_angle = self.distance_angle(angle)
		distance = delta_angle / self.step_angle

		if self.print_on: 
			print('angle_to_step',self.name_axis, angle, 'distance_angle', delta_angle, 'distance', distance)
			print()

		return distance
	


class Robot:
	def __init__(self):
		self.print_on = True

		self.first_go = False

		self.calibration_ready = True
		self.calib_distance = 1000

		self.stopped = False

		self.lenght_filler = 4.5

		self.step_position_value = 300
		self.step_position = 0

		self.radius_min = 14
		self.radius_max = 26

		self.home = False

		self.error_x = False
		self.error_y = False
		self.error_z = False

		self.motor_x = Motor('x', pins.motor_x_step, pins.motor_x_dir, pins.motor_x_enable)
		self.motor_y = Motor('y', pins.motor_y_step, pins.motor_y_dir, pins.motor_y_enable)
		self.motor_z = Motor('z', pins.motor_z_step, pins.motor_z_dir, pins.motor_z_enable)

		self.distance_x = 0
		self.distance_y = 0
		self.distance_z = 0

		self.axis_x = Axis('motor_x', self.motor_x)
		self.axis_x.motor.speed_def = 0.00005
		self.axis_x.motor.direction = True
		self.axis_x.step_angle = 0.062
		self.axis_x.angle_0 = 0
		self.axis_x.angle = self.axis_x.angle_0
		self.axis_x.limit_min = -90
		self.axis_x.limit_max = 90

		self.axis_y = Axis('motor_y', self.motor_y)
		self.axis_y.motor.speed_def = 0.00005
		self.axis_y.motor.direction = False
		self.axis_y.step_angle = 0.13
		self.axis_y.arm_lenght = 12
		self.axis_y.angle_0 = 122
		self.axis_y.angle = self.axis_y.angle_0
		self.axis_y.y0 = 0
		self.axis_y.z0 = 20.5
		self.axis_y.limit_min = 2
		self.axis_y.limit_max = 122

		self.axis_z = Axis('motor_z', self.motor_z)
		self.axis_z.motor.speed_def = 0.0002
		self.axis_z.motor.direction = True
		self.axis_z.direction_real = False
		self.axis_z.direction_distance = False
		self.axis_z.step_angle = 0.116
		self.axis_z.arm_lenght = 12
		self.axis_z.angle_0 = 145
		self.axis_z.angle = self.axis_z.angle_0
		self.axis_z.limit_min = 145
		self.axis_z.limit_max = 95


	def run(self):
		if self.calibration_ready:
			neuron.memory_objects = self.move_objects(neuron.list_coord, neuron.objects)


	def null_value(self):
		self.axis_x.motor.null_value()
		self.axis_y.motor.null_value()
		self.axis_z.motor.null_value()


	def angle_to_coord(self, angle_x, angle_y, angle_z):
		x = 0
		y = 0
		z = 0

		error_limit_x = False
		error_limit_y = False
		error_limit_z = False

		angle_x1 = angle_x
		angle_y1 = angle_y
		angle_z1 = angle_z

		if angle_x < self.axis_x.limit_min:
			angle_x = self.axis_x.limit_min
			error_limit_x = True

		if angle_x > self.axis_x.limit_max:
			angle_x = self.axis_x.limit_max
			error_limit_x = True

		if angle_y < self.axis_y.limit_min:
			angle_y = self.axis_y.limit_min
			error_limit_y = True

		if angle_y > self.axis_y.limit_max:
			angle_y = self.axis_y.limit_max
			error_limit_y = True

		#print(angle_z, self.axis_z.limit_min)
		if angle_z > self.axis_z.limit_min:
			angle_z = self.axis_z.limit_min
			error_limit_z = True

		if self.axis_z.angle >= 60:
			limit_z2 = self.axis_z.angle_0 - angle_y 
		else:
			limit_z2 = 60

		#print(angle_z, self.axis_z.limit_max - limit_z2,  limit_z2)
		if angle_z < self.axis_z.limit_max - limit_z2:
			angle_z = self.axis_z.limit_max + limit_z2
			error_limit_z = True


		#print(angle_x1, angle_y1, angle_z1)

		y1 = self.axis_y.y0 + self.axis_y.arm_lenght * math.cos(math.radians(angle_y1))
		z1 = self.axis_y.z0 + self.axis_y.arm_lenght * math.sin(math.radians(angle_y1))

		#print(round(x, 5), round(y1, 5), round(z1, 5))

		y2 = y1 + self.axis_z.arm_lenght * math.cos(math.radians(angle_z1 - angle_y))
		z2 = z1 - self.axis_z.arm_lenght * math.sin(math.radians(angle_z1 - angle_y))

		#print(round(x, 5), round(y2, 5), round(z2, 5))

		x3 = (y2 + self.lenght_filler) * math.sin(math.radians(angle_x1))
		y3 = (y2 + self.lenght_filler) * math.cos(math.radians(angle_x1)) 
		z3 = z2

		x = round(x3, 3)
		y = round(y3, 3)
		z = round(z3, 3)

		#print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz', x, y, z, error_limit_x, error_limit_y, error_limit_z)

		return x, y, z, error_limit_x, error_limit_y, error_limit_z
	

	@_timing(True)
	def find_angle(self, x0, y0, z0):
		angle_x = self.axis_x.angle_0
		angle_y = self.axis_y.angle_0
		angle_z = self.axis_z.angle_0

		h = 1
		i = 0

		error = False

		while True:
			x, y, z, error_limit_x, error_limit_y, error_limit_z = self.angle_to_coord(angle_x, angle_y, angle_z)

			if y <= y0:
				if error_limit_y == False:
					angle_y -= 1* h

				if error_limit_z == False:
					angle_z -= 1 * h
			else:
				h = 0.1

				if error_limit_x == False:
					if x0 > 0:
						if x < x0:
							angle_x += 1 * h
					elif x0 < 0:
						if x > x0:
							angle_x -= 1 * h
			
				if abs(x) >= abs(x0):
					if z <= z0:
						if error_limit_y == False:
							angle_y -= 1 * h

						if error_limit_z == False:
							angle_z -= 2 * h
					else:

						angle_y += 1 * h

						angle_z += 2 * h
					
			if error_limit_y == True:
				angle_y += 1
				angle_z -= 1

			i += 1
			#print(i)
			
			if abs(x) >= abs(x0) and y >= y0 and z <= z0:
				break

			if i > 10000:
				error = True
				print('Error position', abs(x) >= abs(x0), y >= y0, z <= z0)
				break

		angle_x = round(angle_x, 3)
		angle_y = round(angle_y, 3)
		angle_z = round(angle_z, 3)

		print(f"angle_x: {angle_x} x: {x}")
		print(f"angle_y: {angle_y} y: {y}")
		print(f"angle_z: {angle_z} z: {z}")
		print('x0, y0, z0', x0, y0, z0)

		return angle_x, angle_y, angle_z, error
	

	def steps_find(self, angle_y, angle_z):
		delta_y = self.axis_y.distance_angle(angle_y)

		angle_real = self.axis_z.angle_0 - self.axis_z.motor.value * self.axis_z.step_angle


		# print('self.axis_z.motor.value', self.axis_z.motor.value)
		# self.axis_z.motor.value = (self.axis_z.motor.value * self.axis_z.step_angle + delta_y) / self.axis_z.step_angle 
		# print('self.axis_z.motor.value2', self.axis_z.motor.value)

		print('angle_real', angle_real, angle_z)
	
		
		new_angle_z = angle_real - delta_y

		if new_angle_z < 35:
			new_angle_z = 35
		

		print('new_angle_z, angle_z', new_angle_z, angle_z)

		delta_z = abs(new_angle_z - angle_z)


		if new_angle_z < angle_real:
			delta_z = delta_z
		else:
			delta_z = -delta_z


		# print('delta_z', delta_z)

		distante_z = delta_z / self.axis_z.step_angle

		return distante_z
		

	async def _detect_sensor(self):
		while True:
			if self.stopped:
				break

			
			await asyncio.sleep(0.0001)

	
	async def _limit(self):
		while True:
			if self.stopped:
				break

			# if self.axis_y.motor.value <= 300 and self.axis_y.motor.ready == False:
			# 	self.axis_z.motor.stop_for = True
			# else:
			# 	self.axis_z.motor.stop_for = False
			
			await asyncio.sleep(0.0001)


	async def _move_async(self, distance_x, distance_y, distance_z, detect = False):
		self.stopped = False
		tasks = []

		if detect:
			sensor_task = asyncio.create_task(self._detect_sensor())

		limit_task = asyncio.create_task(self._limit())

		if distance_x != 0:
			tasks.append(asyncio.create_task(self.axis_x.motor.move(distance_x, async_mode=True)))
		
		if distance_y != 0:
			tasks.append(asyncio.create_task(self.axis_y.motor.move(distance_y, async_mode=True)))

		if distance_z != 0:
			tasks.append(asyncio.create_task(self.axis_z.motor.move(distance_z, async_mode=True)))
			
		try:
			await asyncio.gather(*tasks)
		except asyncio.CancelledError:
			for task in tasks:
				if not task.done():
					task.cancel()

		self.stopped = True

		if detect:
			sensor_task.cancel()
		
		limit_task.cancel()


	def move(self, distance_x, distance_y, distance_z):
		asyncio.run(self._move_async(distance_x, distance_y, distance_z))


	def go_to_point(self, x, y, z):
		if self.print_on: 
			print('go_to_point, input:', 'x, y, z', x, y, z)
			print()
		
		angle_x0 = self.axis_x.angle_real()
		angle_y0 = self.axis_y.angle_real()
		angle_z0 = self.axis_z.angle_real()

		x0, y0, z0, _, _, _ = self.angle_to_coord(angle_x0, angle_y0, angle_z0)
		if self.print_on:
			print('go_to_point', 'x0, y0, z0', x0, y0, z0)
			print('go_to_point', 'angle_x0, angle_y0, angle_z0', angle_x0, angle_y0, angle_z0)
			print()

		angle_x, angle_y, angle_z, error = self.find_angle(x, y, z)
		if self.print_on:
			print('go_to_point, self.find_angle', 'angle_x, angle_y, angle_z,', angle_x, angle_y, angle_z)

		x1, y1, z1, _, _, _ = self.angle_to_coord(angle_x, angle_y, angle_z)
		if self.print_on:
			print('go_to_point','proverka' , 'x, y, z', x1, y1, z1)
			print()

		error_x = abs(x1 - x)
		error_y = abs(y1 - y)
		error_z = abs(z1 - z)

		if self.print_on:
			print('go_to_point','error', 'error_x, error_y, error_z', error_x, error_y, error_z)
			print()
		
		if error_x > 1 or error_y > 1 or error_z > 1:
			pass

		
		self.distance_x = self.axis_x.angle_to_step(angle_x)
		self.distance_y = self.axis_y.angle_to_step(angle_y)

		if self.home == False:
			self.distance_z = self.steps_find(angle_y, angle_z)
		else:
			self.distance_z = self.axis_z.angle_to_step(angle_z)

		self.home = False

		if self.print_on:
			print('go_to_point', 'distance_x, distance_y, distance_z', self.distance_x, self.distance_y, self.distance_z)
			print()

		#input('GO???')
		self.move(self.distance_x, self.distance_y, self.distance_z)
		
		print('go_to_point Приехал в координаты:', 
			'x:', x1, 'angle x:', self.axis_x.angle_real(),
			'y:', y1, 'angle y:', self.axis_y.angle_real(), 
			'z:', z1, 'angle z:', self.axis_z.angle_real())
		

		#input('&&&&&')
		#time.sleep(1)



	def check_limit(self, x, y, z):
		limit_check = False

		radius = math.sqrt((x**2) + (y**2))

		if self.radius_min <= radius <= self.radius_max:
			limit_check = True
		else:
			limit_check = False

		if self.print_on:
			print('check_limit radius', radius, limit_check)

		return limit_check


	def move_objects(self, list_coord, list_objects):
		if self.print_on:
			print('move_objects list_objects', list_objects)
			print('move_objects list_coord', list_coord)

		i = 0
		limit = False

		for coord in list_coord:
			x, y, z = coord

			limit = self.check_limit(x, y, z)

			if list_objects[i][0] == False and limit == True:
				z = z + 2
				
				self.go_to_point(x, y, z)

				camera.read_cam()

				interface.show_img()

				if y >= 10 * (1 + z/20):
					neuron.find_objects()

					try:
						value = neuron.objects[i][4]
					except:
						value = 0
					finally:
						if abs(list_objects[i][4] - value) < neuron.region_x:
							pump_station.run()

							list_objects[i][0] = True
				else:
					pump_station.run()
					list_objects[i][0] = True
				
				self.go_home()

			i += 1

			interface.show_img()

		return list_objects
	

	def calibration(self):
		self.move(3000, 0, 0, detect = True)
		self.move(self.calib_distance, 0, 0)

		self.calibration_ready = True


	def go_home(self):
		self.home = True 
		self.go_to_point(0, 9, 27)
		self.motor_y.move(-20)
		self.null_value()


		print('go home')

	
	def correction(self, list_coord):
		x = round(list_coord[0])
		y = round(list_coord[1])

		list_correction_y = neuron.memory_read('correction.txt', y)
		print(list_correction_y)

		try:
			correction_x = list_correction_y[x]
			correction_x = 0
			print('такой ключ есть')
			input() 
		except KeyError:
			correction_x = 1

		distance_x = 0
		distance_y = 0

		while list_correction_y != 0 and correction_x != 0:
			axis = input()

			if axis == 'x':
				distance_x = int(input(f'distance {axis}'))
				self.motor_x.move(distance_x)
			
			if axis == 'y':
				distance_y = int(input(f'distance {axis}'))
				self.motor_y.move(distance_y)

			if axis == 'p':
				neuron.memory_write('correction.txt', y, list_correction_y)
				print(f'Save {list_correction_y[x]}')
				list_correction_y[x] = (distance_x, distance_y)
	
				break


robot = Robot()


if __name__ == '__main__':
	# #self.axis_z.init_go_axis(115)
	# self.axis_z.go_axis(1, 115)

	# #self.axis_z.init_go_axis(110)
	# self.axis_z.go_axis(1, 110)

	# #self.axis_z.init_go_axis(145)
	# self.axis_z.go_axis(1, 145)
     
	# #robot.go_to_point(11, 11 , 13)

	# self.axis_x.go_axis(1, 16)
	# self.axis_y.go_axis(1, 25.8)
	# self.axis_z.go_axis(1, 104)

	robot.go_to_point(-12.8, 12.8, 11)
	robot.go_home()

	robot.go_to_point(0, 16.8, 15)
	robot.go_home()
	
	robot.go_to_point(12.8, 16.8, 11)
	robot.go_home()

	robot.go_to_point(0, 16.5, 15)
	robot.go_home()

	robot.go_to_point(-12.8, 16.5, 11)
	robot.go_home()
