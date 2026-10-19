# Pico Pomodoro Timer

A desk Pomodoro timer built on a Raspberry Pi Pico, written in MicroPython.

Turn the knob to set the minutes, press to start, press again to pause. It runs the standard cycle: 25 minutes of work, a 5 minute break, and a 15 minute break after every fourth round. A color OLED shows the state, the countdown, and how many rounds you've finished, and a buzzer marks each minute and the end of each session.

## Hardware

- Raspberry Pi Pico
- SSD1351 128x128 color OLED (SPI)
- Rotary encoder with push button
- Passive buzzer

## Wiring

| Part | Pico pin |
|---|---|
| OLED SCK | GP10 |
| OLED MOSI | GP11 |
| OLED DC | GP8 |
| OLED CS | GP9 |
| OLED RST | GP7 |
| Encoder CLK | GP16 |
| Encoder DT | GP17 |
| Encoder button | GP18 |
| Buzzer | GP15 |

## Running it

Copy the repo to the Pico (the MicroPico VS Code extension works well). `boot.py` runs on power-up, so the timer starts as soon as the board has power.

The `test_*.py` scripts check the buzzer, display, and encoder one at a time, which helps when wiring things up. `niners.py` draws a 49ers screen in team colors, just for fun.

## Notes

The screen redraws only the parts that changed, so the countdown doesn't flicker. The encoder input is debounced to keep the minute setting from jumping.

The display driver (`ssd1351.py`) and font utility (`xglcd_font.py`) come from rdagger's [micropython-ssd1351](https://github.com/rdagger/micropython-ssd1351).
