# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 09:05:10 2025

@author: M.A. Real basado en prog Lean y Cia.
"""

## =========      AMETEK 7124 functions ==================================== ##  
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

