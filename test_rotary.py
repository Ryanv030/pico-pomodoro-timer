# rotary_one_click.py - One count per physical click
from machine import Pin
import time

# Set up pins
clk = Pin(16, Pin.IN, Pin.PULL_UP)
dt = Pin(17, Pin.IN, Pin.PULL_UP)
sw = Pin(18, Pin.IN, Pin.PULL_UP)

print("ROTARY ENCODER - ONE COUNT PER CLICK")
print("=" * 40)
print("Each physical click = 1 position change")
print("=" * 40)

counter = 0
clk_last = clk.value()
dt_last = dt.value()

# Track direction during rotation
rotating = False
clockwise = True

while True:
    clk_state = clk.value()
    dt_state = dt.value()
    
    # Detect start of rotation to capture direction
    if (clk_state != clk_last or dt_state != dt_last) and not rotating:
        if clk_state != clk_last:
            clockwise = (dt_state != clk_state)
        else:
            clockwise = (dt_state == clk_state)
        rotating = True
    
    # Detect completion of click (both back to HIGH)
    if clk_state == 1 and dt_state == 1 and rotating:
        if clockwise:
            counter += 1
            print(f"→ Position: {counter}")
        else:
            counter -= 1
            print(f"← Position: {counter}")
        rotating = False
    
    # Button check
    if sw.value() == 0:
        print(f"🔘 BUTTON! Position: {counter}")
        counter = 0  # Reset to zero
        print("↻ Reset to 0")
        time.sleep(0.3)
    
    # Update last values
    clk_last = clk_state
    dt_last = dt_state
    
    time.sleep(0.002)  # Slightly longer delay for stability