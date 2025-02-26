# PWM Zero Crossing Detection with ADC Synchronization on Raspberry Pi Pico

This project demonstrates how to precisely trigger an ADC reading when a PWM signal reaches zero on the Raspberry Pi Pico. It ensures accurate synchronization between the PWM carrier and ADC sampling, making it useful for power electronics applications, motor control, and PLL implementations.

## Features
- Generates a **1 kHz PWM signal** on GPIO 21.
- Detects when the PWM counter **resets to zero** using an external sync pin (GPIO 12).
- Sends a pulse wave to GPIO 4 to be seen in an oscilloscope and compare to PWM falling edge.
- Reads **ADC input (GPIO 26)** exactly when the PWM reaches zero (when the interrupt is requested).
- Uses **hardware interrupts (IRQ)** for precise timing (Interrupts requests).

## Hardware Setup
- **GPIO 21** → PWM output.
- **GPIO 12** → Sync input (should be connected physically with the PWM pin (Pin 21)).
- **GPIO 4**  → Aux output to observe the pulse wave every interruption.
- **GPIO 26** → ADC input.

## Code Implementation
```python
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
```

# How It Works

---

## 1. **PWM Generation:**
A 1 kHz PWM signal is created on GPIO 21, with 1kHz frequency and 50% duty cycle.
```python
# Configure PWM on GPIO 21
pwm_pin = PWM(Pin(21))  # Set PWM output on pin 21
pwm_pin.freq(1000)  # Set carrier frequency to 1 kHz
pwm_pin.duty_u16(32767)  # 50% duty cycle
```

---

## 2. **Settings:**
All the other pins are created and configured.
```python
# Configure ADC on GPIO 26
adc = ADC(Pin(26))

# Configure Sync Pin
sync_pin = Pin(12, Pin.IN)

# Cofigure IRQ Indicator aux Pin
indicator = Pin(4, Pin.OUT)
```

---

## 3. **Interruption:**
The following line configures an **interrupt request (IRQ)** on a GPIO pin using MicroPython:
```python
sync_pin.irq(trigger=Pin.IRQ_FALLING, handler=pwm_zero_detect)
```
- **`Pin.IRQ_FALLING`** → The interrupt occurs when the signal falls from **1 to 0** (**falling edge**).
- **`handler=pwm_zero_detect`** → When the interrupt occurs, the function `pwm_zero_detect()` is executed.

This means that **whenever the PWM resets to zero, the interrupt automatically triggers the ADC reading function**.

---

### What is `Pin.IRQ_FALLING`?
`Pin.IRQ_FALLING` is a **constant** from the **`machine`** library in **MicroPython**. It is used to configure **interrupts on GPIO pins**.
In the **Raspberry Pi Pico 2 (RP2350) context**, this constant indicates that the **interrupt (IRQ) will be triggered when the pin signal transitions from HIGH (1) to LOW (0)**—meaning, on the **falling edge**.

---

### Other IRQ Modes
MicroPython provides other constants to configure **GPIO interrupts**:
- **`Pin.IRQ_RISING`** → Triggers the interrupt on the **rising edge** (0 → 1).
- **`Pin.IRQ_FALLING`** → Triggers the interrupt on the **falling edge** (1 → 0).
- **`Pin.IRQ_RISING | Pin.IRQ_FALLING`** → Triggers the interrupt on **both edges**.

This setup ensures that the **ADC reading is executed precisely when the PWM reaches zero**, allowing accurate synchronization. 🚀

---

## 4. **pwm_zero_detect() Function:**

### Overview

The `pwm_zero_detect` function is an interrupt function used to detect the exact moment when a PWM signal reaches zero. It is configured to be called whenever an interrupt occurs on the synchronization pin (`sync_pin`), which is associated with the PWM signal.

### Code

```python
def pwm_zero_detect(pin):
    global irq_count  # Allows modification of the global variable
    if irq_count < max_interrupts:
        adc_value = adc.read_u16()  # Reads the ADC value (0-65535)
        print(f"PWM reached zero! ADC Reading: {adc_value}")
        irq_count += 1
    else:
        sync_pin.irq(handler=None)  # Disables the interrupt after 100 executions
```

### Global Variables

- `irq_count`: Global variable that counts the number of times the interrupt has been triggered.
- `max_interrupts`: Maximum limit of interrupt function executions.

### Function Behavior

1. **ADC Reading:**
   - The function reads the ADC value (0 to 65535) from the configured pin.

2. **Printing the ADC Value:**
   - Prints the ADC value to the console for monitoring.

3. **Interrupt Count:**
   - Increments the interrupt counter (`irq_count`).

4. **Interrupt Deactivation:**
   - When the maximum number of interrupts is reached, the interrupt is disabled to prevent additional executions.

---

# Results

### Oscilloscope Waveform

The following image shows the captured PWM signal using a Tektronix TBS 1102B oscilloscope:

![Oscilloscope PWM Signal](images/Oscilloscope.jpg)





