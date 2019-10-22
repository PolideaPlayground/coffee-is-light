# Coffee is light

Source code of winning project of the Polieda Blekhaton 2019. The aim of the project
was to be able to remotely check if there's coffee ready to drink in our office coffee
machine and to get notifications while someone is preparing the coffee. The hardware
is based on two weight sensors located on the left and right side of the coffee machine,
which are connected to the Raspberry PI module.

The source code consists of three major modules:

## analyzer

The analyzer is responsible of retrieving data from the weight sensors and analyze them
in order to find out the current state of the coffee machine. It does it in the loop and
each time writes the current state into the JSON file. That module is also responsible
of sending slack notifications whenever the brewing process is started or finished.

## light

Light module drives the BLE RGB lightbulb to show the current state of the coffee
machine. The color of the lightbulb depends on the amount of the available coffee. If
the brewing is in progress the lightbulb blinks.

## server

Serves the current state of the coffee machine over HTTP. The web page shows the
current amount of water in the water tank and the amount of coffee in the kettle. During
the brewing process, it shows animated progress in real-time.

# Authors:

- Damian Gadomski
- Konrad Rodzik
- Maciej Krysztofiak
- Przemek Lenart
