import machine
import time
import sys
from machine import Pin, SPI
from ssd1351 import Display, color565
from xglcd_font import XglcdFont

# Pin definitions
ENCODER_CLK = 16
ENCODER_DT = 17
ENCODER_SW = 18
BUZZER_PIN = 15

# Initialize hardware
clk = machine.Pin(ENCODER_CLK, machine.Pin.IN, machine.Pin.PULL_UP)
dt = machine.Pin(ENCODER_DT, machine.Pin.IN, machine.Pin.PULL_UP)
sw = machine.Pin(ENCODER_SW, machine.Pin.IN, machine.Pin.PULL_UP)
buzzer = machine.PWM(machine.Pin(BUZZER_PIN))

# Initialize SPI and OLED display
spi = SPI(1, baudrate=10000000, sck=Pin(10), mosi=Pin(11))
display = Display(spi, dc=Pin(8), cs=Pin(9), rst=Pin(7))
font = XglcdFont('fonts/Unispace12x24.c', 12, 24)

# Timer states
STATE_IDLE = 0
STATE_RUNNING = 1
STATE_PAUSED = 2

# Timer settings
WORK_MINUTES = 25
SHORT_BREAK = 5
LONG_BREAK = 15
POMODOROS_UNTIL_LONG_BREAK = 4

class PomodoroTimer:
    def __init__(self):
        self.state = STATE_IDLE
        self.minutes = WORK_MINUTES
        self.seconds = 0
        self.total_seconds = WORK_MINUTES * 60
        self.pomodoro_count = 0
        self.in_break = False
        
        # Encoder tracking
        self.last_clk = clk.value()
        self.last_dt = dt.value()
        self.last_encoder_time = 0
        self.encoder_position = 0
        
        # Button tracking
        self.button_pressed = False
        self.last_button_state = 1  # Released state
        self.last_press_time = 0
        
        # Timer tracking
        self.last_update_time = time.ticks_ms()
        
        # Display tracking
        self.last_display_update = 0
        self.last_display_state = None
        self.last_display_time = None
        self.last_display_count = None
        
        # Initialize display
        self.update_display()
        
    def beep(self, frequency=1000, duration=100):
        """Play a beep sound"""
        buzzer.freq(frequency)
        buzzer.duty_u16(32768)  # 50% duty cycle
        time.sleep_ms(duration)
        buzzer.duty_u16(0)  # Turn off
        
    def double_beep(self):
        """Play two quick beeps"""
        self.beep(1200, 100)
        time.sleep_ms(50)
        self.beep(1200, 100)
        
    def alarm(self):
        """Play alarm pattern when timer completes"""
        for _ in range(3):
            self.beep(1500, 200)
            time.sleep_ms(100)
            
    def update_display(self):
        """Update OLED display with current timer state - only redraw what changed"""
        # Create current state snapshot
        current_state = (self.state, self.in_break)
        current_time = (self.minutes, self.seconds)
        current_count = self.pomodoro_count
        
        # Check what needs updating
        state_changed = current_state != self.last_display_state
        time_changed = current_time != self.last_display_time
        count_changed = current_count != self.last_display_count
        
        # If nothing changed, don't update
        if not (state_changed or time_changed or count_changed):
            return
        
        # Only clear if state changed (which affects layout)
        if state_changed:
            display.clear()
            
        # Update state text if changed
        if state_changed:
            if self.state == STATE_IDLE:
                state_text = "READY"
                color = color565(0, 255, 0)  # Green
            elif self.state == STATE_RUNNING:
                if self.in_break:
                    state_text = "BREAK"
                    color = color565(0, 255, 255)  # Cyan
                else:
                    state_text = "WORK"
                    color = color565(255, 165, 0)  # Orange
            else:  # PAUSED
                state_text = "PAUSED"
                color = color565(255, 255, 0)  # Yellow
                
            # Draw state text at top
            state_x = (128 - font.measure_text(state_text)) // 2
            display.draw_text(state_x, 10, state_text, font, color)
        
        # Update timer if time changed
        if time_changed:
            # Clear just the timer area (approximate)
            display.fill_rectangle(0, 45, 128, 30, color565(0, 0, 0))  # Black rectangle
            
            timer_text = f"{self.minutes:02d}:{self.seconds:02d}"
            timer_x = (128 - font.measure_text(timer_text)) // 2
            display.draw_text(timer_x, 50, timer_text, font, color565(255, 255, 255))
        
        # Update pomodoro count if changed
        if count_changed:
            # Clear count area
            display.fill_rectangle(0, 85, 128, 30, color565(0, 0, 0))  # Black rectangle
            
            if self.pomodoro_count > 0:
                count_text = f"#{self.pomodoro_count}"
                count_x = (128 - font.measure_text(count_text)) // 2
                display.draw_text(count_x, 90, count_text, font, color565(128, 128, 128))
        
        # Update tracking variables
        self.last_display_state = current_state
        self.last_display_time = current_time
        self.last_display_count = current_count
            
    def handle_encoder_rotation(self):
        """Handle rotary encoder rotation with improved debouncing"""
        current_clk = clk.value()
        current_dt = dt.value()
        current_time = time.ticks_ms()
        
        # Only process if enough time has passed (debounce)
        if time.ticks_diff(current_time, self.last_encoder_time) < 5:
            return
            
        if current_clk != self.last_clk:
            if current_clk == 0:  # Falling edge on CLK
                if self.state == STATE_IDLE:
                    # Store the DT state at the falling edge
                    if current_dt == 1:
                        # Clockwise
                        self.encoder_position += 1
                    else:
                        # Counter-clockwise
                        self.encoder_position -= 1
                    
                    # Update minutes based on accumulated position
                    # This helps filter out noise
                    if abs(self.encoder_position) >= 2:
                        if self.encoder_position > 0:
                            self.minutes = min(60, self.minutes + 1)
                            print(f"Timer set to {self.minutes} minutes")
                            self.beep(800, 30)
                        else:
                            self.minutes = max(1, self.minutes - 1)
                            print(f"Timer set to {self.minutes} minutes")
                            self.beep(600, 30)
                        
                        self.encoder_position = 0
                        self.total_seconds = self.minutes * 60
                        self.update_display()
                        
            self.last_encoder_time = current_time
                
        self.last_clk = current_clk
        self.last_dt = current_dt
        
    def handle_button_press(self):
        """Handle encoder button press with better debouncing"""
        current_button = sw.value()
        current_time = time.ticks_ms()
        
        # Detect button press (transition from 1 to 0)
        if current_button == 0 and self.last_button_state == 1:
            # Button just pressed down
            if time.ticks_diff(current_time, self.last_press_time) > 200:  # Debounce
                self.button_pressed = True
                self.last_press_time = current_time
                
        # Detect button release (transition from 0 to 1)
        elif current_button == 1 and self.last_button_state == 0:
            # Button just released
            if self.button_pressed:
                self.button_pressed = False
                self.handle_button_action()
                
        self.last_button_state = current_button
        
    def handle_button_action(self):
        """Handle button press action based on current state"""
        print(f"Button pressed! Current state: {self.state}, in_break: {self.in_break}")
        
        if self.state == STATE_IDLE:
            # Start timer
            self.state = STATE_RUNNING
            self.seconds = 0
            self.in_break = False
            print(f"\nStarting {self.minutes} minute timer")
            self.double_beep()
            self.update_display()
            
        elif self.state == STATE_RUNNING:
            if self.in_break:
                # Skip break and go to next pomodoro
                self.state = STATE_IDLE
                self.in_break = False
                self.minutes = WORK_MINUTES
                self.total_seconds = WORK_MINUTES * 60
                print("\nBreak skipped, ready for next pomodoro")
                self.beep(800, 100)
                self.update_display()
            else:
                # Pause work timer
                self.state = STATE_PAUSED
                print("\nTimer paused")
                self.beep(600, 100)
                self.update_display()
            
        elif self.state == STATE_PAUSED:
            # Resume timer
            self.state = STATE_RUNNING
            print("\nTimer resumed")
            self.beep(1000, 100)
            self.update_display()
            
    def update_timer(self):
        """Update timer countdown"""
        if self.state == STATE_RUNNING:
            current_time = time.ticks_ms()
            if time.ticks_diff(current_time, self.last_update_time) >= 1000:  # 1 second
                self.last_update_time = current_time
                
                if self.total_seconds > 0:
                    self.total_seconds -= 1
                    self.minutes = self.total_seconds // 60
                    self.seconds = self.total_seconds % 60
                    
                    # Print time remaining
                    print(f"\rTime: {self.minutes:02d}:{self.seconds:02d}", end="")
                    
                    # Update display
                    self.update_display()
                    
                    # Beep every minute
                    if self.state == STATE_RUNNING and self.in_break and self.seconds == 0 and self.minutes > 0:
                        self.beep(500, 50)
                        
                else:
                    # Timer completed
                    self.timer_complete()
                    
    def timer_complete(self):
        """Handle timer completion"""
        self.alarm()
        
        if self.in_break:
            # Break completed, back to work
            self.state = STATE_IDLE
            self.in_break = False
            self.minutes = WORK_MINUTES
            self.total_seconds = WORK_MINUTES * 60
            print("\nBreak completed! Press button to start next pomodoro.")
            self.double_beep()
            self.update_display()
            
        elif self.state == STATE_RUNNING:
            # Work session completed
            self.pomodoro_count += 1
            print(f"\n\nPomodoro #{self.pomodoro_count} completed!")
            
            # Determine break duration
            if self.pomodoro_count % POMODOROS_UNTIL_LONG_BREAK == 0:
                self.minutes = LONG_BREAK
                print(f"Time for a long break! ({LONG_BREAK} minutes)")
            else:
                self.minutes = SHORT_BREAK
                print(f"Time for a short break! ({SHORT_BREAK} minutes)")
                
            self.state = STATE_RUNNING
            self.in_break = True
            self.total_seconds = self.minutes * 60
            print("Break timer started automatically")
            self.update_display()
            
    def run(self):
        """Main timer loop"""
        print("\n" + "="*50)
        print("Pomodoro Timer Ready!")
        print("="*50)
        print(f"Current setting: {self.minutes} minutes")
        print("\nControls:")
        print("- Rotate encoder to adjust time (when idle)")
        print("- Press button to start/pause")
        print("="*50 + "\n")
        
        try:
            while True:
                self.handle_encoder_rotation()
                self.handle_button_press()
                self.update_timer()
                time.sleep_ms(5)  # Small delay to prevent CPU overload
                
        except KeyboardInterrupt:
            print("\n\nTimer stopped by user")
            buzzer.duty_u16(0)  # Ensure buzzer is off
            display.cleanup()
            sys.exit()

# Create and run timer
if __name__ == "__main__":
    timer = PomodoroTimer()
    timer.run()