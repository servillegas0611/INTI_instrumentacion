# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 09:05:10 2025

@author: M.A. Real basado en prog Lean y Cia.
"""
import pyvisa
#from gpib_ctypes import gpib
import time
import matplotlib.pyplot as plt
import json 
import requests
import numpy as np
#import asyncio
import telnetlib
#import csv
import pandas as pd
from datetime import datetime
from SR830pythonClass import SR830 as sr830
import SignalRecovery7280 as sr7280
#import Ametek7124 as ame7124



# INPUTS ==============================
nro_medicion = input('Ingresar número de medición:')
sample = input('Ingrese la muestra: ')

field_start= 5.04 # initial field (T)
field_stop= 7.5 # final field (T)
field_step= 10e-3 #(T) step 10 mT 
field_time_wait= 6 # tiempo de espera campo (s)

frequency = 13.838 # Hz
voltage = 1.0 #V



# =====================================
#string para nombre de archivo
now = datetime.now()
str_file = nro_medicion + '_' + sample + '_' + now.strftime('%Y%m%d_%H%M%S') + '_G'
str_file_conf = nro_medicion + '_' + sample + '_' + now.strftime('%Y%m%d_%H%M%S') + '_G_conf'
print('Salvando en: ' + str_file + '.dat')



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
    INPUT
    -----
    TIME (array str): array of time to append or empty array
    Returns
    -------
    ahora (str): last value
    
    TIME (array str): appended array
    """
    ahora = datetime.now()
    print(ahora)
    TIME.append(ahora)
    return ahora, TIME


def conductance(GX, GY, ix, iy, vx, vy):
    """
    Evalua la conductancia compleja y devuelve cada componente en forma defloat
    y de array en unidades del cuanto (G0)

    Parameters
    ----------
    GX : array,  GY : array
    ix : float, iy : float, vx : float,  vy : float
    
    Returns
    -------
    gx : float, gy : float, GX : array, GY : array
    """
    G0 = 7.748091729e-5 # (S) cuantum conductance from CODATA
    v =  float(vx)**2 + float(vy)**2
    
    gx = (float(ix)*float(vx) + float(iy)*float(vy))/ v / G0
    gy = (float(iy)*float(vx) + float(ix)*float(vy))/ v / G0
    GX.append(gx)
    GY.append(gy)
    return gx, gy, GX, GY

#---------------------------------------------------------------------------



rm = pyvisa.ResourceManager()
# Listar equipos
equipos = rm.list_resources()
print('Equipos conectados:', equipos)


# Sig Rec 7280 ---------------------------------------------------
lia1 = rm.open_resource('GPIB1::12::INSTR')
# NOTA, MAR 2025: se utilizan dos GPIB porque lia1 (Sig Rec 7280) no permite por algún motivo
# meter otro instrumento en GPIB. Al conectar otro instr desaparecen todos. Puede
# ser que el inconvenieente venga por corriente?
str_term = 'EOI' 

# Ametek Sig Rec 7124 ---------------------------------------------------
# tn2 = lia2
#ip2='192.168.1.16'
#port2=50001
#tn2= telnetlib.Telnet(ip2,port2)

# SR830 ---------------------------------------------------
lia3obj = rm.open_resource('GPIB0::8::INSTR')
lia4obj = rm.open_resource('GPIB0::9::INSTR')
# instance for the SR830 class
lia3 = sr830(lia3obj)
lia4 = sr830(lia4obj)
# Take identities and modes
lia3.get_identity()
lia4.get_identity()
lia3.auto_scale()
lia4.auto_scale()
lia3mode = lia3.get_mode()
lia4mode = lia4.get_mode()
print('autoescalados los LIA 3 y 4')


# inicializo arrays
lia1X, lia1Y, lia2X, lia2Y, lia3X, lia3Y, lia4X, lia4Y = [], [], [], [], [], [], [], []
TIEMPO, TEMP, FIELD, FREQ = [], [], [], []
GX1, GY1, GX2, GY2 = [], [], [], []

# seteo excitacion LIA3
lia3.set_frequency(frequency)
lia3.set_amplitude(voltage)


# get MXC temperature
temp, TEMP = temperature_MXC(TEMP)
print('Temp = {temp}' + ' K')
# Save configuration and constants
config_data = {
    'fecha-hora': now.strftime('%Y-%m-%d %H:%M:%S'),
    'muestra': sample,
    'nro_medicion': nro_medicion,
    'temp_sample (K)': temp,
    'field_start': field_start,
    'field_stop': field_stop,
    'field_step': field_step,
    'field_time_wait': field_time_wait,
    'frequency (Hz)': frequency,
    'voltage (V)': voltage,
    'lia1': 'Signal Recovery 7280 DSP',
    'lia2': 'Ametek 7124',
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

    


######### ========== Field =================== ###########
host = "192.168.1.27"
port = 7180
timeout = 100000  # Tiempo de espera en segundos
tn = telnetlib.Telnet(host, port, timeout=timeout) 
######### ==================================== ###########
orden(tn, 'CONFigure:FIELD:TARGet ' + str(field_start))
orden(tn, "CONFigure:RAMP:RATE:FIELD 1,0.1,1")
orden(tn, "RAMP")


# plotting ------------------------------------------------------------------
fig, ax = plt.subplots(nrows= 2, ncols= 2, squeeze= False)      
line1X, = ax[0,0].plot(FIELD,lia1X, marker= '.', linestyle= '-', color= 'blue', label='LIA1x') 
line1Y, = ax[0,0].plot(FIELD,lia1Y, marker= '.', linestyle= '-', color= 'lightblue',  label='LIA1y') 
line3X, = ax[1,0].plot(FIELD,lia3X, marker= '.', linestyle= '-', color= 'green', label='LIA3x') 
line3Y, = ax[1,0].plot(FIELD,lia3Y, marker= '.', linestyle= '-', color= 'lightgreen', label='LIA3y') 
line4X, = ax[0,1].plot(FIELD,lia4X, marker= '.', linestyle= '-', color= 'red', label='LIA4x') 
line4Y, = ax[0,1].plot(FIELD,lia4Y, marker= '.', linestyle= '-', color= 'salmon', label='LIA4y')                       
lineGX1, = ax[1,1].plot(FIELD,GX1, marker= '.', linestyle= '-', color= 'purple', label='Gx1') 
lineGY1, = ax[1,1].plot(FIELD,GY1, marker= '.', linestyle= '-', color= 'orchid', label='Gy1')                       
lineGX2, = ax[1,1].plot(FIELD,GX2, marker= '.', linestyle= '-', color= 'black', label='Gx2') 
lineGY2, = ax[1,1].plot(FIELD,GY2, marker= '.', linestyle= '-', color= 'grey', label='Gy2')                       

#plot properties
ax[0,0].set_title('LIA1 vs Field')
ax[0,0].set_xlabel('Field (T)')
ax[0,0].set_ylabel('V (V)')
ax[0,0].legend(loc= 'upper right', bbox_to_anchor= (1,1))

ax[1,0].set_title('LIA3 vs FIELD')
ax[1,0].set_xlabel('Field (T)')
ax[1,0].set_ylabel('I (A)')
ax[1,0].legend(loc= 'upper right', bbox_to_anchor= (1,1))

ax[0,1].set_title('LIA4 vs Field')
ax[0,1].set_xlabel('Field (T)')
ax[0,1].set_ylabel('I (A)')
ax[0,1].legend(loc= 'upper right', bbox_to_anchor= (1,1))

ax[1,1].set_title('G vs field')
ax[1,1].set_xlabel('Field (T)')
ax[1,1].set_ylabel('G/G_0')
ax[1,1].legend(loc= 'upper right', bbox_to_anchor= (1,1))




for field in np.arange(field_start,field_stop+field_step,field_step):
    
    # cambia campo
    orden(tn, 'CONFigure:FIELD:TARGet ' + str(field))
    orden(tn, "CONFigure:RAMP:RATE:FIELD 1,0.1,1")
    orden(tn, "RAMP")
    FIELD.append(float(field))  
    plt.pause(field_time_wait)
    
    # Measure each LIA
    lia1x, lia1y = sr7280.outputs(lia1, str_term)
    lia3x, lia3y = lia3.read_x_y_output()                
    lia4x, lia4y = lia4.read_x_y_output()                
    
    # append to array
    lia1X.append(lia1x)
    lia1Y.append(lia1y) 
    lia3Y.append(lia3y)
    lia3X.append(lia3x)
    lia4X.append(lia4x)
    lia4Y.append(lia4y)
    
    # conductance
    gx1, gy1, GX1, GY1 = conductance(GX1, GY1, lia3x, lia3y, lia1x, lia1y)
    gx2, gy2, GX2, GY2 = conductance(GX2, GY2, lia4x, lia4y, lia1x, lia1y)
            
    # update axes with data
    line1X.set_data(FIELD, lia1X)
    line1Y.set_data(FIELD, lia1Y)
    line3X.set_data(FIELD, lia3X)
    line3Y.set_data(FIELD, lia3Y)
    line4X.set_data(FIELD, lia4X)
    line4Y.set_data(FIELD, lia4Y)
    lineGX1.set_data(FIELD,GX1) 
    lineGY1.set_data(FIELD,GY1)                       
    lineGX2.set_data(FIELD,GX2)                       
    lineGY2.set_data(FIELD,GY2)                       
    #rescale    
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
    print('Campo= {} T'.format(field))                                                   
    TIEMPO.append(fecha_hora_actual)
    # create dataframe to save data
    df=pd.DataFrame({'fecha-hora':TIEMPO, 
                     'FIELD':FIELD, 
                     'lia1X':lia1X,
                     'lia1Y':lia1Y, 
                     'lia3X':lia3X, 
                     'lia3Y':lia3Y,
                     'lia4X':lia4X, 
                     'lia4Y':lia4Y,
                     'gx1' : GX1,
                     'gy1' : GY1,
                     'gx2' : GX2,
                     'gy2' : GY2
                     })
    #save data
    df.to_csv('C:/Users/Leandro/Documents/mreal/202501_corbino/data/'+ str_file + '.dat', 
              index=False, sep=" ")
    
    plt.pause(1)        
    
    # Adjust sensitivity based on output
    lia3.adjust_sensitivity(lia3mode)
    lia4.adjust_sensitivity(lia4mode)

 