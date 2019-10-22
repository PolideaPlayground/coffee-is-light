import time
import binascii
import json

import bluepy.btle

import config

_LIGHT_CHARACTERISTIC_UUID = "0000fffc-0000-1000-8000-00805f9b34fb"


def get_state():
    try:
        with open(config.DATA_JSON_PATH) as json_file:
            return json.load(json_file)
    except (IOError, json.JSONDecodeError) as e:
        logging.warning(e)


def control_ble_module():
    while True:
        print("Restarting BLE module")
        try:
            print("Connecting...")
            peripheral = bluepy.btle.Peripheral(config.BLE_LIGHT_ADDRESS, addrType=ADDR_TYPE_PUBLIC)

            characteristics = peripheral.getCharacteristics()
            handle = 0
            for characteristic in characteristics:
                if str(characteristic.uuid) == _LIGHT_CHARACTERISTIC_UUID:
                    handle = characteristic.getHandle()

            print("Connected!")
            last_output = ""

            while True:
                # Input data
                input = get_state()

                # Calculate rgb values
                red = 0
                green = 0
                blue = 0
                new_output = ""

                try:
                    green = min(max(int(input["amount"] * 2.55), 0), 255)
                    blue = 255 - green
                    if 0 < input["inProgress"] < 100:
                        if (time.time() * (1.0 + input["inProgress"] / 25)) % 1 > 0.5:
                            green = 0
                            blue = 0
                    elif not input["coffee"]:
                        green = 0
                        blue = 0
                    new_output = "00{:02x}{:02x}{:02x}".format(red, green, blue)
                except (TypeError, KeyError) as e:
                    logging.warning("Wrong state received. Will try again. ({})".format(e))

                # Check if we need to update anything on the LED side.
                if last_output != new_output:
                    last_output = new_output
                    peripheral.writeCharacteristic(handle, binascii.a2b_hex(last_output))

                # Wait for a new measurements
                time.sleep(0.05)

        except IOError as e:
            logging.warning("IO exception occurred: {}".format(e))
        except BTLEException as e:
            logging.warning("BTLE exception occurred: {}".format(e))


control_ble_module()
