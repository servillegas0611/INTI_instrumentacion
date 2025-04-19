import pyvisa

class Multimeter3458A:
    def __init__(self, resource_name):
        self.resource_name = resource_name
        self.instrument = None

    def connect(self):
        rm = pyvisa.ResourceManager()
        self.instrument = rm.open_resource(self.resource_name)
        self.instrument.read_termination = '\n'
        self.instrument.write_termination = '\n'
        self.instrument.timeout = 5000
        print(f"Connected to Multimeter 3458A: {self.instrument.query('ID?')}")
        self.instrument.write("RESET")

    def configure_voltage_dc(self, NPLC=20):
        # Configure for DC voltage measurement, autoranging, 20 NPLC
        if self.instrument:
            self.instrument.write("FUNC VOLT:DC")
            self.instrument.write(f"NPLC {NPLC}")
            self.instrument.write("NDIG 8,;AZERO ON;MFORMAT DREAL;MEM LIFO;TRIG auto;")
        else:
            raise Exception("Multimeter 3458A is not connected.")

    def measure_voltage_dc(self):
        if self.instrument:
            return self.instrument.query('RMEM 1;')
        else:
            raise Exception("Multimeter 3458A is not connected.")
        
    def close(self):
        if self.instrument:
            self.instrument.close()
            print("Multimeter 3458A connection closed.")

class Multimeter34420A:
    def __init__(self, resource_name):
        self.resource_name = resource_name
        self.instrument = None

    def connect(self):
        rm = pyvisa.ResourceManager()
        self.instrument = rm.open_resource(self.resource_name)
        self.instrument.read_termination = '\n'
        self.instrument.write_termination = '\n'
        self.instrument.timeout = 5000  # Timeout de 5 segundos
        print(f"Connected to Multimeter: {self.instrument.query('*IDN?')}")

    def measure_voltage_dc(self):
        if self.instrument:
            return self.instrument.query("MEAS:VOLT:DC? AUTO,MIN,(@1)")
        else:
            raise Exception("Multimeter is not connected.")

    def close(self):
        if self.instrument:
            self.instrument.close()
            print("Multimeter connection closed.")

class PowerSupply:
    def __init__(self, resource_name):
        self.resource_name = resource_name
        self.instrument = None

    def connect(self):
        rm = pyvisa.ResourceManager()
        self.instrument = rm.open_resource(self.resource_name)
        print(f"Connected to Power Supply: {self.instrument.query('*IDN?')}")

    def set_voltage(self, voltage):
        if self.instrument:
            self.instrument.write(f"VOLT {voltage}")
        else:
            raise Exception("Power Supply is not connected.")

    def set_current(self, current):
        if self.instrument:
            self.instrument.write(f"CURR {current}")
        else:
            raise Exception("Power Supply is not connected.")

    def output_on(self):
        if self.instrument:
            self.instrument.write("OUTP ON")
        else:
            raise Exception("Power Supply is not connected.")

    def output_off(self):
        if self.instrument:
            self.instrument.write("OUTP OFF")
        else:
            raise Exception("Power Supply is not connected.")

    def set_triax_inner_shield(self, mode):
        """
        Configures the triax inner shield connection.
        :param mode: 'GUARD' or 'OLOW' (Output Low)
        """
        if self.instrument:
            if mode.upper() in ["GUARD", "OLOW"]:
                self.instrument.write(f"OUTP:ISHield {mode.upper()}")
                print(f"Triax inner shield set to {mode.upper()}.")
            else:
                raise ValueError("Invalid mode. Use 'GUARD' or 'OLOW'.")
        else:
            raise Exception("Power Supply is not connected.")

    def set_current_range(self, current_range):
        if self.instrument:
            self.instrument.write(f"SOUR:CURR:RANG {current_range}")
        else:
            raise Exception("Power Supply is not connected.")
    
    def set_current_range_auto(self):
        """
        Configura el rango de corriente en automático.
        Envía el comando correspondiente al instrumento.
        """
        self.instrument.write("CURR:RANG:AUTO ON")  # Comando SCPI para habilitar rango automático
        #print("Rango de corriente configurado en automático.")


    def close(self):
        if self.instrument:
            self.instrument.close()
            print("Power Supply connection closed.")
