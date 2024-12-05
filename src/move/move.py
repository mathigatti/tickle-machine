import math
import serial
import threading
from time import sleep
from pynput import keyboard

# Configure the serial connection
arduino_port = "/dev/ttyUSB0"  # Replace with your Arduino's serial port
baud_rate = 9600       # Must match the baud rate in the Arduino sketch

# Create a serial connection
try:
    ser = serial.Serial(arduino_port, baud_rate, timeout=1)
    print(f"Connected to Arduino on {arduino_port}")
except Exception as e:
    print(f"Failed to connect to Arduino: {e}")
    exit()

# Function to read from Arduino
def read_from_arduino():
    while True:
        try:
            if ser.in_waiting > 0:
                message = ser.readline().decode().strip()
                if message:
                    print(f"Received: {message}")
        except Exception as e:
            print(f"Error reading from Arduino: {e}")
            break



def valor(i):
    x_total_cm = 100
    z_total_cm = 200
    y_total_cm = 220

    x = x_total_cm/2
    y = 0
    z = z_total_cm*2/5

    max_v = 100
    base = 0
    return (x, abs(math.sin(i))*max_v+base, z)

# Start the read thread
read_thread = threading.Thread(target=read_from_arduino)
read_thread.daemon = True
read_thread.start()

# Define a function to send messages to the Arduino
def send_to_arduino(message):
    try:
        ser.write(message.encode())  # Send the message
        print(f"Sent: {message}")
    except Exception as e:
        print(f"Error sending to Arduino: {e}")

# Define a callback for key presses
def on_press(key):
    try:
        if key.char == "1":
            #text = input()
            for i in range(100):
                coord = valor(i)
                #print(text)
                send_to_arduino(str(coord).replace(" ", ""))
                sleep(0.5)
            
        if key.char in {'q', 'a', 'w', 's', 'e', 'd', 'y', 'h', 'u', 'j', 'i', 'k', 'm', 'n', 'b', 'c','v'}:
            send_to_arduino(key.char.upper())  # Send the command in uppercase
    except AttributeError:
        # Handle special keys (non-character keys)
        pass

# Define a callback for key releases
def on_release(key):
    if key == keyboard.Key.esc:
        # Stop listener
        print("Exiting...")
        return False

# Start listening to the keyboard
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

# Close the serial connection when done
if ser.is_open:
    ser.close()
