# import PyLTSpice
from PyLTSpice.LTSpiceBatch import SimCommander
from PyLTSpice import LTSpice_RawRead

import pandas as pd
import numpy as np

corners = ["SS","TT","FF"]
temps = [0,35,70]
Vsupply_list = [1.8, 1.1]

LTC = SimCommander("SIM_transient.asc")

# array to store data
transient_data = []

for corner in corners:
    LTC.add_instruction(f".include cmos018_{corner}.lib")

    # change the power supply to 1.1 V
    for Vsupply in Vsupply_list:
        LTC.set_component_value('Vsupply', Vsupply)
        
        for temp in temps:
            LTC.add_instruction(f".temp {temp}")
            exp_name = f"SIM_transient_{corner}_{Vsupply:.1f}_{temp:.1f}"
            LTC.run(run_filename=f"{exp_name}.net")
            LTC.wait_completion()
            LTR = LTSpice_RawRead.RawRead(f"{exp_name}.raw")
            print("Read Success")
            
            # read time data. (I don't know why time from raw file is sometimes negative, so abs is needed.)
            time = np.abs(np.array(LTR.get_trace('time'), dtype=np.longdouble))# I don't 
            # read magnitude data.
            mag = np.array(LTR.get_trace('V(vout)'), dtype=np.longdouble)
            # data to export.
            settling = []
            
            zero_crossings = np.where(np.diff(np.sign(mag - 0.505))) 
            # Step value is 0.5 V. Wait until the signal drops to within 1%.
            
            transient_data.append((time[zero_crossings[0][1]] - 2e-6)/1e-6)
            # The start time is at 2us. the time unit exported is microsec.
            
            LTC.remove_instruction(f".temp {temp}")
    
    # remove old instruction
    LTC.remove_instruction(f".include cmos018_{corner}.lib")

rows = 3;
columns = 6;

transient_data = np.reshape(transient_data, (rows, columns)).T
np.savetxt("SIM_transient.csv", transient_data, delimiter=",", fmt='%.3f')
    
    

    