
# -*- coding: utf-8 -*-
"""
Programa de adquisición de datos de un termohigrómetro con interfaz gráfica.
Diseño de termohigrómetro por: Ricardo Iuzzolino, Juan Ignacio Medved 

Software de adquisición de datos por: 
Author: Juan Pablo Catolino
Date: 2024/04
Modified by: Mariano A. Real
Date: 2024/12
This script acquires data from a thermohygrometer with a graphical interface.

Functions:
    list_serial_ports(): Lists all available serial ports and prints their device names and descriptions.
    read_data(arduino, command): Sends a command to the Arduino and reads the response.

Usage:
    The script lists available serial ports, sets up a serial connection to an Arduino device, 
    sends commands to read temperature, humidity, and pressure data, and prints the results.
"""

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
def open_serial_connection(port= 'COM4', baudrate= 115200, timeout= 1):
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
    arduino = serial.Serial(port, baudrate, timeout= timeout)
    arduino.flush()
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


# INPUTS ==============================
nombre_medicion = input('Ingresar nombre de medición \n' + 
                        '(el programa incluirá fecha y hora en el nombre del archivo): ')

# =====================================
# string para nombre de archivo
now = datetime.now()
str_file = nombre_medicion + '_' + now.strftime('%Y%m%d_%H%M%S')
print('Salvando en: ' + str_file + '.dat')


# List all available serial ports
list_serial_ports()

# Set up the serial connection parameters
port = 'COM3'
baudrate = 115200
v_timeout = int(1)
# Open the serial connection
arduino = open_serial_connection(port, baudrate, timeout= v_timeout)

# inicializo arrays
array_time, array_T, array_H, array_P = [], [], [], []

# Read arduino and save to file
try:
    while True:
        print('Reading data from the Arduino...\n')
        print('To interrupt the program press CRT+C\n')
        
        # Read temperature, humidity, and pressure data and print the results
        T = float(read_data(arduino, 'T?\r\n'))
        H = float(read_data(arduino, 'H?\r\n'))
        P = float(read_data(arduino, 'P?\r\n'))
        t = datetime.now() 
        
        # Guardo en arrays
        array_time.append(t)
        array_T.append(T)
        array_H.append(H)
        array_P.append(P)
        
        # Guardo en archivo .dat
        df = pd.DataFrame({'time': array_time, 'T': array_T, 'H': array_H, 'P': array_P})
        df.to_csv(str_file + '.dat', index=False, sep='\t')
        
        # Print the results
        print('Time = {}'.format(t))
        print('Temperatura = {} °C'.format(T))
        print('Humedad = {} %'.format(H))
        print('Presión = {} hPa'.format(P))

        time.sleep(10)  # Wait for 1 second before reading the data again

except KeyboardInterrupt:
    print("Data acquisition stopped by user.")

finally:
    arduino.close()


