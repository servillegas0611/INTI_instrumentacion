# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 09:05:10 2025

@author: M.A. Real basado en prog Lean y Cia.
"""
import pyvisa
import time
import matplotlib.pyplot as plt
import json 
import requests
import numpy as np
import telnetlib
import pandas as pd
from datetime import datetime
from SR830pythonClass_rev2 import SR830 as sr830
#import SignalRecovery7280 as sr7280
#import Ametek7124 as ame7124
#from gpib_ctypes import gpib
#import asyncio
#import csv

#### =======   INPUTS  ========================####
# Modify before start
# se asume que LIA3 es el que da la tensión
# LIAs en Harm = 2
field_start= 4.3 # initial field (T)
field_stop= 0.5 # final field (T)
field_step= -0.005 #(T) 
field_time_wait= 10 # tiempo de espera campo (s)

frequency = 13.838 # Hz
voltage = [0.01, 0.1, 0.2, 0.6, 0.8] # V  se pueden seleccionar varios poniendolos en forma de array






## -----------  definicion de funciones adicionales -------------------------##

##============== heater function  ===============## 
def heater(p,t,ON):
    DEVICE_IP = '192.168.1.1'
    # Timeout for http operations (in ms)
    TIMEOUT = 1000
    url = 'http://{}:5001/heater/update'.format(DEVICE_IP)
    data = {
     'heater_nr': 4,
     'power': p,
      'active':ON
    }
    req = requests.post(url, json=data, timeout=TIMEOUT)
    data = req.json()
    print('Response: \n{}'.format(json.dumps(data, indent=2)))
    time.sleep(t)
    return None 

## ============ telnet =====================================================##
def consultap(tn, code, info):
    command =  code
    tn.write(command.encode('ascii') + b"\n")
    response = tn.read_until(b"\n").decode('ascii').strip()
    print(info + ": " + response)
    
def consulta(tn, code):
    command =  code
    tn.write(command.encode('ascii') + b"\n")
    return tn.read_until(b"\n").decode('ascii').strip()
    
def orden(tn, code):
    command =  code
    tn.write(command.encode('ascii') + b"\n")

## ======== Temperatures =================================================== ##       

def temperature_MXC(TEMP_mxc):
    """
    Requests the mixing chamber temperature (MCX), it waits 3 s.
    Requirements: import json

    Parameters
    ----------
    TEMP_mxc : (array) empty or temperature array.

    Returns
    -------
    t_mxc : (float) temperature (K)
        
    TEMP_mxc : (array) of temperatures (K)
    """
    while True:
        req= requests.get("http://192.168.1.1:5001/channel/measurement/latest", timeout=10)
        data = req.json()
        ch=6 ##mxc temperature channel
        if data.get('channel_nr')==ch:
            t_mxc=round(data.get('temperature')*1e3,4)
            break
    time.sleep(3)
    TEMP_mxc.append(t_mxc)
    return t_mxc, TEMP_mxc

## ======== MISC FUNC  ===================================================== ##       
def get_time(TIME):    
    """
    This func gets the current time and date
    INPUT:      TIME (array str): array of time to append or empty array
    Returns:    ahora (str): last value
                TIME (array str): appended array
    """
    ahora = datetime.now()
    print(ahora)
    TIME.append(ahora)
    return ahora, TIME

def gain_ampli(gain_dB):
    '''
    Evaluates de ampli gain from dB to factor
    Parameters:     ganancia_dB (float)
    Returns:        amplification factor (float)
    '''
    amplification= 10**(float(gain_dB) / 20)
    return amplification
    
def ask_user_number(str_to_show):
    while True:
        try:
            user_input = input(str(str_to_show))
            number = float(user_input)
            return number
            break
        except ValueError:
            print('Invalid input. Please enter a number')
            
#---------------------------------------------------------------------------



# INPUTS to be asked when starting ===================================
nro_medicion = input('Ingresar número de medición: ')
sample = input('Ingrese la muestra: ')
ganancia_ampli_1 = ask_user_number('Ingrese setting amp1 (dB):')
ganancia_ampli_2 = ask_user_number('Ingrese setting amp1 (dB):')
# ====================================================================
tipo_medicion = 'Vtp'
meas_harmonic = 2


#string para nombre de archivo
now = datetime.now()
str_file = nro_medicion + '_' + sample + '_' + now.strftime('%Y%m%d_%H%M%S') + '_' + tipo_medicion
str_file_conf = nro_medicion + '_' + sample + '_' + now.strftime('%Y%m%d_%H%M%S') + '_' + tipo_medicion + '_conf'
print('Salvando en: ' + str_file + '.dat')


# LOAD  VISA AND INSTRUMENTS
rm = pyvisa.ResourceManager()
# Listar equipos
equipos = rm.list_resources()
print('Equipos conectados:', equipos)


# SR830 ---------------------------------------------------

lia3obj = rm.open_resource('GPIB0::8::INSTR')
lia4obj = rm.open_resource('GPIB0::9::INSTR')
# instance for the SR830 class
lia3 = sr830(lia3obj)
lia4 = sr830(lia4obj)
# Take identities and modes
lia3.get_identity()
lia4.get_identity()
# set harmonic for Vtp detection
lia3.set_harmonic(meas_harmonic)
lia4.set_harmonic(meas_harmonic)
# set time constant to 1 s (index = 10)
lia3.set_time_constant(10) 
lia3.set_time_constant(10)
# auto scale initially
lia3.auto_scale()
time.sleep(10) # the Vtp is really slow
lia4.auto_scale()
time.sleep(10)
# mode of operation
lia3mode = lia3.get_mode()
lia4mode = lia4.get_mode()

print('autoescalados los LIA 3 y 4')


# inicializo arrays
lia1X, lia1Y, lia2X, lia2Y, lia3X, lia3Y, lia4X, lia4Y = [], [], [], [], [], [], [], []
TIEMPO, TEMP, FIELD, FREQ = [], [], [], []
GX1, GY1, GX2, GY2 = [], [], [], []

# seteo excitacion LIA3
lia3.set_frequency(frequency)
lia3.set_amplitude(voltage[0])


# get MXC temperature
temp, TEMP = temperature_MXC(TEMP)

# Save configuration and constants
config_data = {
    'fecha-hora': now.strftime('%Y-%m-%d %H:%M:%S'),
    'muestra': sample,
    'nro_medicion': nro_medicion,
    'tipo de medicion': tipo_medicion,
    'temp_sample (K)': temp,
    'field_start': field_start,
    'field_stop': field_stop,
    'field_step': field_step,
    'field_time_wait': field_time_wait,
    'frequency (Hz)': frequency,
    'voltage heater (V)': voltage,
    'lia3': lia3.get_identity(),
    'lia3_mode (0:A, 1: A-B, 2: I1, 3: I2)': lia3.get_mode(),
    'lia3_sensitivity': lia3.get_full_scale(lia3.get_sensitivity()),
    'lia3_time_constant': lia3.get_time_constant(),
    'lia4': lia4.get_identity(),
    'lia4_mode (0:A, 1: A-B, 2: I1, 3: I2)': lia4.get_mode(),
    'lia4_sensitivity': lia4.get_full_scale(lia4.get_sensitivity()),
    'lia4_time_constant': lia4.get_time_constant()
}

with open('C:/Users/Leandro/Documents/mreal/202501_corbino/data/' + str_file_conf + '.json', 'w') as config_file:
    json.dump(config_data, config_file, indent=4)

    


# ######### ========== Field =================== ###########
host = "192.168.1.27"
port = 7180
timeout = 100000  # Tiempo de espera en segundos
tn = telnetlib.Telnet(host, port, timeout=timeout) 
# ######### ==================================== ###########
orden(tn, 'CONFigure:FIELD:TARGet ' + str(field_start))
orden(tn, "CONFigure:RAMP:RATE:FIELD 1,0.1,1")
orden(tn, "RAMP")




lia_data = [lia3X, lia3Y, lia4X, lia4Y] # array of arrays for manage data

# Initialize plot ------------------------------------------------------------------
fig, ax = plt.subplots(nrows= 2, ncols= 2, squeeze= False)      
line3X, = ax[0,0].plot(FIELD, lia_data[0], marker= '.', linestyle= '-', color= 'green', label='LIA3x 2f') 
line3Y, = ax[1,0].plot(FIELD, lia_data[1], marker= '.', linestyle= '-', color= 'lightgreen', label='LIA3y 2f') 
line4X, = ax[0,1].plot(FIELD, lia_data[2], marker= '.', linestyle= '-', color= 'red', label='LIA4x 2f') 
line4Y, = ax[1,1].plot(FIELD, lia_data[3], marker= '.', linestyle= '-', color= 'salmon', label='LIA4y 2f')                       

lines = [line3X, line3Y, line4X, line4Y]

# plot properties
ax[0,0].set_title('LIA3x-2f vs Field')
ax[0,0].set_xlabel('Field (T)')
ax[0,0].set_ylabel('V_{2f} (V)')
ax[0,0].legend(loc= 'upper right', bbox_to_anchor= (1,1))

ax[1,0].set_title('LIA3y-2f vs Field')
ax[1,0].set_xlabel('Field (T)')
ax[1,0].set_ylabel('V_{2f} (V)')
ax[1,0].legend(loc= 'upper right', bbox_to_anchor= (1,1))

ax[0,1].set_title('LIA4x-2f vs Field')
ax[0,1].set_xlabel('Field (T)')
ax[0,1].set_ylabel('V_{2f} (V)')
ax[0,1].legend(loc= 'upper right', bbox_to_anchor= (1,1))

ax[1,1].set_title('LIA4y-2f vs Field')
ax[1,1].set_xlabel('Field (T)')
ax[1,1].set_ylabel('V_{2f} (V)')
ax[1,1].legend(loc= 'upper right', bbox_to_anchor= (1,1))




reverse = False # will reverse the direccion of the mag field

for i, voltage_heater in enumerate(voltage):
    
    if i != 0:
        # set voltage to next value
        lia3.set_amplitude(voltage_heater)
        # Adjust sensitivity based on output
        lia3.adjust_sensitivity(lia3mode)
        lia4.adjust_sensitivity(lia4mode)

    if reverse:
        # B field up
        field_init  = field_stop
        field_end   = field_start
        field_delta  = -field_step
    else:
        field_init  = field_start
        field_end   = field_stop
        field_delta  = field_step


    for field in np.arange(field_init,field_end+field_delta,field_delta):
        
        # cambia campo
        orden(tn, 'CONFigure:FIELD:TARGet ' + str(field))
        orden(tn, "CONFigure:RAMP:RATE:FIELD 1,0.1,1")
        orden(tn, "RAMP")
        FIELD.append(float(field))                                                     
        plt.pause(field_time_wait)
        
        # Measure each LIA
        lia3x, lia3y = lia3.read_x_y_output()
        lia4x, lia4y = lia4.read_x_y_output()
        lia3Y.append(lia3y/gain_ampli(ganancia_ampli_1))
        lia3X.append(lia3x/gain_ampli(ganancia_ampli_1))
        lia4X.append(lia4x/gain_ampli(ganancia_ampli_2))
        lia4Y.append(lia4y/gain_ampli(ganancia_ampli_2))

        lia_data = [lia3X, lia3Y, lia4X, lia4Y]

        

        # update axes with data
        for i, line in enumerate(lines):
            # update axes with data
            line.set_data(FIELD, lia_data[i])
        
        # rescale
        ax[0,0].relim()
        ax[0,0].autoscale_view()
        ax[1,0].relim()
        ax[1,0].autoscale_view()
        ax[0,1].relim()
        ax[0,1].autoscale_view()
        ax[1,1].relim()
        ax[1,1].autoscale_view()
        
        
        
        fecha_hora_actual = datetime.now()
        print(fecha_hora_actual)
        print(field)
        TIEMPO.append(fecha_hora_actual)
        # create dataframe to save data
        df=pd.DataFrame({'fecha-hora':TIEMPO, 
                        'FIELD':FIELD, 
                        'lia3X':lia3X, 
                        'lia3Y':lia3Y,
                        'lia4X':lia4X, 
                        'lia4Y':lia4Y
                        })
        #save data
        df.to_csv('C:/Users/Leandro/Documents/mreal/202501_corbino/data/'+ str_file + 'Vheater_{}'.format(voltage_heater) + '_V.dat', 
                index=False, sep=" ")
        
        plt.pause(1)        
        
        # Adjust sensitivity based on output
        lia3.adjust_sensitivity(lia3mode)
        lia4.adjust_sensitivity(lia4mode)

    reverse = not reverse  # changes de direccion of the mag field
    