# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 09:05:10 2025

@author: M.A. Real basado en prog Lean y Cia.
"""
import pyvisa
#from gpib_ctypes import gpib
import time
import matplotlib.pyplot as plt
#import json 
#import requests
import numpy as np
#import asyncio
import telnetlib
#import csv
import pandas as pd
from datetime import datetime


# INPUTS ==============================
nro_medicion = input('Ingresar número de medición:')
f_init = 1e2
f_final = 1e5
n_freq = 1000 
# =====================================

#string para nombre de archivo
now = datetime.now()
str_file = nro_medicion + '_' + now.strftime('%Y%m%d_%H%M%S') 
print(str_file)



#  definicion de funciones --------------------------------------------------
def outputs7280(lockin, str_term):   
    # lia1    
    lia1x = lia1.query('X. ' + str_term)     # Returns signal magnitude singal
    lia1y = lia1.query('Y. ' + str_term)     # Returns signal magnitude singal
    print(float(lia1x))
    print(float(lia1y))
    return lia1x, lia1y


def outputsSR830(lockin):
    x = lockin.query('OUTP? 1')
    y = lockin.query('OUTP? 2')
    print(float(x), float(y))
    return x, y
    
def freqSR830(lockin):
    freq = lockin.query('FREQ?')
    print(float(freq))
    return freq


def outputsAm7124(tn2):
    command='X.'
    tn2.write(command.encode('utf-8') + b"\n")
    response=tn2.read_until(b'\n',timeout=1)
    lia2x=response.decode('utf-8')[:-5]
    print(float(lia2x))

    command='Y.'
    tn2.write(command.encode('utf-8') + b"\n")
    response=tn2.read_until(b'\n',timeout=1)
    lia2y=response.decode('utf-8')[:-5]
    print(float(lia2y))
    return lia2x, lia2y
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

# SR830 ---------------------------------------------------
lia3 = rm.open_resource('GPIB0::8::INSTR')
lia4 = rm.open_resource('GPIB0::9::INSTR')

# Ametek Sig Rec 7124 ---------------------------------------------------
# tn2 = lia2
ip2='192.168.1.16'
port2=50001
tn2= telnetlib.Telnet(ip2,port2)

str_term = 'EOI' 


lia1X = []
lia1Y = []
lia2X = []            
lia2Y = []     
lia3X = []
lia3Y = []
lia4X = []
lia4Y = []
FREQ = [] 
TIEMPO = []
frequencies = np.logspace(np.log10(f_init), np.log10(f_final), n_freq)

# plotting ------------------------------------------------------------------
fig, ax = plt.subplots(nrows= 2, ncols= 1, squeeze= False)      
line1X, = ax[0,0].plot(FREQ,lia1X, marker= 'o', linestyle= '-', color= 'blue', label='LIA1') 
line2X, = ax[0,0].plot(FREQ,lia2X, marker= 'o', linestyle= '-', color= 'orange', label='LIA2') 
line3X, = ax[0,0].plot(FREQ,lia3X, marker= 'o', linestyle= '-', color= 'green', label='LIA3') 
line4X, = ax[0,0].plot(FREQ,lia4X, marker= 'o', linestyle= '-', color= 'red', label='LIA4') 
line1Y, = ax[1,0].plot(FREQ,lia1Y, marker= 'o', linestyle= '-', color= 'blue',  label='LIA1') 
line2Y, = ax[1,0].plot(FREQ,lia2Y, marker= 'o', linestyle= '-', color= 'orange', label='LIA2') 
line3Y, = ax[1,0].plot(FREQ,lia3Y, marker= 'o', linestyle= '-', color= 'green', label='LIA3') 
line4Y, = ax[1,0].plot(FREQ,lia4Y, marker= 'o', linestyle= '-', color= 'red', label='LIA4')                       

#plot properties
ax[0,0].set_xscale('log')
ax[0,0].set_title('X vs freq')
ax[0,0].set_xlabel('freq (Hz)')
ax[0,0].set_ylabel('X (V)')
ax[0,0].legend(loc= 'upper right', bbox_to_anchor= (1,1))
ax[1,0].set_xscale('log')
ax[1,0].set_title('Y vs freq')
ax[1,0].set_xlabel('freq (Hz)')
ax[1,0].set_ylabel('Y (V)')
ax[1,0].legend(loc= 'upper right', bbox_to_anchor= (1,1))


for freq in frequencies:    
    FREQ.append(float(freq))
    # set freq to reference
    lia3.write(f'FREQ {freq}')
    time.sleep(1)
    
    # Measure each LIA
    lia1x, lia1y = outputs7280(lia1, str_term)
    lia1X.append(float(lia1x))
    lia1Y.append(float(lia1y))
    lia2x,lia2y = outputsAm7124(tn2)
    lia2X.append(float(lia2x))
    lia2Y.append(float(lia2y))
    lia3x, lia3y = outputsSR830(lia3)
    lia4x, lia4y = outputsSR830(lia4)
    lia3X.append(float(lia3x))
    lia3Y.append(float(lia3y))
    lia4X.append(float(lia4x))
    lia4Y.append(float(lia4y))
        
    # update axes with data
    line1X.set_data(FREQ, lia1X)
    line2X.set_data(FREQ, lia2X)
    line3X.set_data(FREQ, lia3X)
    line4X.set_data(FREQ, lia4X)
    line1Y.set_data(FREQ, lia1Y)
    line2Y.set_data(FREQ, lia2Y)
    line3Y.set_data(FREQ, lia3Y)
    line4Y.set_data(FREQ, lia4Y)
    #rescale    
    ax[0,0].relim()
    ax[0,0].autoscale_view()
    ax[1,0].relim()
    ax[1,0].autoscale_view()

    
    fecha_hora_actual = datetime.now()
    print(fecha_hora_actual)
    TIEMPO.append(fecha_hora_actual)
    
    df=pd.DataFrame({'fecha-hora':TIEMPO, 
                     'freq':FREQ, 
                     'lia1X':lia1X,
                     'lia1Y':lia1Y, 
                     'lia2X':lia2X, 
                     'lia2Y':lia2Y,
                     'lia3X':lia2X, 
                     'lia3Y':lia2Y,
                     'lia4X':lia2X, 
                     'lia4Y':lia2Y
                     })
    
    
    df.to_csv('C:/Users/Leandro/Documents/mreal/202501_corbino/data/'+ str_file + '_freq_response_LIAs' + '.dat', 
              index=False, sep=" ")
    
    
    plt.pause(1)

 
 
 
 