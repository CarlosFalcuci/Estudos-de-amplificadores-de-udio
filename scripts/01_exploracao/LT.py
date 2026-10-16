from PyLTSpice import SimRunner,RawRead,SpiceEditor,LTSpiceLogReader
import numpy as np
import matplotlib.pyplot as plt

lts=r"C:\Users\Carlos Eduardo\AppData\Local\Programs\ADI\LTspice\LTspice.exe"
netlist_path = SimRunner(output_folder='./teste_py_lt',simulator=lts)

asc = r"C:\Users\Carlos Eduardo\Documents\LTspice\teste_py.asc"
net_editor=SpiceEditor(asc)
net_editor.set_component_value("R14","1000")
net_editor.set_component_value("V3","SINE(0 .7 1K)")
net_editor.add_instruction(".ac dec 50 0.1 10Meg")
net_editor.add_instruction(".meas ac GMAX max mag(V(A))")
net_editor.add_instruction(".meas ac FC when mag(V(A))=GMAX/sqrt(2)")

raw_ac, log_ac =netlist_path.run_now(net_editor)
curvas = RawRead(raw_ac)
vout=curvas.get_trace("V(a)")
v=vout.get_wave()
frequencia=curvas.get_axis()

voutdb= 20* np.log10(np.abs(v))

#plt.semilogx(frequencia,voutdb)
#plt.show()

#Simulacao DC, é necessário remover as intrucoes passadas anteriormente

net_editor.remove_instruction(".ac dec 50 0.1 10Meg")
net_editor.remove_instruction(".meas ac GMAX max mag(V(A))")
net_editor.remove_instruction(".meas ac FC when mag(V(A))=GMAX/sqrt(2)")

net_editor_cc=SpiceEditor(asc)

net_editor_cc.add_instruction(".tran 10m")
net_editor_cc.add_instruction(".four 1K V(A)")


raw_cc, log_cc=netlist_path.run_now(net_editor_cc)
print(log_ac)
log = LTSpiceLogReader(log_ac)
print(log.get_measure_names())
print("fc:",log.get_measure_value("fc_at"))
fcorte=log.get_measure_value("fc_at")

log = LTSpiceLogReader(log_cc)
print(log.fourier["V(A)"][0].thd)

net_editor_cc_slew=SpiceEditor(asc)
net_editor_cc_slew.set_component_value("V3","PULSE(0 5 0 1n 1n 1u 2u)")
net_editor_cc_slew.add_instruction(".meas tran SR_MAX MAX ddt(V(a))")
net_editor_cc_slew.add_instruction(".tran 1u")
raw_cc_slew, log_cc_slew=netlist_path.run_now(net_editor_cc_slew)
log = LTSpiceLogReader(log_cc_slew)

curvas_sr=RawRead(raw_cc_slew)
voutsr=curvas_sr.get_trace("V(a)")
Vmax=max(voutsr)
Vmin=min(voutsr)
Sr=Vmax-Vmin
print(Sr)
#print(log.get_measure_value("sr_max_to"))
#simulacao mt lenta!