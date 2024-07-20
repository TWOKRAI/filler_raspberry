import asyncio
from math import sqrt



from wrapper import _timing, _log_input_output


class Motor:
	def __init__(self, name: str, pin_step, pin_direction, pin_enable):
		self.name = name

		self.stop_for = False
		
		self.pin_step = pin_step
		self.pin_direction = pin_direction
		self.pin_enable = pin_enable

		self.null_value()
		self.enable_on(False)

		self.value = 0
		self.distance = 0
		self.distance_step = 0
		self.ready = False

		self.direction = True
		
		self.speed_def = 0.00005
		self.speed_min = 0
		self.speed = 0
		
		self.acc_run = True
		self.acc_start = 30
		self.k = 20
		self.distance_start = 0
		self.distance_start_def = 30
		self.step_start = 0
		
		self.acc_end = 30
		self.distance_end = 0
		self.distance_end_def = 30
		self.step_end = 0

		self.limit_min = -2000
		self.limit_max = 2000
		self.error_limit = False
		self.stop = False

		self.data = []

    
	def null_value(self):
		self.value = 0
        

	def enable_on(self, on: bool):
		if on:
			self.pin_enable.set_value(1)
		else:
			self.pin_enable.set_value(0)
    
    
    
	def init_acceleration(self, distance: int, mode: bool = True, print_log = True) -> float:
		if self.acc_run:
			self.speed_min = self.speed_def * self.k

			if mode: 
				self.distance_start = abs(distance) / 100 * self.acc_start
				self.distance_end = abs(distance) / 100 * self.acc_end
			else: 
				self.distance_start = self.distance_start_def
				self.distance_end = self.distance_end_def 	

			if self.distance_start != 0:
				self.step_start = abs(self.speed_min - self.speed_def) / self.distance_start

			if self.distance_end != 0:
				self.step_end = abs(self.speed_min - self.speed_def) / self.distance_end

			if print_log:
				print('init_acceleration', self.acc_start, self.acc_end, self.step_start, self.step_start, self.speed_min)

			return self.speed_min
		else:
			return self.speed_def
        

	@_log_input_output(False)
	def acceleration(self, speed: float, step: int) -> float:
		if self.acc_run:
			if step < self.distance_start:
				speed = speed - self.step_start

			elif step >= self.distance_start and step < self.distance - self.distance_end:
				speed = self.speed_def
				
			elif step >= self.distance - self.distance_end:
				speed = speed + self.step_start
			
		return abs(speed)

	
	async def _move_async(self, distance: int, print_log = False):
		self.ready = False
		self.error_limit = False

		self.distance_step = 0
		self.data = []
		
		if print_log:
			print(f'{self.name} distance: {distance}')

		self.distance = abs(round(distance, 0))

		self.speed = self.init_acceleration(self.distance)

		if distance > 0:
			direction = True
		else:
			direction = False

		for step in range(int(self.distance)):
			if self.stop_for:
				print(f'{self.name}, self.stop_for')
				while self.stop_for:
					await asyncio.sleep(self.speed_def)
			
			if self.limit_min <= self.value and self.value >= self.limit_max:
				self.error_limit = True
				print(f'error limit {self.name}: {self.error_limit}')
				break
						
			if self.stop == True:
				break


			if direction == True:
				self.pin_direction.set_value(self.direction)

				self.value += 1
			else:
				self.pin_direction.set_value(not self.direction)

				self.value -= 1
			
			self.speed = self.acceleration(self.speed, step)


			self.pin_step.set_value(1)
			await asyncio.sleep(self.speed)

			self.pin_step.set_value(0)
			await asyncio.sleep(self.speed)

			self.data.append(self.speed)
			self.distance_step += 1 
			
			if print_log:
				print(f'{self.name} value: {self.value}, speed: {self.speed}')
				#input('&&')

		if not self.error_limit and not self.stop:
			self.ready = True

		if print_log:
			print(f'{self.name} ready: {self.ready}')


		self.stop_for = False
	

	@_timing(True)
	async def _freq_async(self, frequency, sec, distance):
		self.ready = False

		if distance >= 0:
			self.pin_direction.set_value(self.direction)
		else:
			self.pin_direction.set_value(not self.direction)

		acc = False

		time_distance = 0
		k = 0.01

		while True:
			if self.stop == True:
				break

			if acc == False:
				step = frequency * 1 / sec * k

				if step < 1: 
					step = 1

				print(step)

				stop_distance = abs(distance) / 1000 * 0.95

				for f in range(1, frequency, int(step)):
					if self.stop == True:
						break
					
					print(time_distance, stop_distance)

					self.pin_step.frequency = f
					self.pin_step.value = 0.5
					print(f)

					time_distance += k
					await asyncio.sleep(k)

					if time_distance >= sec:
						break

				
				acc = True

			time_distance += k
			print(time_distance)
			await asyncio.sleep(k)
						
			if time_distance >= stop_distance - sec:
				break
			
					
		for f in range(frequency, -1, -int(step)):
			self.pin_step.frequency = f
			self.pin_step.value = 0.5
			
			time_distance += k
			print(time_distance)
			await asyncio.sleep(k)

			if time_distance >= stop_distance:	
				break
				
		self.ready = True

		self.stop_for = False
		self.pin_step.value = 0
		

	def freq(self, frequency, k):
		asyncio.run(self._freq_async(self, frequency, k))


	@_log_input_output(False)
	@_timing(True)
	def move(self, distance: int, async_mode: bool = False):
		if async_mode:
			return self._move_async(distance)
		else:
			asyncio.run(self._move_async(distance))


# motor_x = Motor('motor_x', 4, 3, 26)

# motor_x.move(200)
# motor_x.chip.close()