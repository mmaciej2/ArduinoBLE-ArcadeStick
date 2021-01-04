import asyncio
from bleak import BleakClient
import uinput
import sys

ADDRESS = "4c:11:ae:d5:7a:7a"
UUID = "00002a4d-0000-1000-8000-00805f9b34fb"

events = (
    (0x03, 0x00, -127, 127, 0, 0),  # ABS X
    (0x03, 0x01, -127, 127, 0, 0),  # ABS Y
    (0x01, 0x130),  # ABS BTN_A
    (0x01, 0x131),  # ABS BTN_B
    (0x01, 0x132),  # ABS BTN_C
    (0x01, 0x13c),  # ABS BTN_MODE
    )

bit_map = { # bits from left to right!
    1: events[5],
    2: events[3],
    3: events[2],
    4: events[0],
    5: events[0],
    6: events[1],
    7: events[1]}


class notification_handler():

    def __init__(self, device):
        self.states = type('', (), {})()
        self.device = device
        self.last_call = None

    def __call__(self, sender, data):
        bits = [int(bit) for byte in data for bit in bin(byte)[2:].zfill(8)]

        if not self.last_call:
            self.last_call = [1-bit for bit in bits]

        # Disconnect signal
        for i in range(0, 1):
            if bits[i]:
                self.states.disconnect = True

        # Regular buttons
        for i in range(1, 4):
            if bits[i] != self.last_call[i]:
                self.device.emit(bit_map[i], bits[i], syn=False)

        # X axis left/right
        if bits[4:6] != self.last_call[4:6]:
            if bits[4]:
                self.device.emit(bit_map[4][:2], 127, syn=False)
            elif not bits[5]:
                self.device.emit(bit_map[4][:2], -127, syn=False)
            else:
                self.device.emit(bit_map[4][:2], 0, syn=False)

        # Y axis up/down
        if bits[6:8] != self.last_call[6:8]:
            if not bits[7]:
                self.device.emit(bit_map[6][:2], -127, syn=False)
            elif bits[6]:
                self.device.emit(bit_map[6][:2], 127, syn=False)
            else:
                self.device.emit(bit_map[6][:2], 0, syn=False)

        self.last_call = bits
        self.device.syn()

async def run(address):
    async with BleakClient(address) as client:
        await client.is_connected()
        print("connected")
        sys.stdout.flush()
        device = uinput.Device(events)
        handler = notification_handler(device)
        handler.states.disconnect = False
        await client.start_notify(UUID, handler)
        while await client.is_connected() and not handler.states.disconnect:
            None
        await client.disconnect()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(ADDRESS))

