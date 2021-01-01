#include <ArduinoBLE.h>

const unsigned long BUTTON_REBOUND_PERIOD = 5;
const unsigned int NUM_BUTTONS = 7;

BLELocalDevice peripheral = BLE;

typedef struct {
  unsigned long last_fired;
  unsigned int pin;
  bool state;
  const int bit_position;
  const int bit_state;
} button;

button button_array[NUM_BUTTONS] = {
  {0, 0, false, 0, false}, // up
  {0, 1, true, 1, true}, // down
  {0, 2, true, 3, true}, // right
  {0, 3, false, 2, false}, // left
  {0, 6, true, 4, true}, // one
  {0, 7, true, 5, true}, // two
  {0, 8, true, 6, true}  // main
};
const byte default_message = 0b00000101;

bool check_button(button *b, unsigned long now) {
  if (digitalRead(b->pin) == b->state^b->bit_state && now - b->last_fired >= BUTTON_REBOUND_PERIOD) {
    b->state = !b->state;
    b->last_fired = now;
    return true;
  }
  return false;
}

const byte report_descriptor[51] = {
  0x05, 0x01,  // Usage Page (Generic Desktop)
  0x09, 0x05,  // Usage (Gamepad)
  0xa1, 0x01,  // Collection (Application)
  0x09, 0x05,  //   Usage (Gamepad)
  0xa1, 0x02,  //   Collection (Logical)
  0x09, 0x01,  //     Usage (Pointer)
  0xa1, 0x00,  //     Collection (Physical)
  0x09, 0x90,  //       Usage (D-pad Up)
  0x09, 0x91,  //       Usage (D-pad Down)
  0x09, 0x92,  //       Usage (D-pad Right)
  0x09, 0x93,  //       Usage (D-pad Left)
  0x95, 0x04,  //       Report Count (4)
  0x75, 0x01,  //       Report Size (1)
  0x15, 0x00,  //       Logical Minimum (0)
  0x25, 0x01,  //       Logical Maximum (1)
  0x81, 0x02,  //       Input (Data,Var,Abs)
  0x05, 0x09,  //       Usage Page (Button)
  0x09, 0x01,  //       Usage (Button 1)
  0x09, 0x02,  //       Usage (Button 2)
  0x09, 0x10,  //       Usage (Button 16)
  0x95, 0x03,  //       Report Count (3)
  0x81, 0x02,  //       Input (Data,Var,Abs)
  0x95, 0x01,  //       Report Count (1)
  0x81, 0x03,  //       Input (Cnst,Var,Abs)
  0xc0,        //     End Collection
  0xc0,        //   End Collection
  0xc0         // End Collection
};

BLEService hid_service("1812");  // "Human Interface Device" Service
BLECharacteristic report("2a4d", BLERead|BLENotify, 1);  // "Report" Characteristic
const uint8_t report_type[2] = {0x00, 0x01};
BLEDescriptor report_reference("2908", report_type, 2); // "Report Reference" Descriptor
const uint8_t cccd_value[2] = {0x00, 0x01};
BLEDescriptor cccd("2902", cccd_value, 2); // "Client Characteristic Configuration" Descriptor
BLECharacteristic report_map("2a4b", BLERead, 51);  // "Report Map" Characteristic
const byte hid_info_data[4] = {0x11, 0x01, 0x00, 0x00};
BLECharacteristic hid_info("2a4a", BLERead, 4);  // "HID Information" Characteristic
BLECharacteristic hid_cp("2a4c", BLEWriteWithoutResponse, 1);  // "HID Control Point" Characteristic

BLEService battery_service("180f");  // "Battery"
const byte battery_value[1] = {69};
BLECharacteristic battery_level("2a19", BLERead, 1);  // "Battery Level" Characteristic

BLEService info_service("180a");  // "Device Information" Service
//const byte pnp_id_data[7] = {0x02, 0x41, 0x23, 0x00, 0x00, 0x01, 0x01};
const byte pnp_id_data[7] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
BLECharacteristic pnp_id("2a50", BLERead, 7);  // "PnP ID" Characteristic
const char mname_data[3] = "me";
BLECharacteristic manufacturer_name("2a29", BLERead, 2);  // "Manufacturer Name String" Characteristic
const char mnum_data[3] = "m1";
BLECharacteristic model_number("2a24", BLERead, 2);  // "Model Number String" Characteristic
const char fr_data[3] = "f1";
BLECharacteristic firmware_revision("2a26", BLERead, 2);  // "Software Revision String" Characteristic
const char sr_data[3] = "s1";
BLECharacteristic software_revision("2a28", BLERead, 2);  // "Manufacturer Name String" Characteristic


void setup() {
  unsigned long now = millis();

  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  for (uint8_t i = 0; i < NUM_BUTTONS; i++) {
    button_array[i].last_fired = now;
    pinMode(button_array[i].pin, INPUT_PULLUP);
  }

  Serial.begin(9600);

  if (!peripheral.begin()){
    Serial.println("Starting BLE failed!");
    while (true);
  }

  peripheral.setLocalName("ArcadeStick");
  peripheral.setDeviceName("ArcadeStick");
  peripheral.setAppearance(0x03c4);
  peripheral.setAdvertisedService(hid_service);
  peripheral.setConnectionInterval(0x0006, 0x0006);

  report.addDescriptor(report_reference);
  hid_service.addCharacteristic(report);
  report_map.writeValue(report_descriptor, 51);
  hid_service.addCharacteristic(report_map);
  hid_info.writeValue(hid_info_data, 4);
  hid_service.addCharacteristic(hid_info);
  hid_service.addCharacteristic(hid_cp);
  peripheral.addService(hid_service);

  pnp_id.writeValue((uint8_t*)pnp_id_data, 7);
  info_service.addCharacteristic(pnp_id);
  peripheral.addService(info_service);

  battery_level.writeValue(battery_value, 1);
  battery_service.addCharacteristic(battery_level);
  peripheral.addService(battery_service);

  if (!peripheral.advertise()) {
    Serial.println("Failed to advertise!");
    while (true);
  }
  Serial.println("advertising");

}


void loop() {

  BLEDevice host = peripheral.central();

  if (host) {
    
    Serial.print("Connected to: ");
    Serial.println(host.address());
    digitalWrite(LED_BUILTIN, HIGH);

    byte report_message = default_message;
    byte last_message = default_message;

    while (host.connected()) {

      unsigned long now;

      while (report_message == last_message) {

        now = millis();
        peripheral.poll();

        // check buttsons
        for (uint8_t i = 0; i < NUM_BUTTONS; i++) {
          if (check_button(&button_array[i], now)) {
            report_message ^= (-!button_array[i].state ^ report_message) & (0x01 << button_array[i].bit_position);
          }
        }

        // check for disconnect
        if (!button_array[6].state && now - button_array[6].last_fired > 3000) {
          report_message = 0x80 | default_message;
          report.writeValue(&report_message, 1);
          delay(10);
          host.disconnect();
          report_message = default_message;
        }

      }

      // write message
      report.writeValue(&report_message, 1);
      last_message = report_message;

    }

    Serial.println("Disconnected.");
    
  }

  digitalWrite(LED_BUILTIN, HIGH);
  delay(500);
  digitalWrite(LED_BUILTIN, LOW);
  delay(500);
  
}
