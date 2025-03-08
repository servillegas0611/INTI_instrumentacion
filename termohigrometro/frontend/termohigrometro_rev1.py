'''
    Title: Termohigrometro_rev1.py
    author: https://github.com/realmariano
    Date: 2025-03
    based on work of J.P. Catolino and using GitHub copilot assistance.

    Description: This script reads data from a DHT11 sensor and sends it to an Arduino device via serial communication.
    
    The Arduino then processes the data and sends it back to the Python script for display.
    
    This module provides functions to list available serial ports, establish a serial connection
    to an Arduino device, and read data from the Arduino.
    Functions:
        list_serial_ports():
        open_serial_connection(port='COM3', baudrate=115200, timeout=1):
        read_data(arduino, command):
    Dependencies:
        - serial
        - serial.tools.list_ports
        - time
        - pandas as pd
        - datetime
    Usage Example:
        ports = list_serial_ports()
        arduino = open_serial_connection(port='COM3', baudrate=115200, timeout=1)
        response = read_data(arduino, 'YOUR_COMMAND')

'''
# Import the necessary libraries
import serial
import serial.tools.list_ports
import time
import pandas as pd
from datetime import datetime

# List all available serial ports
def list_serial_ports():
    """
    Lists all available serial ports and prints their device names and descriptions.
    This function uses the `serial.tools.list_ports.comports()` method to retrieve
    a list of available serial ports on the system. For each port, it prints the
    device name and description.
    Returns:
        None
    """
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print(f"Device: {port.device}, Description: {port.description}")

# Open the serial connection
def open_serial_connection(port='COM3', baudrate=115200, timeout=1):
    """
    Establishes a serial connection to an Arduino device.
    Parameters:
    port (str): The serial port to connect to (default is 'COM3').
    baudrate (int): The baud rate for the serial communication (default is 115200).
    timeout (int or float): The timeout value for the serial connection in seconds (default is 1).
    Returns:
    serial.Serial: An instance of the serial connection to the Arduino.
    Raises:
    serial.SerialException: If the connection to the specified port cannot be established.
    """
    arduino = serial.Serial(port, baudrate, timeout=timeout)
    arduino.flushInput()  # Flush the input buffer
    arduino.flushOutput()  # Flush the output buffer
    time.sleep(2)  # Wait for the connection to be established
    return arduino

# Read data from the Arduino
def read_data(arduino, command):
    """
    Sends a command to the Arduino and reads the response.
    Args:
        arduino: The serial connection to the Arduino.
        command (str): The command to send to the Arduino.
    Returns:
        str: The response from the Arduino, decoded and stripped of any leading/trailing whitespace.
    Note:
        The function waits for 2 seconds after sending the command to ensure the connection is established.
    """
    arduino.write(command.encode())
    line = arduino.readline()
    arduino.flush()
    time.sleep(2)  # Wait for the connection to be established
    return line.decode().strip()