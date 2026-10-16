#Otimização da distorção harmônica 1° Estágio.

from PyLTSpice import SimRunner, SpiceEditor, RawRead
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from matplotlib.ticker import AutoMinorLocator


ltspice_exe_path = r"C:\Users\Carlos Eduardo\AppData\Local\Programs\ADI\LTspice\LTspice.exe"
runner = SimRunner(output_folder='./THD', simulator=ltspice_exe_path)

netlist_path = "1E.asc"

netlist_path_thd = "1E_thd.asc"



corrente_Is = np.arange(1e-3, 10e-3 + 0.5e-3, 0.5e-3)

#target_gains= [2,3,6,8,10,15,20]
target_gains= [2,3,6,8,10,15,20]

V_pol_RC = 5

RG= 54.9E3

resultados_THD = []
for Av_target in target_gains:
    for Is in corrente_Is:
        Ic = Is/2
        R_calc = V_pol_RC / Ic
        re = 26e-3/Ic
        Freq = 1E3

        #Simulção preliminar para determinar bheta

        RE_guess = (R_calc / (2 * Av_target)) - re - (RG / (2 * 550))

        if RE_guess <= 0:
            RE_guess = 50.0
        
        net_pre = SpiceEditor(netlist_path)

        net_pre.set_component_value("I1",f"{Is}")
        net_pre.set_component_value("R1", str(R_calc))
        net_pre.set_component_value("R2", str(R_calc))
        net_pre.set_component_value("R3",str(RE_guess))
        net_pre.set_component_value("R4", str(RE_guess))
        net_pre.set_component_value("R5", str(RG))
        net_pre.set_component_value("RG1", str(RG))
        net_pre.add_instruction(".op")

        #rodar simulação 

        raw_path, log_path = runner.run_now(net_pre)
        LTR = RawRead(raw_path)

        ib = abs(LTR.get_trace("ib(Q1)").get_wave(0)[0])
        ic= abs(LTR.get_trace("I(R1)").get_wave(0)[0])
        bheta = ic/ib if ib !=0 else 550

        # COM BHETA REAL

        RE_calc = (R_calc / (2 * Av_target)) - re - (RG / (2 * bheta))
        
        if RE_calc <=0:
            continue

        net_thd = SpiceEditor(netlist_path_thd)

        net_thd.set_component_value("I1",f"{Is}")
        net_thd.set_component_value("R1", str(R_calc))
        net_thd.set_component_value("R2", str(R_calc))
        net_thd.set_component_value("R3",str(RE_calc))
        net_thd.set_component_value("R4", str(RE_calc))
        net_thd.set_component_value("R5", str(RG))
        net_thd.set_component_value("RG1", str(RG))
        

        #PARAMETROS PARA SIMULAÇÃO DE THD 
        
        Freq = 1e3
        numcyc= 1000
        FFT= 655360
        dlycyc = 0
        simtime = (dlycyc+numcyc)/Freq
        dlytime = dlycyc/Freq
        numsampl = simtime / Freq / ((simtime / numcyc) * FFT)


        net_thd.set_element_model("V3",f"SINE(0 10m {Freq})")
        net_thd.add_instruction(".options plotwinsize=0")   
        net_thd.add_instruction(".options numdgt=7")
      

        net_thd.add_instruction(f".four {Freq} V(OUT)")
        net_thd.add_instruction(f".tran 0 {simtime} {dlytime} {numsampl}")

        raw_ac, log_ac = runner.run_now(net_thd)

        with open(log_ac, "r", encoding="utf-8", errors="ignore") as f:
            log = f.read()
            for linha in log.splitlines():
                if "Total Harmonic Distortion" in linha:
                    thd_string = linha.split(":")[1].strip()
                    thd = float(thd_string.split("%")[0])
    
            
        resultados_THD.append((Av_target,Is*1e3,thd))  

        print(
            f"Is={Is*1e3:.2f}mA | RC={R_calc:.1f}Ω | RE={RE_calc:.1f}Ω | Av ={Av_target}-> "
            f"THD={thd}% | "
        )


 #_____________________PLOTAGEM ______________________#
 
plt.figure(figsize=(8, 5))

curvas = {}

for Av, Is_ma, thd in resultados_THD:
    curvas.setdefault(Is_ma,{"Av":[], "thd":[]})
    curvas[Is_ma]["Av"].append(Av)
    curvas[Is_ma]["thd"].append(thd)


for Is_ma in curvas:
    plt.plot(curvas[Is_ma]["Av"], curvas[Is_ma]["thd"],
             linewidth=2, marker='.', label=f"Is={Is_ma}")
    
plt.title("THD vs AV")
plt.xlabel("AV (Ganho)")
#plt.xlim (0,10)
plt.ylabel("THD (%)")
#plt.ylim(100,1600)
#subdivsões
ax = plt.gca()
ax.xaxis.set_minor_locator(AutoMinorLocator(4))  
ax.yaxis.set_minor_locator(AutoMinorLocator(2))
ax.grid(True, which='major', linestyle='-', linewidth=1.0, alpha=1)
ax.grid(True, which='minor', linestyle='--', linewidth=0.5, alpha=0.5)


plt.legend()
plt.tight_layout()

plt.show()


        
            
        