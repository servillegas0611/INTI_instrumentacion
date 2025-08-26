
"""
--------------------------------------------------------
 Automatic Measurement Program with Keithley 6430
--------------------------------------------------------

⚠️ IMPORTANT:
This program is intended **only** for automatic
measurements using the Keithley electrometer
in source (generator) mode.

By selecting the index, you specify which
quantity is being measured:
    - 0 → Voltage
    - 1 → Current
    - 2 → Resistance

Measurement settings must be configured
manually on the instrument. For example:
    - Set the range to 20 V when measuring ~19 V

The program will automatically:
    - Control the instrument via PyVISA
    - Perform 10 measurements
    - Create a timestamped .txt file
      with the results
    - Play a buzzer sound at the end to
      indicate that the measurement is finished

Requirements:
    - Python 3.x
    - pyvisa library
"""

import os
import pyvisa
import time
from datetime import datetime
import winsound

print("\n")

index = 0   #  0=voltage, 1=current, 2=resistance

#index = int(input("Enter 0 for voltage, 1 for current, 2 for resistance: "))
if index == 0:
            units ='Volt'
            parameter='VOLT'
elif index == 1:
            units ='Ampere'
            parameter='CURR'
elif index == 2:
            units ='Ohm'
            parameter='RES'    

# Generate file name with current date and time
now = datetime.now()
file_name = now.strftime("%Y-%m-%d_%H-%M-%S") + ".txt"

script_dir = os.path.dirname(os.path.abspath(__file__))
output_file = open(os.path.join(script_dir, file_name), 'w')


# Create file to save results
#output_file = open('C:\\Users\\lvillegas\\Documents\\Calibrator_Electrometer\\Electrometer\\' + file_name, 'w')
output_file.write('Range (A)\tReading 1\tReading 2\tReading 3\tReading 4\tReading 5\tReading 6\tReading 7\tReading 8\tReading 9\tReading 10\n')

# Connect to the instrument
rm = pyvisa.ResourceManager()
Keithley = rm.open_resource('GPIB0::26::INSTR')

Keithley.timeout = 20000
# Terminations
Keithley.write_termination = '\n'
Keithley.read_termination = '\n'

#Keithley.write(':SENS:VOLT:PROT 21')   # Current protection at 100 mA
Keithley.write(':OUTP ON')              # Enable output

values_float = []
rango= Keithley.query(':SENS:{}:RANG?'.format(parameter)) 
print('Range:', rango.strip())
output_file.write(rango.strip())


print("\nTaking 10 measurements, one every 5 seconds...\n")
for i in range(10):
    reading = Keithley.query(':READ?')
    print(f'Reading #{i+1}:', reading.strip())

    values = reading.strip().split(',')
    if len(values) >= 2:
        value_str = values[index].strip()
        print(f'  Extracted value: {value_str}'+ ' {0}'.format(units))
            
        try:
            current_float = float(value_str)
            values_float.append(current_float)
        except ValueError:
            print('  Error converting to number.')
    else:
        print('  Could not extract the current.')

    time.sleep(5)

# Average
if values_float:
    avg = sum(values_float) / len(values_float)
    print('\nAverage value: {:.6E}'.format(avg) + ' {0}'.format(units))
else:
    print('\nNot enough data to calculate average.')

# Save row in the file
measurements_txt = '\t'.join(['{:.6E}'.format(c) for c in values_float])
output_file.write(f'\t{measurements_txt}\n')

# Deactivate output for the next cycle
#Keithley.write(':OUTP OFF')

time.sleep(5)

# Deactivate output (if needed)
#F5500.write("STBY")

rm.close()

# Sound notification sequence
winsound.Beep(frequency=500, duration=500)  # 500 Hz, 0.5 seconds
time.sleep(2)
winsound.Beep(frequency=500, duration=500)
time.sleep(2)
winsound.Beep(frequency=500, duration=500)

print(f"\nMeasurements completed. File saved as '{file_name}'.")