# -*- coding: utf-8 -*-
"""
Created on Mon Jun  6 15:19:30 2022

@author: nutchanonj
"""
import re

# import PyLTSpice
from PyLTSpice.LTSpiceBatch import SimCommander
from PyLTSpice import LTSpice_RawRead

# import numpy
import numpy as np

LTC = SimCommander("SIM_noise.asc")

# params
corners = ["SS", "TT", "FF"]
temps = [0,35,70]

# array to store data
noise_data = []

for corner in corners:   
    LTC.add_instruction(f".include cmos018_{corner}.lib")
    
    for Vsupply in [1.8, 1.1]:
        LTC.set_component_value('Vsupply', Vsupply)
    
        for temp in temps:
            exp_name = "SIM_noise"
            
            LTC.add_instruction(f".temp {temp}")
            LTC.run(run_filename=f"{exp_name}.net")
            LTC.wait_completion()
            
            file = open(f'{exp_name}.log', 'r')
            Lines = file.readlines()
            
            for line in Lines:
                if (line.find('noiserms:') != -1):
                    noise_data.append( float(re.findall(r"[-+]?(?:\d*\.\d+|\d+)", line)[0]) * 1000000 )
            
            LTC.remove_instruction(f".temp {temp}")
    
    # remove old instruction
    LTC.remove_instruction(f".include cmos018_{corner}.lib")

rows = 3;
columns = 6;

noise_data = np.reshape(noise_data, (rows, columns)).T
np.savetxt("SIM_noise.csv", noise_data, delimiter=",", fmt='%.2f')



