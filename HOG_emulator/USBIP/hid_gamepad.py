import time
import random
import datetime
from USBIP.USBIP import BaseStucture, USBDevice, InterfaceDescriptor, DeviceConfigurations, EndPoint, USBContainer
import array
import asyncio


# Emulating USB gamepad

# HID Configuration

class HIDClass(BaseStucture):
    _fields_ = [
        ('bLength', 'B', 9),
        ('bDescriptorType', 'B', 0x21),  # HID
        ('bcdHID', 'H'),
        ('bCountryCode', 'B'),
        ('bNumDescriptors', 'B'),
        ('bDescriptprType2', 'B'),
        ('wDescriptionLength', 'H'),
    ]


hid_class = HIDClass(bcdHID=0x0100,  # keyboard
                     bCountryCode=0x0,
                     bNumDescriptors=0x1,
                     bDescriptprType2=0x22,  # Report
                     wDescriptionLength=0x3500)  # Little endian


interface_d = InterfaceDescriptor(bAlternateSetting=0,
                                  bNumEndpoints=1,
                                  bInterfaceClass=3,  # class HID
                                  bInterfaceSubClass=0,
                                  bInterfaceProtocol=0, #keyboard
                                  iInterface=0)

end_point = EndPoint(bEndpointAddress=0x81,
                     bmAttributes=0x3,
                     wMaxPacketSize=0x0800,  # Little endian
                     bInterval=0x0A)  # interval to report


configuration = DeviceConfigurations(wTotalLength=0x2200,
                                     bNumInterfaces=0x1,
                                     bConfigurationValue=0x1,
                                     iConfiguration=0x0,  # No string
                                     bmAttributes=0x80,  # valid self powered
                                     bMaxPower=50)  # 100 mah current

interface_d.descriptions = [hid_class]  # Supports only one description
interface_d.endpoints = [end_point]  # Supports only one endpoint
configuration.interfaces = [interface_d]   # Supports only one interface


class USBHID(USBDevice):
    vendorID = 0xadde
    productID = 0xefbe
    bcdDevice = 0x0
    bcdUSB = 0x0
    bNumConfigurations = 0x1
    bNumInterfaces = 0x1
    bConfigurationValue = 0x1
    configurations = []
    bDeviceClass = 0x0
    bDeviceSubClass = 0x0
    bDeviceProtocol = 0x0
    configurations = [configuration]  # Supports only one configuration

    def __init__(self, states):
        USBDevice.__init__(self)
        self.start_time = datetime.datetime.now()
        self.states = states

    def generate_keyboard_report(self):

        arr = [0x05, 0x01,  # Usage Page (Generic Desktop)
               0x09, 0x05,  # Usage (Gamepad)
               0xa1, 0x01,  # Collection (Application)
               0x09, 0x05,  #   Usage (Gamepad)
               0xa1, 0x02,  #   Collection (Logical)
               0x09, 0x01,  #     Usage (Pointer)
               0xa1, 0x00,  #     Collection (Physical)
               0x09, 0x31,  #       Usage (Y)
               0x09, 0x30,  #       Usage (x)
               0x95, 0x02,  #       Report Count (2)
               0x75, 0x02,  #       Report Size (2)
               0x15, 0x00,  #       Logical Minimum (0)
               0x25, 0x02,  #       Logical Maximum (3)
               0x35, 0x81,  #       Physical Minimum (-127)
               0x45, 0x7F,  #       Physical Maximum (127)
               0x81, 0x02,  #       Input (Data,Var,Abs)
               0x05, 0x09,  #       Usage Page (Button)
               0x09, 0x01,  #       Usage (Button 1)
               0x09, 0x02,  #       Usage (Button 2)
               0x09, 0x10,  #       Usage (Button 16)
               0x95, 0x03,  #       Report Count (3)
               0x75, 0x01,  #       Report Size (1)
               0x81, 0x02,  #       Input (Data,Var,Abs)
               0x95, 0x01,  #       Report Count (1)
               0x81, 0x03,  #       Input (Cnst,Var,Abs)
               0xc0,        #     End Collection
               0xc0,        #   End Collection
               0xc0]        # End Collection
        return array.array('B', arr).tobytes()



    async def handle_data(self, usb_req):
        await asyncio.sleep(0.001)
        self.states.new_value = False
        self.send_usb_req(usb_req, self.states.report, 1)


    def handle_unknown_control(self, control_req, usb_req):
        if control_req.bmRequestType == 0x81:
            if control_req.bRequest == 0x6:  # Get Descriptor
                if control_req.wValue == 0x22:  # send initial report
                    print('send initial report')
                    ret=self.generate_keyboard_report()
                    self.send_usb_req(usb_req, ret, len(ret))

        if control_req.bmRequestType == 0x21:  # Host Request
            if control_req.bRequest == 0x0a:  # set idle
                print('Idle')
                # Idle
                self.send_usb_req(usb_req, '', 0,0)
                pass
            if control_req.bRequest == 0x09:  # set report
                print('set report')
                data = usb_container.usb_devices[0].connection.recv(control_req.wLength)
                #use data ? 
                self.send_usb_req(usb_req, '', 0,0)
                pass
