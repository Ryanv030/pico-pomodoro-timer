# LOUD buzzer test
from machine import Pin, PWM
import time

buzzer = PWM(Pin(15))

print("VOLUME TEST")

# Quieter (25% duty cycle)
print("Quiet beep...")
buzzer.freq(2000)
buzzer.duty_u16(16384)  # 25% volume
time.sleep(0.5)
buzzer.duty_u16(0)

time.sleep(0.5)

# Maximum volume (50% duty cycle)
print("LOUD BEEP!")
buzzer.freq(2000)
buzzer.duty_u16(32768)  # 50% volume - MAXIMUM
time.sleep(0.5)
buzzer.duty_u16(0)

# Even louder perception - use a more piercing frequency
print("PIERCING BEEP!")
buzzer.freq(3000)  # Higher frequency sounds louder
buzzer.duty_u16(32768)
time.sleep(0.5)
buzzer.duty_u16(0)