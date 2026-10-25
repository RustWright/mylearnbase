+++
title = "Reaction-wheel pendulum"
description = "A pendulum that balances itself upright by spinning a wheel, taken from derived equations of motion and a Python model to C++ firmware on a Raspberry Pi Pico."
weight = 12
draft = true

[extra]
# active | complete. Anything else fails the build (templates/project.html).
status = "active"
period = "October 2026 – present"
stack = ["Python", "NumPy", "C++", "Raspberry Pi Pico"]
# No repo: the working repository is private and must never be linked.
logbook = "posts/logbook/reaction-wheel/_index.md"
+++

A pendulum with a motor-driven wheel at its tip. Spinning the wheel one way pushes the arm the other, and that reaction torque is the only thing holding the arm upright. The goal is a pendulum that balances on its own, swings itself up from hanging, and recovers when tapped.

The work follows the standard order for a control design. First a model, derived by hand and checked in simulation against its own linearization. Then the hardware, then system identification to measure how far the model is off, then a hand-tuned PID controller followed by an LQR. A Kalman filter fuses the gyro and accelerometer, and the firmware runs on the microcontroller in C++.

Each stage gets its own write-up as it lands.
