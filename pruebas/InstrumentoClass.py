import visa

class GPIBInstrument:
  #  In a class, names with a leading underscore indicate to other programmers that the attribute or method is intended to be be used inside that class.
    def __init__(self, address):
        # Per convention, a single standalone underscore is sometimes used as a name to indicate that a variable is temporary or insignificant.
        rm = visa.ResourceManager()
        self.instrument = rm.open_resource(address)

    def read(self):
        return self.instrument.read()

    def write(self, command):
        self.instrument.write(command)
        # here command should be changed to get the proper response of the instrument.

    def clear(self):
        self.instrument.clear()

    def close(self):
        self.instrument.close()

        
# You can use the class like this:
# create an instance of the class with the GPIB address of the instrument
inst = GPIBInstrument("GPIB0::12::INSTR")
# write a command to the instrument
inst.write("*IDN?")
# read the response from the instrument
print(inst.read())
# clear the buffer
inst.clear()
# close the connection
inst.close()


