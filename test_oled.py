import machine
from machine import Pin, SPI
from ssd1351 import Display, color565
from xglcd_font import XglcdFont

# Initialize SPI1
spi = SPI(1, baudrate=10000000, sck=Pin(10), mosi=Pin(11))

# Initialize display
display = Display(spi, dc=Pin(8), cs=Pin(9), rst=Pin(7))

# Load font
font = XglcdFont('fonts/Unispace12x24.c', 12, 24)

# Clear and draw text
display.clear()
text = "Hello OLED!"
x = (128 - font.measure_text(text)) // 2
display.draw_text(x, 50, text, font, color565(255, 255, 255))

# Wait, then cleanup
machine.lightsleep(30000)
display.cleanup()