from microbit import i2c, pin12, pin8, pin13, pin14, pin15, pin1, pin2
from time import sleep_us
from machine import time_pulse_us

CUTEBOT_ADDR = 0x10
LEFT_LIGHT_ADDR = 0x04
RIGHT_LIGHT_ADDR = 0x08


class Cutebot:
    def __init__(self):
        i2c.init()
        self._e, self._t, self._l, self._r = pin12, pin8, pin13, pin14
        self._l.set_pull(self._l.PULL_UP)
        self._r.set_pull(self._r.PULL_UP)

        self._ext_e, self._ext_t = pin2, pin1

    def set_motors_speed(self, l: int, r: int):
        if not -100 <= l <= 100 or not -100 <= r <= 100:
            return
        i2c.write(CUTEBOT_ADDR, bytearray([0x01, 0x02 if l > 0 else 0x01, abs(l), 0]))
        i2c.write(CUTEBOT_ADDR, bytearray([0x02, 0x02 if r > 0 else 0x01, abs(r), 0]))

    def set_car_light(self, light: int, R: int, G: int, B: int):
        if R > 255 or G > 255 or B > 255:
            return
        i2c.write(CUTEBOT_ADDR, bytearray([light, R, G, B]))

    def get_distance(self) -> float:
            self._e.read_digital()
            self._t.write_digital(1)
            sleep_us(10)
            self._t.write_digital(0)
            ts = time_pulse_us(self._e, 1, 25000)
            return round(ts * 0.017, 2)

    def get_distance_side(self) -> float:
        self._ext_e.read_digital()
        self._ext_t.write_digital(1)
        sleep_us(10)
        self._ext_t.write_digital(0)
        ts = time_pulse_us(self._ext_e, 1, 25000)
        return round(ts * 0.017, 2)

    def get_tracking(self) -> int:
        l, r = self._l.read_digital(), self._r.read_digital()
        if l == 1 and r == 1: return 0
        if l == 0 and r == 1: return 10
        if l == 1 and r == 0: return 1
        if l == 0 and r == 0: return 11
        return -1
