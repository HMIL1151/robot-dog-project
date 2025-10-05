
import random

class Pin:
    IN = 0
    OUT = 1

    def __init__(self, pin_id, mode=None):
        self.pin_id = pin_id
        self.mode = mode

    def value(self, val=None):
        if val is None:
            return 0  # Always return low for input
        # Set value (no-op in mock)

class UART:
    def __init__(self, uart_id, baudrate=9600, tx=None, rx=None):
        self.uart_id = uart_id
        self.baudrate = baudrate
        self.tx = tx
        self.rx = rx
        self._buffer = bytearray()

    def read(self, nbytes):
        # Simulate reading nbytes from UART
        if len(self._buffer) < nbytes:
            # Fill buffer with random bytes if not enough data
            self._buffer += bytearray(random.getrandbits(8) for _ in range(nbytes - len(self._buffer)))
        result = self._buffer[:nbytes]
        self._buffer = self._buffer[nbytes:]
        return bytes(result)

    def write(self, data):
        # Simulate writing data to UART (no-op)
        return len(data)