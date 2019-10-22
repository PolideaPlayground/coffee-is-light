import os


DEBUG = False

# path to the file to be used as "shared memory", preferably located in ramdisk
DATA_JSON_PATH = os.environ["DATA_JSON_PATH"]

# slack hook url that will allow to post notifications
SLACK_HOOK_URL = os.environ.get("SLACK_HOOK_URL")

# the address of the RGB bluetooth light bulb
BLE_LIGHT_ADDRESS = os.environ.get("BLE_LIGHT_ADDRESS", "b5:3a:4b:17:ac:e6")
