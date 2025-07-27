from machine import Pin, SPI
from ssd1351 import Display, color565
from xglcd_font import XglcdFont

# Initialize SPI and display
spi = SPI(1, baudrate=10000000, sck=Pin(10), mosi=Pin(11))
display = Display(spi, dc=Pin(8), cs=Pin(9), rst=Pin(7))
font = XglcdFont('fonts/Unispace12x24.c', 12, 24)

# 49ers colors
RED = color565(170, 0, 0)      # 49ers red
GOLD = color565(182, 142, 48)  # 49ers gold  
BLACK = color565(0, 0, 0)
WHITE = color565(255, 255, 255)

def draw_oval_border(cx, cy, rx, ry, color, thickness=2):
    """Draw oval border"""
    for t in range(thickness):
        for angle in range(0, 360, 2):  # Every 2 degrees for smoother curve
            import math
            rad = angle * math.pi / 180
            x = int(cx + (rx - t) * math.cos(rad))
            y = int(cy + (ry - t) * math.sin(rad))
            if 0 <= x < 128 and 0 <= y < 128:
                display.draw_pixel(x, y, color)

def draw_filled_oval(cx, cy, rx, ry, color):
    """Draw filled oval"""
    for y in range(max(0, cy - ry), min(128, cy + ry + 1)):
        for x in range(max(0, cx - rx), min(128, cx + rx + 1)):
            dx = x - cx
            dy = y - cy
            if (dx*dx)/(rx*rx) + (dy*dy)/(ry*ry) <= 1:
                display.draw_pixel(x, y, color)

def draw_49ers_logo():
    """Draw the official 49ers oval logo"""
    cx, cy = 64, 80  # Center of logo
    
    # Draw black outer border
    draw_filled_oval(cx, cy, 45, 25, BLACK)
    
    # Draw gold middle ring
    draw_filled_oval(cx, cy, 42, 22, GOLD)
    
    # Draw red center
    draw_filled_oval(cx, cy, 38, 19, RED)
    
    # Draw "SF" letters - simplified pixel art version
    # Letter S
    display.fill_rectangle(48, 68, 12, 3, WHITE)  # Top bar
    display.fill_rectangle(48, 68, 3, 7, WHITE)   # Left side top
    display.fill_rectangle(48, 74, 12, 3, WHITE)  # Middle bar
    display.fill_rectangle(57, 77, 3, 7, WHITE)   # Right side bottom
    display.fill_rectangle(48, 84, 12, 3, WHITE)  # Bottom bar
    
    # Letter F  
    display.fill_rectangle(68, 68, 3, 19, WHITE)  # Left vertical
    display.fill_rectangle(68, 68, 12, 3, WHITE)  # Top bar
    display.fill_rectangle(68, 76, 8, 3, WHITE)   # Middle bar

def main():
    display.clear()
    
    # Draw "GO 49ERS!" text at top
    text = "GO 49ERS!"
    text_width = font.measure_text(text)
    x = (128 - text_width) // 2
    display.draw_text(x, 15, text, font, GOLD)
    
    # Draw the 49ers logo
    draw_49ers_logo()
    
    print("Go 49ers! Display active")

if __name__ == "__main__":
    main()