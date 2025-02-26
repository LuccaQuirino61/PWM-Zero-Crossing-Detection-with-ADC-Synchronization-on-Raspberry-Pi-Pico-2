from machine import Pin, PWM, ADC
import time

# Configure PWM on GPIO 21
pwm_pin = PWM(Pin(21))  # Set PWM output on pin 21
pwm_pin.freq(1000)  # Set carrier frequency to 1 kHz
pwm_pin.duty_u16(32767)  # 50% duty cycle

# Configure ADC on GPIO 26
adc = ADC(Pin(26))

# Configure Sync Pin
sync_pin = Pin(12, Pin.IN)

# Cofigure IRQ Indicator aux Pin
indicator = Pin(4, Pin.OUT)

# Global variable to count interruptions
irq_count = 0
max_interrupts = 1000  # 1000 limit

# Interrupt function for zero detection
def pwm_zero_detect(pin):
    global irq_count  # Allows you to modify the global variable
    if irq_count < max_interrupts:
        indicator.value(1) # generates the pulse wave 
        irq_count += 1
        indicator.value(0) # generates the pulse wave 
        adc_value = adc.read_u16()  # Read ADC value (0-65535)
        print(f"PWM reached zero! ADC Reading: {adc_value}")
    else:
        sync_pin.irq(handler=None)  # Disable interrupt after 100 executions, to preserve CPU.

# Attach interrupt to the sync pin
sync_pin.irq(trigger=Pin.IRQ_FALLING, handler=pwm_zero_detect)