import asyncio
from bleak import BleakClient
import USBIP.USBIP as USBIP
import USBIP.hid_gamepad as HID

ADDRESS = "4c:11:ae:d5:7a:7a"
UUID = "00002a4d-0000-1000-8000-00805f9b34fb"
KILL_CODE = b'\x80'
device_states = type('', (), {})()

class notification_handler():

    def __init__(self, HID):
        self.device = HID

    def __call__(self, sender, data):
        print(data)
        self.device.states.report = data
        self.device.states.new_value = True
        if data[0] & KILL_CODE[0] == KILL_CODE[0]:
            self.device.states.disconnect = True

async def run(address):
    async with BleakClient(address) as client:
        states = type('', (), {})()
        states.report = b'\x00'
        states.new_value = False
        states.disconnect = False
        await client.is_connected()
        print("connected")
        usb_dev = HID.USBHID(states)
        handler = notification_handler(usb_dev)
        usb_container = USBIP.USBContainer()
        usb_container.add_usb_device(usb_dev)
        await client.start_notify(UUID, handler)
        task = asyncio.create_task(usb_container.run())
        while not usb_dev.states.disconnect:
            await asyncio.sleep(0.1)
        await client.disconnect()



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(ADDRESS))

