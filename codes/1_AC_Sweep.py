# -*- coding: utf-8 -*-
"""
Created on Mon Jun  6 15:19:30 2022

@author: nutchanonj
"""

# import PyLTSpice
from PyLTSpice.LTSpiceBatch import SimCommander
from PyLTSpice import LTSpice_RawRead

# import math function
from math import log10
from math import pi
from cmath import phase

# import
import numpy as np
from matplotlib import pyplot as plt

import time

# function to change complex number to abs
def to_dB(x):
    return 20*log10(abs(x))

# function to change complex number to phase
def to_degree(x):
    out = phase(x)/pi*180
    if 0 < out < 180:
        out = out - 360
    return out

# function to receive raw data and generate result
def run_result(exp_name):
    
    # read data from raw file
    LTR = LTSpice_RawRead.RawRead(f"{exp_name}.raw")
    print("Read Success")
    freq = np.array(LTR.get_trace('frequency'), dtype=np.longdouble)
    vout = np.array(LTR.get_trace('V(vout)'), dtype=np.clongdouble)
    vout_abs = np.fromiter(map(lambda x: to_dB(x), vout), dtype=np.longdouble)
    vout_phase = np.fromiter(map(lambda x: to_degree(x), vout), dtype=np.longdouble)
    
    # # plot the result
    # figure = plt.figure()
    # ax = figure.add_subplot(111)
    # plt.xscale("log")
    # ax.plot(freq, vout_abs)
    # figure.savefig(f'{exp_name}.png', dpi=300)
    
    # find dc gain
    dc_gain = vout_abs[0]
    
    # find crossover frequency and phase margin
    zero_crossing = int(np.where(np.diff(np.sign(vout_abs)))[0])
    cross_freq = freq[zero_crossing]/1000000 # unit in MHz
    phase_margin = vout_phase[zero_crossing] + 180
    
    return dc_gain, cross_freq, phase_margin

# export result
def export_result(export_name, dc_gain_data, cross_freq_data, phase_margin_data, rows, columns):
    # export dc gain
    dc_gain_exp = np.reshape(dc_gain_data, (rows, columns))
    np.savetxt(f"{export_name}_dc_gain.csv", dc_gain_exp, delimiter=",", fmt='%.2f')
    # export crossover freq
    cross_freq_exp = np.reshape(cross_freq_data, (rows, columns))
    np.savetxt(f"{export_name}_cross_freq.csv", cross_freq_exp, delimiter=",", fmt='%.2f')
    # export phase margin
    phase_margin_exp = np.reshape(phase_margin_data, (rows, columns))
    np.savetxt(f"{export_name}_phase_margin.csv", phase_margin_exp, delimiter=",", fmt='%.2f')
    
    
# params
corners = ["SS","TT","FF"]
temps = [0,35,70]

LTC = SimCommander("SIM_ac_sweep.asc", parallel_sims=8)

dc_gain_data = []
cross_freq_data = []
phase_margin_data = []

for corner in corners:
    # run the simulation    
    LTC.add_instruction(f".include cmos018_{corner}.lib")
    
    # change the power supply to 1.1 V
    Vsupply = 1.1
    LTC.set_component_value('Vsupply', Vsupply)
    
    for Vin in [0.1, 0.3, 0.5, 0.7, 0.9]:
        LTC.set_component_value('Vsource', Vin)
        LTC.set_component_value('Voffset', 0)
        for temp in temps:
            LTC.add_instruction(f".temp {temp}")
            exp_name = f"SIM_ac_sweep_Vin_{corner}_{Vsupply:.1f}_{Vin:.1f}_{temp:.1f}"
            LTC.run(run_filename=f"{exp_name}.net")
            LTC.remove_instruction(f".temp {temp}")
    
    for Voffset in [-0.45, 0, 0.45]:
        Vin = 0.55
        Vout = Vin + Voffset 
        LTC.set_component_value('Vsource', Vin)
        LTC.set_component_value('Voffset', Voffset)
        for temp in temps:
            LTC.add_instruction(f".temp {temp}")
            exp_name = f"SIM_ac_sweep_Vout_{corner}_{Vsupply:.1f}_{Vout:.1f}_{temp:.1f}"
            LTC.run(run_filename=f"{exp_name}.net")
            LTC.remove_instruction(f".temp {temp}")
            
    # change the power supply to 1.8 V
    Vsupply = 1.8
    LTC.set_component_value('Vsupply', Vsupply)
    
    for Vin in [0.1, 0.4, 0.7, 1.0, 1.3, 1.6]:
        LTC.set_component_value('Vsource', Vin)
        LTC.set_component_value('Voffset', 0)
        for temp in temps:
            LTC.add_instruction(f".temp {temp}")
            exp_name = f"SIM_ac_sweep_Vin_{corner}_{Vsupply:.1f}_{Vin:.1f}_{temp:.1f}"
            LTC.run(run_filename=f"{exp_name}.net")
            LTC.remove_instruction(f".temp {temp}")
    
    for Voffset in [-0.8, -0.4, 0, 0.4, 0.8]:
        Vin = 0.9
        Vout = Vin + Voffset
        LTC.set_component_value('Vsource', Vin)
        LTC.set_component_value('Voffset', Voffset)
        for temp in temps:
            LTC.add_instruction(f".temp {temp}")
            exp_name = f"SIM_ac_sweep_Vout_{corner}_{Vsupply:.1f}_{Vout:.1f}_{temp:.1f}"
            LTC.run(run_filename=f"{exp_name}.net")
            LTC.remove_instruction(f".temp {temp}")
    
    # remove old instruction
    LTC.remove_instruction(f".include cmos018_{corner}.lib")

LTC.wait_completion()

for corner in corners:
    
    # change the power supply to 1.1 V
    Vsupply = 1.1
    for Vin in [0.1, 0.3, 0.5, 0.7, 0.9]:
        for temp in temps:
            exp_name = f"SIM_ac_sweep_Vin_{corner}_{Vsupply:.1f}_{Vin:.1f}_{temp:.1f}"
            dc_gain, cross_freq, phase_margin = run_result(exp_name)
            dc_gain_data.append(dc_gain)
            cross_freq_data.append(cross_freq)
            phase_margin_data.append(phase_margin)
        
    rows = 5;
    columns = 3;
    export_name = f"SIM_ac_sweep_Vin_{corner}_{Vsupply:.1f}"
    export_result(export_name, dc_gain_data, cross_freq_data, phase_margin_data, rows, columns)
    dc_gain_data = []; cross_freq_data = []; phase_margin_data = [];
    
    for Voffset in [-0.45, 0, 0.45]:
        Vin = 0.55
        Vout = Vin + Voffset 
        for temp in temps:
            exp_name = f"SIM_ac_sweep_Vout_{corner}_{Vsupply:.1f}_{Vout:.1f}_{temp:.1f}"
            dc_gain, cross_freq, phase_margin = run_result(exp_name)
            dc_gain_data.append(dc_gain)
            cross_freq_data.append(cross_freq)
            phase_margin_data.append(phase_margin)
    
    rows = 3;
    columns = 3;
    export_name = f"SIM_ac_sweep_Vout_{corner}_{Vsupply:.1f}"
    export_result(export_name, dc_gain_data, cross_freq_data, phase_margin_data, rows, columns)
    dc_gain_data = []; cross_freq_data = []; phase_margin_data = [];
    
    # change the power supply to 1.8 V
    Vsupply = 1.8
    LTC.set_component_value('Vsupply', Vsupply)
    
    for Vin in [0.1, 0.4, 0.7, 1.0, 1.3, 1.6]:
        for temp in temps:
            exp_name = f"SIM_ac_sweep_Vin_{corner}_{Vsupply:.1f}_{Vin:.1f}_{temp:.1f}"
            dc_gain, cross_freq, phase_margin = run_result(exp_name)
            dc_gain_data.append(dc_gain)
            cross_freq_data.append(cross_freq)
            phase_margin_data.append(phase_margin)
    
    rows = 6;
    columns = 3;
    export_name = f"SIM_ac_sweep_Vin_{corner}_{Vsupply:.1f}"
    export_result(export_name, dc_gain_data, cross_freq_data, phase_margin_data, rows, columns)
    dc_gain_data = []; cross_freq_data = []; phase_margin_data = [];
    
    for Voffset in [-0.8, -0.4, 0, 0.4, 0.8]:
        Vin = 0.9
        Vout = Vin + Voffset
        for temp in temps:
            exp_name = f"SIM_ac_sweep_Vout_{corner}_{Vsupply:.1f}_{Vout:.1f}_{temp:.1f}"
            dc_gain, cross_freq, phase_margin = run_result(exp_name)
            dc_gain_data.append(dc_gain)
            cross_freq_data.append(cross_freq)
            phase_margin_data.append(phase_margin)
    
    rows = 5;
    columns = 3;
    export_name = f"SIM_ac_sweep_Vout_{corner}_{Vsupply:.1f}"
    export_result(export_name, dc_gain_data, cross_freq_data, phase_margin_data, rows, columns)
    dc_gain_data = []; cross_freq_data = []; phase_margin_data = [];
    
    
    





    
    
    
    






