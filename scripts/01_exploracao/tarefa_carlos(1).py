from PyLTSpice import SimRunner, SpiceEditor, LTSpiceLogReader
import numpy as np
import matplotlib.pyplot as plt

lts = r"C:\Users\Carlos Eduardo\AppData\Local\Programs\ADI\LTspice\LTspice.exe"
runner = SimRunner(output_folder='./teste_py_lt', simulator=lts)

asc = r"C:\Users\Carlos Eduardo\Documents\LTspice\pestagio.asc"

# =========================
# BLOCO 1 - fh vs corrente
# =========================
Is=[0.0004,0.004,0.01]
net_editor_ac = SpiceEditor(asc)
Re1=np.linspace(3200,6800,50)
y1=[]
x1=[]
net_editor_ac.set_component_value("I1", 0.0004)
Rx=20/(0.0004/2)
net_editor_ac.set_component_value("Rd1e", str(Rx))
net_editor_ac.set_component_value("Rd1d", str(Rx))

for val in Re1:
    net_editor_ac.set_component_value("Rs1e", str(val))
    net_editor_ac.set_component_value("Rs1d", str(val))

    raw, log = runner.run_now(net_editor_ac)
    log = LTSpiceLogReader(log)

    y1.append(log.fourier["V(vout)"][0].thd)
    vpp = float(log.dataset["vpp"][0])
    av = vpp / 2
    x1.append(av)

plt.figure(figsize=(8, 5))
plt.plot(x1, y1, marker='o', linestyle='-')

plt.title("THD vs AV")
plt.xlabel("AV = Vpp/2")
plt.ylabel("THD (%)")
plt.grid(True)
plt.tight_layout()
plt.show()

# =========================
# BLOCO 2 - THD vs AV (I = 0.004 A)
# =========================
net_editor_ac = SpiceEditor(asc)

Re2 = np.linspace(300, 700, 50)  # <-- novos valores de Re (ajuste como quiser)
y2 = []
x2 = []

net_editor_ac.set_component_value("I1", 0.004)

Rx = 20 / (0.004 / 2)
net_editor_ac.set_component_value("Rd1e", str(Rx))
net_editor_ac.set_component_value("Rd1d", str(Rx))

for val in Re2:
    net_editor_ac.set_component_value("Rs1e", str(val))
    net_editor_ac.set_component_value("Rs1d", str(val))

    raw, log = runner.run_now(net_editor_ac)
    log = LTSpiceLogReader(log)

    y2.append(log.fourier["V(vout)"][0].thd)

    vpp = float(log.dataset["vpp"][0])
    av = vpp / 2
    x2.append(av)

# plot separado
plt.figure(figsize=(8, 5))
plt.plot(x2, y2, marker='o', linestyle='-')

plt.title("THD vs AV (I = 4 mA)")
plt.xlabel("AV = Vpp/2")
plt.ylabel("THD (%)")
plt.grid(True)
plt.tight_layout()
plt.show()

# =========================
# BLOCO 3 - THD vs AV (I = 0.01 A)
# =========================
net_editor_ac = SpiceEditor(asc)

Re3 = np.linspace(110, 260, 50)  # <-- ajuste esse range conforme fizer sentido
y3 = []
x3 = []

net_editor_ac.set_component_value("I1", 0.01)

Rx = 20 / (0.01 / 2)
net_editor_ac.set_component_value("Rd1e", str(Rx))
net_editor_ac.set_component_value("Rd1d", str(Rx))

for val in Re3:
    net_editor_ac.set_component_value("Rs1e", str(val))
    net_editor_ac.set_component_value("Rs1d", str(val))

    raw, log = runner.run_now(net_editor_ac)
    log = LTSpiceLogReader(log)

    y3.append(log.fourier["V(vout)"][0].thd)

    vpp = float(log.dataset["vpp"][0])
    av = vpp / 2
    x3.append(av)

# plot separado
plt.figure(figsize=(8, 5))
plt.plot(x3, y3, marker='o', linestyle='-')

plt.title("THD vs AV (I = 10 mA)")
plt.xlabel("AV = Vpp/2")
plt.ylabel("THD (%)")
plt.grid(True)
plt.tight_layout()
plt.show()

plt.figure(figsize=(8, 5))

# curva 1
plt.plot(x1, y1, marker='o', linestyle='-', label='I = 0.4 mA')

# curva 2
plt.plot(x2, y2, marker='s', linestyle='-', label='I = 4 mA')

# curva 3
plt.plot(x3, y3, marker='^', linestyle='-', label='I = 10 mA')

plt.title("THD vs AV (Comparação)")
plt.xlabel("AV = Vpp/2")
plt.ylabel("THD (%)")

plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()