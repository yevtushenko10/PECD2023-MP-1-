Raspberry Pi project topic

The project aims to develop a “smart” doorbell system based on a Raspberry Pi 3 board and
peripherals (RGB camera, PIR motion sensor, buzzer).

The doorbell system is intended to detect the presence of a person and signal this via audio using the buzzer.
The detection of a person is based on whether the person’s face can be seen in the proximity of
the system (in an image taken with the RGB camera). This detection should be implemented as
efficiently as possible, both in terms of optimizing the detection processes (e.g., by adjusting the
sensor sampling rate, using hierarchical sensing, Bluetooth-based passive human sensing, etc.)
and in terms of the inference process.

For inferring whether a human face is present in an image, there are two options:

1. local on-board inference using either a basic machine learning algorithm (e.g. Viola
Jones) or a neural network model that is already provided (including the code to perform
the actual inference on the image), and

3. remote inference by sending the image to an online API endpoint that responds with the
result of the inference. (Wi-Fi connectivity is available)
