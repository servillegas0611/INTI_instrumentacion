'''
    Title: Termohigrometro_rev1.py
    author: https://github.com/realmariano
    Date: 2025-03
    based on work of J.P. Catolino and using GitHub copilot assistance.

'''
import json
from datetime import datetime
import pandas as pd
import time
from termohigrometro_rev1 import list_serial_ports, open_serial_connection, read_data

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
arduino = open_serial_connection(port, baudrate, timeout=v_timeout)

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
        
        # Save the latest values to a JSON file
        latest_values = {'time': t.strftime('%Y-%m-%d %H:%M:%S'), 'T': T, 'H': H, 'P': P}
        with open('latest_values.json', 'w') as f:
            json.dump(latest_values, f)

        # Print the results
        # print('Time = {}'.format(t))
        # print('Temperatura = {} °C'.format(T))
        # print('Humedad = {} %'.format(H))
        # print('Presión = {} hPa'.format(P))

        time.sleep(10)  # Wait for 10 seconds before reading the data again

except KeyboardInterrupt:
    print("Data acquisition stopped by user.")

finally:
    arduino.close()