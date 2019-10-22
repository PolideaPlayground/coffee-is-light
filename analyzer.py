import csv
import json
import time
import sys
import subprocess
import logging

import HX711

import config


def get_current_time_millis():
    return int(round(time.time() * 1000))


def get_test_data():
    with open("test.out.csv", mode='r') as data_csv:
        csv_reader = csv.reader(data_csv)
        for row in csv_reader:
            yield (row[0], row[1], row[2])


def get_real_data():
    hx = hx711.HX711(5, 6)

    hx.set_reading_format("MSB", "MSB")

    hx.set_reference_unit_A(1)
    hx.set_reference_unit_B(1)

    hx.reset()

    hx.set_gain(64)

    hx.tare_A()
    hx.tare_B()
    logging.info("Tare done! You can now add weight.")

    channel_A_ratio = 369  # Magic numbers to scale both channels in the same units
    channel_B_ratio = 172

    start_time = get_current_time_millis()

    while True:
        try:
            weight_A = hx.get_weight_A() / channel_A_ratio
            weight_B = hx.get_weight_B() / channel_B_ratio

            #print "%s,%s,%s" % (get_current_time_millis() - start_time, val_A, val_B)

            yield get_current_time_millis(), weight_B, weight_A

        except (KeyboardInterrupt, SystemExit):
            logging.info("Shutting down!")
            sys.exit()


def median(samples):
    n = len(samples)
    if n < 1:
        return None
    if n % 2 == 1:
        return sorted(samples)[n // 2]
    else:
        return sum(sorted(samples)[n // 2 - 1:n // 2 + 1]) / 2.0


def is_buffer_constant(buffer, variation=10):
    average_sum = sum(buffer) / len(buffer)
    return all(i > average_sum - variation for i in buffer) and \
           all(i < average_sum + variation for i in buffer)


def send_to_slack(message):
    if config.DEBUG:
        print(message)
    else:
        subprocess.call(
            ["curl", "-X", "POST", "--data-urlencode",
             """payload={"channel": "coffeeislight", "username": "Coffee is LIGHT!", "text": """ + "\"{}\"".format(
                 message) + """, "icon_emoji": "coffee"}""",
             config.SLACK_HOOK_URL]
        )


def analyze():
    buffer_left = []
    buffer_right = []
    buffer_sum = []
    buffer_size = 10

    left_when_started = 0
    right_when_started = 0
    started = False
    progress_duration = 0
    progress = 0
    amount = 0
    coffee = False

    for timestamp, left, right in get_real_data() if not DEBUG else get_test_data():
        buffer_left.append(int(left))
        buffer_right.append(int(right))
        buffer_sum.append(int(left) + int(right))

        if len(buffer_left) == buffer_size + 1:
            buffer_left.pop(0)
            buffer_right.pop(0)
            buffer_sum.pop(0)

            if is_buffer_constant(buffer_sum):
                # nobody is touching coffee machine
                amount = 100 * buffer_sum[buffer_size - 1] / 1200
                amount = 100 if amount > 100 else amount
                amount = 0 if amount < 0 else amount

                if is_buffer_constant(buffer_left) and is_buffer_constant(buffer_right):
                    # coffee machine is in idle (nothing is in progress)
                    if started and progress_duration >= 13:
                        # we've just finished brewing
                        send_to_slack("Coffee is ready!")

                    started = False
                    progress_duration = 0

                    if amount < 10:
                        # kettle & water tank are (almost) empty
                        amount = 0
                        coffee = False
                        progress = 0
                    elif buffer_left[buffer_size - 1] > buffer_right[buffer_size - 1]:
                        # water tank is heavier than kettle (brewing is probably going to start soon)
                        coffee = False
                        progress = 0
                    else:
                        # kettle is heavier than water tank (there's coffee ready to drink)
                        coffee = True
                        progress = 100
                else:
                    # brewing is in progress (coffee machine transports water from one side to the other)
                    if not started:
                        # brewing just started
                        left_when_started = buffer_left[0]
                        right_when_started = buffer_right[0]
                        started = True

                    progress_duration += 1
                    if progress_duration == 13:
                        # to avoid false positives we'are sending notification after some time
                        send_to_slack("Someone started brewing coffee for you! :)")

                    if left_when_started:
                        progress = int(100 * (buffer_right[buffer_size - 1] - right_when_started) / (
                                    left_when_started - right_when_started))
                        progress = 100 if progress > 100 else progress
                        progress = 0 if progress < 0 else progress

        yield timestamp, left, right, progress, amount, coffee


def main():
    for timestamp, left, right, progress, amount, coffee in analyze():
        with open(config.DATA_JSON_PATH, mode='w') as output_json:
            json.dump({"coffee": coffee, "inProgress": progress, "amount": amount}, output_json)


main()
