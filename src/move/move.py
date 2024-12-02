import serial
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
        if key.char in {'q', 'a', 'w', 's', 'e', 'd', 'y','h','u','j','i','k'}:
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
