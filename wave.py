from math import sin
import random


class Wave:
    def __init__(self, wave_number, wave_scale, wave_max_offset, height_offset):
        self.wave_number = wave_number
        self.wave_scale = wave_scale
        self.height_offset = height_offset
        
        self.offsets = [
            (random.random() - 0.5) * wave_max_offset * 2
            for i in range(self.wave_number)
        ]

        self.coefficents = [
            random.random()
            for i in range(self.wave_number)
        ]

    def generate(self, x):
        return sum([
            sin((x - offset) * coefficent)
            for offset, coefficent in zip(self.offsets, self.coefficents)
        ]) / self.wave_number * self.wave_scale + self.height_offset
