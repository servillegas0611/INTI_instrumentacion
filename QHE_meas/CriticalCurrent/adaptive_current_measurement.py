# -*- coding: utf-8 -*-
"""
Script para medir la resistencia de un dispositivo utilizando un multímetro y una fuente de alimentación, 
con ajuste dinámico del paso de corriente.
El script realiza una rampa de corriente desde 0 A hasta un máximo definido, midiendo el tension y calculando 
la resistencia en cada paso.
-------------------------------------------------------------------
2025-04-17
Autor: Elian Urtubey, Federico Huxhagen, M. Real
"""


import time
from clases import Multimeter34420A, Multimeter3458A, PowerSupply
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os

## USER INPUTS ##########################################################################
# Configura los recursos de los instrumentos
multimeter_resource = "GPIB0::13::INSTR"  # Multímetro Agilent 34420A
multimeter3458_resource = "GPIB0::22::INSTR"  # Multímetro Agilent 3458A
power_supply_resource = "GPIB1::12::INSTR"  # Fuente de alimentación Keithley 6220

# Parámetros iniciales
initial_step = 2e-6  # Paso inicial de corriente
min_step = 0.5e-6       # Paso mínimo de corriente
max_current = 200e-6    # Corriente máxima 
init_current =  10e-6   # Corriente inicial
resistance_threshold = 0.02   # Umbral de cambio de resistencia
#######################################################################################



print("Configuración corrientes:")
print(f"Paso mínimo: {min_step} A")
print(f"Corriente máxima: {max_current} A")
print(f"Corriente inicial: {init_current} A")
print(f"Umbral de cambio de resistencia: {resistance_threshold} ohm") 


# Inicializa las listas para guardar los datos
corriente = []
tension = []
tension3458 = []
resistencia = []
resistencia_hall = []

# Conecta los instrumentos
m = Multimeter34420A(multimeter_resource)
m.connect()
voltage = float(m.measure_voltage_dc())

mh = Multimeter3458A(multimeter3458_resource)
mh.connect()
mh.configure_voltage_dc(NPLC=20)
voltage3458 = float(mh.measure_voltage_dc())


fuente = PowerSupply(power_supply_resource)
fuente.connect()
fuente.output_off()  # Asegúrate de que la salida esté apagada antes de configurar
fuente.set_triax_inner_shield("OLOW")  # Configura el malla interno a GUARD
fuente.set_current_range_auto()  # Configura el rango de corriente en automático
fuente.set_current(init_current)  # Configura la corriente inicial
fuente.output_on()  # Enciende la salida

    
# Guarda los datos en un archivo
# -----------------------------------------------
current_folder = os.getcwd() # directorio actual
subfolder = os.path.join(current_folder, "Mediciones") # Define el subdirectorio "Mediciones"
# Crea el subdirectorio si no existe
if not os.path.exists(subfolder):
    os.makedirs(subfolder)
# Construye la ruta completa del archivo usando fecha y hora
now = datetime.now()
file_name = f"corrienteCritica_{now.strftime('%Y%m%d-%H%M%S')}.dat"
file_path = os.path.join(subfolder, file_name)
print(f"Se guardan los datos en: {file_path}")
np.savetxt(file_path, np.column_stack((corriente, tension, resistencia, tension3458, resistencia_hall)), header="Corriente (A);Vxx (V); Rxx (ohm); Vhall (V); Rhall (ohm)", delimiter=";")


# Inicializa la figura para la gráfica en tiempo real
# -----------------------------------------------
plt.ion()  # Habilita el modo interactivo
fig, ax = plt.subplots()
line, = ax.plot([], [], marker='o', label="Resistencia vs Corriente")
ax.set_xlabel("Corriente (A)")
ax.set_ylabel("Resistencia (ohm)")
ax.set_title("Resistencia vs Corriente (Medición en tiempo real)")
ax.grid()
ax.legend()

# Realiza la medición con ajuste dinámico del paso
current = init_current  # Corriente inicial
step = initial_step
previous_resistance = 0

while current < max_current:
    # Configura la corriente
    current += step
    fuente.set_current(current)
    time.sleep(1)  # Espera para estabilizar

    # Mide el tension
    voltage = float(m.measure_voltage_dc())
    voltage3458 = float(mh.measure_voltage_dc())
    corriente.append(current)
    tension.append(voltage)
    tension3458.append(voltage3458)
    resistance = voltage / current if current != 0 else 0
    resistencia.append(resistance)
    resistance_hall = voltage3458 / current if current != 0 else 0
    resistencia_hall.append(resistance_hall)


    # Actualiza la gráfica en tiempo real
    line.set_xdata(corriente)
    line.set_ydata(resistencia)
    ax.relim()  # Recalcula los límites
    ax.autoscale_view()  # Ajusta la escala automáticamente
    plt.draw()
    plt.pause(0.01)  # Pausa breve para actualizar la gráfica

    # Calcula el cambio de resistencia
    resistance_change = abs(resistance - previous_resistance)

    # Ajusta el paso de corriente si el cambio de resistencia excede el umbral
    if resistance_change > resistance_threshold and step > min_step:
        step /= 2  # Reduce el paso a la mitad
    elif resistance_change < resistance_threshold / 2 and step < initial_step:
        step *= 2  # Incrementa el paso si el cambio es pequeño

    previous_resistance = resistance  # Actualiza la resistencia anterior
    print(f"Corriente: {current:.8f} A, V_xx: {voltage:.8f} V, Rxx: {resistance:.8f} ohm, Paso: {step:.6e} A, V_Hall: {voltage3458:.8f} V, Rhall: {resistance_hall:.8f} ohm")

    with open(file_path, 'a') as f:
        np.savetxt(f, np.column_stack((current, voltage, resistance, voltage3458, resistance_hall)), delimiter=";")



# Apaga la salida y cierra las conexiones
fuente.output_off()
fuente.close()
m.close()
mh.close()
print('Closed instruments')

# Finaliza la gráfica interactiva
plt.ioff()  # Deshabilita el modo interactivo
plt.draw()  # Asegúrate de que la gráfica se actualice completamente
plt.show()  # Muestra la gráfica final y espera a que el usuario la cierre

print('Fin del script, termina cuando usted cirres el gráfico.')
