# Programa de adquisición de datos de un termohigrómetro con interfaz gráfica
# Autor: Juan Pablo Catolino
# Fecha: 2024/04
#

# Importing necessary libraries for GUI, serial communication, time, data manipulation and date/time
from tkinter import*
from tkinter import messagebox, filedialog, ttk
import serial, time
#import io
import pandas as pd
import datetime


# Initializing lists to store data
Hora=[]
Fecha=[]
num_med = []
temperatura=[]
humedad=[]
presion=[]

# Defining column names for the data frame
col1="Numero de mediciones" #Doy nombre a las columnas de la tabla data frame
col2="Temperatura"
col3="Humedad"
col4="Presión"
col5="Fecha"
col6="Hora"

# mira hora actual y genera nombre de archivo
now = datetime.datetime.now()


# Creating a root window
raiz=Tk()


# Creating a menu bar
barraMenu=Menu(raiz)
# Configuring the root window with the menu bar and dimensions
raiz.config(menu=barraMenu, width=1200, height=600)
# Creating a frame to place the widgets
miFrame=Frame(raiz, width=300, height=600)
miFrame.pack()


raiz.title("Medidor de condiciones ambientales")

# call relative path to an icon.ico to include in the front end
# raiz.iconbitmap("termohigrometro JPC\Icon.ico")



# Creating a combobox to select the COM port
seleccionarCOM=ttk.Combobox(miFrame, values=['COM1','COM2','COM3','COM4','COM5','COM6','COM7','COM8','COM9','COM10'])
seleccionarCOM.grid(row=1, column=1)
SeleccionarLabel=Label(miFrame, text="Seleccionar puerto:")
SeleccionarLabel.grid(row=1, column=0, sticky="e", padx=10, pady=10)



# Creating a menu bar with different options
archivoMenu=Menu(barraMenu, tearoff=0)
archivoMenu.add_command(label="Nuevo")
archivoMenu.add_command(label="Guardar")
archivoMenu.add_command(label="Guardar como")
archivoMenu.add_separator()
archivoMenu.add_command(label="Cerrar")
archivoMenu.add_command(label="Salir")

archivoEdicion=Menu(barraMenu)
archivoEdicion=Menu(barraMenu, tearoff=0)
archivoEdicion.add_command(label="Copiar")
archivoEdicion.add_command(label="Cortar")
archivoEdicion.add_command(label="Pegar")

archivoHerramientas=Menu(barraMenu)
archivoHerramientas=Menu(barraMenu, tearoff=0)

archivoAyuda=Menu(barraMenu)
archivoAyuda=Menu(barraMenu, tearoff=0)
archivoAyuda.add_command(label="Licencia")
archivoAyuda.add_command(label="Acerca de...")

barraMenu.add_cascade(label="Archivo", menu=archivoMenu)
barraMenu.add_cascade(label="Edición", menu=archivoEdicion)
barraMenu.add_cascade(label="Herramientas", menu=archivoHerramientas)
barraMenu.add_cascade(label="Ayuda", menu=archivoAyuda)


# Creating labels and entry widgets to display the temperature, humidity, pressure, time between measurements and number of measurements
Temperatura=StringVar()
Humedad=StringVar()
Presion=StringVar()
Tiemposentremeds=StringVar()
cantidadMeds=StringVar()
Conexionexitosa=StringVar()

cuadroTemperatura=Entry(miFrame, textvariable=Temperatura)
cuadroTemperatura.grid(row=3, column=1, padx=10, pady=10)
cuadroTemperatura.config(fg="black", justify="center")
TemperaturaLabel=Label(miFrame, text="Temperatura [°C]:")
TemperaturaLabel.grid(row=3, column=0, sticky="e", padx=10, pady=10)

cuadroHumedad=Entry(miFrame, textvariable=Humedad)
cuadroHumedad.grid(row=3, column=3, padx=10, pady=10)
cuadroHumedad.config(fg="black", justify="center")
HumedadLabel=Label(miFrame, text="Humedad [% Hr]:")
HumedadLabel.grid(row=3, column=2, sticky="e", padx=10, pady=10)

cuadroPresion=Entry(miFrame, textvariable=Presion)
cuadroPresion.grid(row=3, column=5, padx=10, pady=10)
cuadroPresion.config(fg="black", justify="center")
PresionLabel=Label(miFrame, text="Presion [hPa]:")
PresionLabel.grid(row=3, column=4, sticky="e", padx=10, pady=10)

cuadroTiempos=Entry(miFrame, textvariable=Tiemposentremeds)
cuadroTiempos.grid(row=2, column=1, padx=10, pady=10)
cuadroTiempos.config(fg="black", justify="center")
HumedadTiempos=Label(miFrame, text="Tiempos entre mediciones [s]:")
HumedadTiempos.grid(row=2, column=0, sticky="e", padx=10, pady=10)

cuadroMeds=Entry(miFrame, textvariable=cantidadMeds)
cuadroMeds.grid(row=2, column=3, padx=10, pady=10)
cuadroMeds.config(fg="black", justify="center")
cantidadMeds=Label(miFrame, text="Cantidad de mediciones:")
cantidadMeds.grid(row=2, column=2, sticky="e", padx=10, pady=10)



# Defining a function to measure the temperature, humidity and pressure
def Medir():
	
	selected_option = seleccionarCOM.get()

	try:
		arduino = serial.Serial(selected_option, 115200,timeout=1)
		arduino.flush()
		time.sleep(1)
		Conexionexitosa="Conexión Exitosa!"
		print(Conexionexitosa)

		if not cuadroMeds.get():
			N=1
		else:
			N=int(cuadroMeds.get())	
		if not cuadroTiempos.get():
			A=2
		else:
			A=float(cuadroTiempos.get())
	
		file_path = filedialog.asksaveasfilename(defaultextension='.xlsx')


		for x in range(N):
			
			time.sleep(A)
			commandT='T?'+ str('\r\n')
			arduino.write(commandT.encode())
			line = arduino.readline()
			Tstring = line.decode().strip()				
			T=float(Tstring)
			Temperatura.set(T)
			commandH='H?'+ str('\r\n')
			arduino.write(commandH.encode())
			line = arduino.readline()
			Hstring = line.decode().strip()
			H=float(Hstring)
			Humedad.set(H)
			commandP='P?'+ str('\r\n')
			arduino.write(commandP.encode())
			line = arduino.readline()
			Pstring = line.decode().strip()
			P=float(Pstring)
			Presion.set(P)
			temperatura.append(T) # Tomo un valor de temperatura
			humedad.append(H)
			presion.append(P)
			Hora.append(datetime.datetime.now().strftime('%H:%M:%S'))
			Fecha.append(datetime.datetime.now().strftime('%d-%m-%Y'))
			num_med.append(x+1)
			print(temperatura)
			print(humedad)
			print(presion)
		
			df_medicion=pd.DataFrame({col1:num_med,col2:temperatura,col3:humedad,col4:presion,col5:Fecha,col6:Hora}) #creo data frame
	        
			df_medicion.to_excel(file_path, sheet_name= 'Valores medidos', index=False) #guarda data frame en excel

		# display a message box to inform the user that the data was saved and the measurement finished
		messagebox.showinfo(message="Datos guardados exitosamente", title="Medición finalizada")
  
		arduino.close()

		
	except serial.SerialException:
		messagebox.showwarning(message="Error en la conexión, cambie de COM", title="Error en la conexión")
		print("Error opening {}. Make sure the device is connected.".format(selected_option))
	

# Creating a button to measure the temperature, humidity and pressure
botonMedir=Button(miFrame, text="Medir", command=Medir)
botonMedir.grid(row=6, column=1, padx=10, pady=10)


raiz.mainloop()




if __name__ == "__main__":
    root = tk.Tk()
    app = SerialPortApp(root)
    raiz.mainloop()
