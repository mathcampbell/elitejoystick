# Write your code here :-)
import board
import digitalio
from time import sleep
import busio
import usb_hid
import analogio
import adafruit_bus_device
from hid_gamepad import Gamepad
from adafruit_mcp230xx.mcp23017 import MCP23017
import neopixel
import math

from breakout_ioexpander import BreakoutIOExpander 

pixel_pin = board.GP0
num_pixels = 12
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, pixel_order=ORDER)
pixels.brightness = 1.0
i2c = busio.I2C(scl=board.GP5, sda=board.GP4)

ioe = BreakoutIOExpander(i2c)



#mcp = MCP23017(i2c)

gp = Gamepad(usb_hid.devices)

button_pins = (
    1, #A0
    2, #A1
    3, #A2
    4, #A3
    5, #A4
    6, #A5
)  # these are the buttons from the IO Expander

hat1_pins = (
    9, #A7
    10, #B0
)

hat2_pins = (
    7,
    8,
)

buttons = button_pins

for button in buttons:
    ioe.set_mode(button, ioe.MODE_PULLUP)

#ioe.set_mode(10, ioe.MODE_PULLUP)

hat1_buttons = hat1_pins
hat2_buttons = hat2_pins


for button in hat1_buttons:
    ioe.set_mode(button, ioe.MODE_ADC)
hat1_xpin = hat1_pins[0]
hat1_ypin = hat1_pins[1]
# 
# for button in hat2_buttons:
#     ioe.set_mode(button, ioe.MODE_ADC)
# hat2_xpin = hat2_pins[0]
# hat2_ypin = hat2_pins[1]

ax = analogio.AnalogIn(board.GP26)
ay = analogio.AnalogIn(board.GP27)
az = analogio.AnalogIn(board.GP28)


# onboard LED for testing etc
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led.value = True


def debounce():
    sleep(0.1)


def range_map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


def hatvalue(value):
    if value == 3:
        return 0
    if value == 8:
        return 1
    if value == 5:
        return 2
    if value == 25:
        return 3
    if value == 20:
        return 4
    if value == 50:
        return 5
    if value == 30:
        return 6
    if value == 33:
        return 7
    else:
        return 8

def read_hat_switch():
#     # Read analog values from the ADC pins
#     
#     x_value = range_map(ioe.get_pin(hat1_xpin, ioe.MODE_ADC), 0, 3.3, 0, 4095)
#     y_value = range_map(ioe.get_pin(hat1_ypin, ioe.MODE_ADC), 0, 3.3, 0, 4095)
# 
#     # Map the analog values to the 8-way HAT switch values
#     x_axis = int(x_value / 341) + 1  # Divide the range into 8 equal segments (4096 / 8 = 512)
#     y_axis = int(y_value / 341) + 1
# 
#     # Combine the x and y axis values to get the HAT switch value
#     hat_value = (y_axis - 1) * 3 + x_axis

# Read analog values from the ADC pins
      # Read analog values from the ADC pins
    deadzone = 1024
    x_value = range_map(ioe.get_pin(hat1_xpin, ioe.MODE_ADC), 0, 3.3, 0, 4095)
    y_value = range_map(ioe.get_pin(hat1_ypin, ioe.MODE_ADC), 0, 3.3, 0, 4095)

    # Check if the joystick is within the deadzone
    if abs(x_value - 2048) < deadzone and abs(y_value - 2048) < deadzone:
        return 8  # Joystick is in the deadzone, so don't change the compass direction

    # Convert the x and y values to an angle in degrees
    angle = math.atan2(y_value - 2048, x_value - 2048) * (180 / math.pi)

    # Adjust the angle so that 0 degrees is north
    angle = (angle + 90) % 360

    # Map the angle to a value between 0 and 7
    compass_value = round(angle / 45) % 8

    return compass_value

print("Setup done Loading")

while True:

    pixels[0] = (255, 255, 0)
    pixels[1] = (0, 100, 255)
    pixels[2] = (0, 100, 255)
    #pixels[0] = (range_map(ax.value, 0, 65535, 0, 255), (range_map(ay.value, 0, 65535, 0, 255)), (range_map(az.value, 0, 65535, 0, 255)))
    #pixels[1] = (range_map(ax.value, 0, 65535, 0, 255), (range_map(ay.value, 0, 65535, 0, 255)), (range_map(az.value, 0, 65535, 0, 255)))
    #pixels[2] = (range_map(ax.value, 0, 65535, 0, 255), (range_map(ay.value, 0, 65535, 0, 255)), (range_map(az.value, 0, 65535, 0, 255)))
    
    pixels.show()

    for i, button in enumerate(buttons):
        #gamepad_button_num = i+1
        if ioe.get_pin(button, ioe.MODE_PULLUP):
            gp.release_buttons(button)
            led.value = False
            
           
        else:
            gp.press_buttons(button)
            led.value = True
            #print("button: ", button)
            #print("button ", gamepad_button_num)
     
#     hallx= ioe.get_pin(hat1_ypin, ioe.MODE_ADC)
#     hallmax = 65535
#     hallnormal = int(round(hallx * hallmax))
#     print("hall sensor test:{}".format(hallx))

# 
#     value = ioe.get_pin(10, ioe.MODE_PULLUP)
#     print("Button value is: {}".format(value))
    xvalue = range_map(ioe.get_pin(hat1_xpin, ioe.MODE_ADC), 0, 3.3, -127, 127)
    yvalue = range_map(ioe.get_pin(hat1_ypin, ioe.MODE_ADC), 0, 3.3, -127, 127)
    gp.move_joysticks(
        #x=range_map(ax.value, 0, 65535, -127, 127),
        x = int(xvalue),
        #y=range_map(ay.value, 0, 65535, -127, 127),
        y= int(yvalue),
        z=range_map(az.value, 0, 65535, -127, 127),
    )

    hat1_value = 0
   
    hat1_value = read_hat_switch()
    
   
    hat2_value = 0

                
    if hat1_value or hat2_value:
        gp.move_hats(
            hat1=hat1_value,
            hat2=hatvalue(hat2_value),
        )
     #   print("hat1 is:", hat1_value)
      #  print("hat2 is:", hat2_value)
        
    else:
        gp.move_hats(
            hat1=8,
            hat2=8,
       )
       # print("hat1 is:", hat1_value)
        #print("hat2 is:", hat2_value)
    #print("x", ax.value, "y", ay.value, "z", az.value)
    debounce()  