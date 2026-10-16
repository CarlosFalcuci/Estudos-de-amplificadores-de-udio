from PyLTSpice import SimRunner, SpiceEditor, LTSpiceLogReader
import numpy as np
import matplotlib.pyplot as plt

lts = r"C:\Users\Carlos Eduardo\AppData\Local\Programs\ADI\LTspice\LTspice.exe"
runner = SimRunner(output_folder='./teste_py_lt', simulator=lts)

asc = r"C:\Users\Carlos Eduardo\Documents\LTspice\pestagio.asc"

# =========================
# BLOCO 1 - fh vs corrente
# =========================
Is = np.linspace(0.0005, 0.01, 50)
net_editor_ac = SpiceEditor(asc)
yfh = []
xis = []

RD = [4100, 8200, 12000]

net_editor_ac.add_instruction(".meas ac GMAX max mag(V(vout))")
net_editor_ac.add_instruction(".meas ac FH when mag(V(vout))=GMAX/sqrt(2)")

for Rx in RD:
    yfh_curva = []
    xis_curva = []

    net_editor_ac.set_component_value("Rd1e", str(Rx))
    net_editor_ac.set_component_value("Rd1d", str(Rx))

    for val in Is:
        net_editor_ac.set_component_value("I1", str(val))

        # varredura inicial
        net_editor_ac.add_instruction(".ac dec 100 1 10Meg")

        raw, log = runner.run_now(net_editor_ac)
        log = LTSpiceLogReader(log)

        fh = float(log.dataset["fh_at"][0])
        print(fh)

        net_editor_ac.remove_instruction(".ac dec 100 1 10Meg")

        # refino da varredura
        sfh = str(fh - 2000)
        instruction = ".ac dec 100 1 " + sfh
        net_editor_ac.add_instruction(instruction)

        raw, log = runner.run_now(net_editor_ac)
        log = LTSpiceLogReader(log)

        fl = float(log.dataset["fh_at"][0])
        net_editor_ac.remove_instruction(instruction)

        fh_grafic = fh / 1000

        yfh_curva.append(fh_grafic)
        xis_curva.append(val * 1000)

    yfh.append(yfh_curva)
    xis.append(xis_curva)

cores = ['blue', 'red', 'green']
labels = ['Av = 5', 'Av = 10', 'Av = 16']

print(len(xis))   # agora deve dar 3

for i in range(len(xis)):
    plt.plot(
        xis[i],
        yfh[i],
        linestyle='-',
        linewidth=2,
        color=cores[i],
        label=labels[i]
    )

plt.title('Frequência de Corte vs Corrente da Fonte', fontsize=14)
plt.xlabel('Corrente da Fonte Is (mA)', fontsize=12)
plt.ylabel('Frequência de Corte fh (kHz)', fontsize=12)

ax = plt.gca()

xmin = min(min(x) for x in xis)
xmax = max(max(x) for x in xis)
ymin = min(min(y) for y in yfh)
ymax = max(max(y) for y in yfh)

ax.set_xlim(xmin, xmax)
ax.set_ylim(ymin, ymax + 50)

plt.minorticks_on()
plt.grid(True, which='major', linestyle='-', linewidth=0.7)
plt.grid(True, which='minor', linestyle=':', linewidth=0.5)

plt.legend()
plt.tight_layout()
plt.show()

dados = np.column_stack((xis, yfh))
np.savetxt(
    "dados_amplificador.csv",
    dados,
    delimiter=",",
    header="Is_mA,fh_Hz",
    comments=""
)

# =========================
# BLOCO 2 - THD vs ganho
# =========================

Isd = [0.008, 0.004, 0.012]
Rc = np.linspace(5000, 12000, 1)
net_editor_tran = SpiceEditor(asc)

gain = []
thd = []

net_editor_tran.add_instruction(".tran 100m")
net_editor_tran.add_instruction(".four 1K V(vout)")
net_editor_tran.add_instruction(".meas TRAN Vmax MAX V(vout)")
net_editor_tran.add_instruction(".meas TRAN Vmin MIN V(vout)")
net_editor_tran.add_instruction(".meas TRAN Vpp PARAM Vmax - Vmin")

cores = ['blue', 'red', 'green']
labels = ['I = 8 mA', 'I = 4 mA', 'I = 12 mA']
net_editor_tran.set_component_value("V6","SINE(0 1 1k)")
for j, I in enumerate(Isd):
    gain = []
    thd = []

    net_editor_tran.set_component_value("I1", str(I))

    for val in Rc:
        net_editor_tran.set_component_value("Rd1e", str(val))
        net_editor_tran.set_component_value("Rd1d", str(val))

        raw_cc, log_cc = runner.run_now(net_editor_tran)
        log = LTSpiceLogReader(log_cc)

        print(log.get_measure_names())

        vpp = float(log.dataset["vpp"][0])
        av = vpp / 2

        gain.append(av)
        thd.append(log.fourier["V(vout)"][0].thd)

        print(av)
        print(log.fourier["V(vout)"][0].thd)

    plt.plot(
        gain,
        thd,
        linestyle='-',
        linewidth=2,
        color=cores[j],
        label=labels[j]
    )

plt.title('THD vs Ganho', fontsize=14)
plt.xlabel('Ganho', fontsize=12)
plt.ylabel('THD', fontsize=12)

plt.minorticks_on()
plt.grid(True, which='major', linestyle='-', linewidth=0.7)
plt.grid(True, which='minor', linestyle=':', linewidth=0.5)

plt.legend()
plt.tight_layout()
plt.show()

dados = np.column_stack((gain, thd))
np.savetxt(
    "dados_amplificador_thdxgain_original.csv",
    dados,
    delimiter=",",
    header="Gain,THD",
    comments=""
)

Sr = []
net_editor_SR = SpiceEditor(asc)
net_editor_SR.set_component_value("V6", "PULSE(-1 1 0 1n 1n 10m 20m)")
net_editor_SR.add_instruction(".tran 1")

net_editor_SR.add_instruction(".meas TRAN Vmax_sr MAX V(vout) FROM 770m TO 780m")
net_editor_SR.add_instruction(".meas TRAN Vmin_sr MIN V(vout) FROM 770m TO 780m")
net_editor_SR.add_instruction(".meas TRAN V10_sr PARAM Vmin_sr + 0.1*(Vmax_sr - Vmin_sr)")
net_editor_SR.add_instruction(".meas TRAN V90_sr PARAM Vmin_sr + 0.9*(Vmax_sr - Vmin_sr)")
net_editor_SR.add_instruction(".meas TRAN t10_sr WHEN V(vout)={V10_sr} RISE=1 TD=770m")
net_editor_SR.add_instruction(".meas TRAN t90_sr WHEN V(vout)={V90_sr} RISE=1 TD=770m")
net_editor_SR.add_instruction(".meas TRAN SR_sr PARAM (V90_sr - V10_sr)/(t90_sr - t10_sr)")
net_editor_SR.add_instruction(".meas TRAN SRu_sr PARAM SR_sr/1e6")

net_editor_SR.save_netlist(r"C:\Users\Carlos Eduardo\Documents\LTspice\debug_sr.cir")

cores = ['blue', 'red', 'green']
labels = ['Av = 5', 'Av = 10', 'Av = 16']

xis_total = []
Sr_total = []

for j, Rx in enumerate(RD):
    xis = []
    Sr = []

    net_editor_SR.set_component_value("Rd1e", str(Rx))
    net_editor_SR.set_component_value("Rd1d", str(Rx))

    for val in Is:
        net_editor_SR.set_component_value("I1", str(val))

        raw, log = runner.run_now(net_editor_SR)
        log = LTSpiceLogReader(log)

        print(log.get_measure_names())

        sr_u = float(log.dataset["sru_sr"][0])

        Sr.append(sr_u)
        xis.append(val * 1000)

    xis_total.append(xis)
    Sr_total.append(Sr)

    plt.plot(
        xis,
        Sr,
        linestyle='-',
        linewidth=2,
        color=cores[j],
        label=labels[j]
    )

plt.title('Slew Rate vs Corrente da Fonte', fontsize=14)
plt.xlabel('Corrente da Fonte Is (mA)', fontsize=12)
plt.ylabel('Slew Rate (V/us)', fontsize=12)

ax = plt.gca()

xmin = min(min(curva) for curva in xis_total)
xmax = max(max(curva) for curva in xis_total)
ymin = min(min(curva) for curva in Sr_total)
ymax = max(max(curva) for curva in Sr_total)

ax.set_xlim(xmin, xmax)
ax.set_ylim(ymin, ymax + 0.1)

plt.minorticks_on()
plt.grid(True, which='major', linestyle='-', linewidth=0.7)
plt.grid(True, which='minor', linestyle=':', linewidth=0.5)

plt.legend()
plt.tight_layout()
plt.show()