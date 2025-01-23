import time

# Usage example
# if __name__ == "__main__":
#     import pyvisa

#     # Initialize the lockin instrument (mocked for demonstration)
#     rm = pyvisa.ResourceManager()
#     lockin = rm.open_resource('GPIB0::8::INSTR')

#     # Create an instance of the SR830 class
#     sr830 = SR830(lockin)

#     # Automatically adjust the sensitivity
#     sr830.auto_scale()

class SR830:
    
    def __init__(self, lockin):
        self.lockin = lockin
        
    def flush_buffer(self):
        '''
        Flush the communication buffer, otherwise the commands do not work properly
        It must be added to every function
        Returns:  None.
        '''
        self.lockin.clear()
        time.sleep(0.05)       
    
    def wait_bit1(self):
        ''' wait for the status bit 1 to be set '''
        while True:
            #status = int(self.lockin.query('LIAS?'))
            self.lockin.write('*STB?')
            status = int(self.lockin.read())
            print(status)     #lo saque para versi sin esto funciona: no tira errores
            if (status & 1): # ver si bit 1 set
                break
            time.sleep(0.1)
    
    def get_error_status_byte(self):
        '''ERR, returns: err status byte (int)'''
        self.flush_buffer()
        error_status = int(self.lockin.query('ERR?'))
        return error_status
    
    def get_event_status_byte(self):
        '''ESB, returns: event status byte (int)'''
        self.flush_buffer()
        event_status = int(self.lockin.query('ESB?'))
        return event_status
        
    def auto_scale(self):
        self.flush_buffer()
        self.lockin.write('AGAN')
        time.sleep(10)
        # No me esta funcionando, hay que ver porque
        # while True:
        #     status_byte = int(self.lockin.query('*STB?'))
        #     if status_byte & 0x10:  # check if the auto-gain bit (bit 1) is set
        #         break
        #     time.sleep(0.1)  # wait 100 ms before checking again
    
    def get_sensitivity(self):
        """
        Get the current sensitivity 
        Returns:
            int: the current sensitivity setting index
        """
        self.flush_buffer()
        sensitivity = int(self.lockin.query('SENS?'))
        return sensitivity
    
    def set_sensitivity(self, sensitivity):
        self.flush_buffer()
        self.lockin.write(f'SENS {sensitivity}')
        time.sleep(2)
        # No me esta funcionando, hay que ver porque
        # # wait for operaion to complete
        # while True:
        #     status_byte = int(self.lockin.query('*STB?'))
        #     if status_byte & 0x10:
        #         break
        #     time.sleep(0.1)
    
    def get_full_scale(self, sensitivity_index):
        # Full scale values for SR830 sensitivity settings
        full_scale_values = [
            2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9, 500e-9,
            1e-6, 2e-6, 5e-6, 10e-6, 20e-6, 50e-6, 100e-6, 200e-6,
            500e-6, 1e-3, 2e-3, 5e-3, 10e-3, 20e-3, 50e-3, 100e-3,
            200e-3, 500e-3, 1
        ]
        return full_scale_values[sensitivity_index]
    
    def get_mode(self):
        '''
        Get the current mode of the lockin amplifier.

        Returns
        -------
        int: The current mode (0:A, 1: A-B, 2: I1, 3: I2).
        '''
        self.flush_buffer()
        mode = int(float(self.lockin.query('ISRC?')))        
        return mode      
        
    def get_time_constant(self):
        """
        Get the current time constant
        Returns:
            int: the current time constant index
        """
        time_constant = int(self.lockin.query('OFLT?'))
        time.sleep(0.05)
        return time_constant
    
    def time_constant_value(self):
        self.flush_buffer()
        time_constant_values = [
            10E-6, 30E-6, 100E-6, 300E-6, 1E-3, 3E-3, 10E-3, 30E-3, 100E-3, 
            300E-3, 1,3,10,30,100, 300,1000,3000, 10000, 30000
            ]
        return time_constant_values[self.get_time_constant()]
    
    def set_time_constant(self, time_constant_index):
        '''
        Set the time constant of the lockin
        Parameters:
            time_constant_index (int):  the time constant setting index
        Returns:
            None
        '''
        self.flush_buffer()
        self.lockin.write(f'OFLT {time_constant_index}')
    
    def get_frequency(self):
        self.flush_buffer()
        freq = self.lockin.query('FREQ?')
        print(float(freq))
        return freq

    def set_frequency(self, freq):
        self.flush_buffer()
        self.lockin.write(f'FREQ {freq}')
        time.sleep(0.5)

    def set_amplitude(self, voltage):
        self.flush_buffer()
        self.lockin.write(f'SLVL {voltage}')
        time.sleep(1)

    def get_identity(self):
        self.flush_buffer()
        identity = self.lockin.query('*IDN?')
        #self.wait_bit1()
        # No me esta funcionando, hay que ver porque
        # while True:
        #     status_byte = int(self.lockin.query('*STB?'))
        #     print(status_byte) # SACAR LUEGO
        #     if status_byte & 0x10:  # check if the auto-gain bit (bit 1) is set
        #         break
        #     time.sleep(0.1)  # wait 100 ms before checking again
        print(identity)
        return identity

    def get_synchronous_filter(self):
        self.flush_buffer()
        sfilter = self.lockin.query('SYNC?')
        return sfilter
        
    def set_synchronous_filter(self, sync):
        self.flush_buffer()
        self.lockin.write(f'SYNC {sync}')
        
    def set_harmonic(self, harmonic):
        self.flush_buffer()
        self.lockin.write(f'HARM {harmonic}')
        print('Harmonic set to {}'.format(harmonic))
        
    def query_with_retry(self, command, retries=3, delay=1):
        """
        Query the lockin with retries in case of timeout errors.
        Parameters:
            command (str): the command to send 
            retries (int): nro retries
            delay (int): delay between retries
            
        Returns: (str): response of the lockin
        """
        for attempt in range(retries):
            try:
                self.flush_buffer()
                response = self.lockin.query(command)
                return response
            except Exception as e:
                if 'VI_ERROR_TMO' in str(e):
                    print(f'Timeout error on attempt {attempt+1}. Retrying...')
                    time.sleep(delay)
                else:
                    raise e
                    raise Exception(f"Failed to query '{command}' after {retries} attempts because timeout ")
       
        
    def read_x_output(self):
        self.flush_buffer()
        x = float(self.query_with_retry('OUTP? 1'))
        #y = float(self.lockin.query('OUTP? 1'))
        #self.wait_bit1()
        return x 
    
    def read_y_output(self):
        self.flush_buffer()
        y = float(self.query_with_retry('OUTP? 2'))
        #y = float(self.lockin.query('OUTP? 2'))
        #self.wait_bit1()
        return y 
    
    def read_x_y_output(self):
        x = self.read_x_output()
        y = self.read_y_output()
        print(float(x), float(y))
        return x, y

    def adjust_sensitivity(self,mode):
        '''
        Adjust the sensitivity of the lockin based on the current readings
    
        Parameters:
            x_value (float) : current x reading
            y_value (float) : current y reading
        Returns : None
        '''
        # levels for A and A-B measurements, multiply by 1E-6 or 1E-8 for current measurements
        #mode = self.get_mode()
        sensitivity_index = self.get_sensitivity()
        full_scale = self.get_full_scale(sensitivity_index)
        x = self.read_x_output()
        y = self.read_y_output()
        mode = int(float(mode))
        
        if mode == 2: # Current I1
            full_scale *= 1e-6
        elif mode == 3: # Current I2
            full_scale *= 1e-8
        
        ratio = (x**2 + y**2)**0.5 / full_scale
            
        if ratio > 0.9 and sensitivity_index < 26:
            self.set_sensitivity(sensitivity_index + 1 )
            time.sleep(7)
        elif ratio < 0.1 and sensitivity_index > 0:
            self.set_sensitivity(sensitivity_index - 1)
            time.sleep(7)