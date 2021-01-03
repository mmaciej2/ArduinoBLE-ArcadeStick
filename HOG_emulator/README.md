
# HID over GATT psuedo-emulator

Currently the HID information (notably the report map/descriptor) is hardcoded according to my design and does not read the HID information from the device. The USBIP folder contains the modified code that emulates a USB HID device using USBIP. The `arcadestick_hog.py` file connects to the device, then creates the USB HID device and reads notifications from the Arduino and then passes the report to the USB HID. After running `arcadestick_hog.py`, the `usbip` command must be used to attach. The `run.sh` file contains an example file of how I set everything up and run Mame.
