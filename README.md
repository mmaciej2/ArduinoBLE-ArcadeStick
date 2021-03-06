
# ArduinoBLE ArcadeStick (and HID over GATT pseudo-emulator)

### WIP for Bluetooth Low Energy arcade stick using the ArduinoBLE library

I'm using a MKR WIFI 1010 with the ArduinoBLE library to create a HID over GATT bluetooth device. ArduinoBLE currently doesn't implement bonding, which is necessary for the HOG Profile, so I am using [Bleak](https://github.com/hbldh/bleak) and [this](https://github.com/lcgamboa/USBIP-Virtual-USB-Device) python implementation of a virtual USB HID to read the relevant HOG info and emulate the deice, passing the reports through.

### Alternate minimal backend

While one goal is to fully implement a proper BLE HID, I am also working on an alternate backend specific to Linux that produces a virtual joystick in as minimal way as possible. This is for an application-driven goal (notably producing a lightweight Mame console with wireless controller), as opposed to the goal of widespread support in a proper BLE HID implementation.
