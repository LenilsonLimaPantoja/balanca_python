import RPi.GPIO as GPIO
import time

class HX711:
    def __init__(self, dout, pd_sck, gain=128):
        self.PD_SCK = pd_sck
        self.DOUT = dout

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.PD_SCK, GPIO.OUT)
        GPIO.setup(self.DOUT, GPIO.IN)

        self.GAIN = 0
        self.REFERENCE_UNIT = 1
        self.OFFSET = 1
        self.lastVal = 0

        self.LAST_READ_TIME = time.time()
        self.READ_TIMEOUT = 0.1

        self.byte_format = 'MSB'
        self.bit_format = 'MSB'

        self.set_gain(gain)

    def set_gain(self, gain):
        if gain == 128:
            self.GAIN = 1
        elif gain == 64:
            self.GAIN = 3
        elif gain == 32:
            self.GAIN = 2

        GPIO.output(self.PD_SCK, False)
        self.read()

    def set_referenceUnit(self, reference_unit):
        self.REFERENCE_UNIT = reference_unit

    def read(self):
        while GPIO.input(self.DOUT) == 1:
            pass

        dataBits = []
        for _ in range(24):
            GPIO.output(self.PD_SCK, True)
            dataBits.append(GPIO.input(self.DOUT))
            GPIO.output(self.PD_SCK, False)

        for _ in range(self.GAIN):
            GPIO.output(self.PD_SCK, True)
            GPIO.output(self.PD_SCK, False)

        value = 0
        for bit in dataBits:
            value = (value << 1) | bit

        if value & 0x800000:
            value |= ~0xffffff

        return value

    def get_weight(self, times=5):
        value = 0
        for _ in range(times):
            value += self.read()
        value /= times
        value -= self.OFFSET
        value /= self.REFERENCE_UNIT
        return value

    def tare(self, times=15):
        sum_ = 0
        for _ in range(times):
            sum_ += self.read()
        self.OFFSET = sum_ / times

    def reset(self):
        self.set_gain(128)

    def power_down(self):
        GPIO.output(self.PD_SCK, False)
        GPIO.output(self.PD_SCK, True)
        time.sleep(0.0001)

    def power_up(self):
        GPIO.output(self.PD_SCK, False)
        time.sleep(0.0001)