# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 09:05:10 2025

@author: M.A. Real basado en prog Lean y Cia.
"""

def outputs(lockin, str_term = 'EOI'):   
    """
    Queries the Signal Recovery 7280 lock-in amplifier for the X and Y signal magnitudes and prints them.
    Parameters:
    lockin (object): The lock-in amplifier object to query.
    str_term (str, optional): The termination string for the query. Defaults to 'EOI'.
    Returns:
    tuple: A tuple containing the X and Y signal magnitudes as strings.
    """
    lia1x = float(lockin.query('X. ' + str_term))     # Returns signal magnitude singal
    lia1y = float(lockin.query('Y. ' + str_term))     # Returns signal magnitude singal
    print(lia1x)
    print(lia1y)
    return lia1x, lia1y