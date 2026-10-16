from PyLTSpice import SimRunner, SpiceEditor, RawRead
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from matplotlib.ticker import AutoMinorLocator


# =======================================================
# Função para encontrar a frequência de corte (-3dB)
# =======================================================
def encontrar_freq_corte(raw_ac):
    raw = RawRead(raw_ac)

    v = raw.get_trace("V(OUT)").data
    freq = raw.get_trace("frequency").data

    # magnitude em dB
    vout = 20 * np.log10(np.abs(v))

    # ganho máximo (ignorando DC)
    indice_vmax = np.argmax(vout[1:]) + 1
    max_gain_db = vout[indice_vmax]

    # nível de corte
    vcorte = max_gain_db - 3

    # busca somente na região após o máximo
    indices_corte = np.where(vout[indice_vmax:] < vcorte)[0]
    if len(indices_corte) == 0:
        raise ValueError("Frequência de corte não encontrada. Aumente o sweep.")

    indice_corte = indices_corte[0] + indice_vmax
    f_corte = freq[indice_corte]

    return f_corte, max_gain_db


# =======================================================
# Configurações
# =======================================================
ltspice_exe_path = r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe"
runner = SimRunner(output_folder='./temp', simulator=ltspice_exe_path)

netlist_path = "1E.asc"

V_pol_RC = 5.0
VT = 26e-3

# Varredura da corrente de cauda
correntes_Is = np.arange(1e-3, 10e-3 + 0.5e-3, 0.5e-3)

# =======================================================
# Simulação
# =======================================================
dados_resultados = []
RG = 54.9e3
#target_gains = np.arange(2,10 + 2, 2)
target_gains= [2,3,6,8,10,15,20]

for Av_target in target_gains:
    for Is in correntes_Is:

        Ic = Is / 2
        R_calc = V_pol_RC / Ic

        # ============================
        # A) SIMULAÇÃO preliminar (.op)
        # ============================
        re = VT / Ic
        RE_guess = (R_calc / (2 * Av_target)) - re - (RG / (2 * 550))

        if RE_guess <= 0:
            RE_guess = 50.0

        net_pre = SpiceEditor(netlist_path)
        net_pre.set_component_value("I1", f"{Is}")
        net_pre.set_component_value("R1", str(R_calc))
        net_pre.set_component_value("R2", str(R_calc))
        net_pre.set_component_value("R3", str(RE_guess))
        net_pre.set_component_value("R4", str(RE_guess))
        net_pre.set_component_value("R5", str(RG))
        net_pre.set_component_value("RG1", str(RG))
        net_pre.add_instruction(".op")

        raw_path, log_path = runner.run_now(net_pre)
        LTR = RawRead(raw_path)

        ib = abs(LTR.get_trace("ib(Q1)").get_wave(0)[0])
        ic = abs(LTR.get_trace("I(R1)").get_wave(0)[0])
        beta = ic / ib if ib != 0 else 100

        # ============================
        # B) RE real com beta medido
        # ============================
        RE_calc = (R_calc / (2 * Av_target)) - re - (RG / (2 * beta))
        if RE_calc <= 0:
            continue

        # ============================
        # C) Simulação final (.ac)
        # ============================
        net = SpiceEditor(netlist_path)
        net.set_component_value("I1", f"{Is}")
        net.set_component_value("R1", str(R_calc))
        net.set_component_value("R2", str(R_calc))
        net.set_component_value("R3", str(RE_calc))
        net.set_component_value("R4", str(RE_calc))
        net.set_component_value("R5", str(RG))
        net.set_component_value("RG1", str(RG))
        net.set_component_value("V3", "AC 1")
        net.add_instruction(".ac dec 800 10 10Meg")

        raw_ac, log_ac = runner.run_now(net)
        f_corte, max_gain = encontrar_freq_corte(raw_ac)

        dados_resultados.append((Is * 1e3, f_corte / 1e3, Av_target))

        print(
            f"Is={Is*1e3:.2f}mA | RC={R_calc:.1f}Ω | RE={RE_calc:.1f}Ω -> "
            f"Fh={f_corte/1e3:.2f}kHz | Gain={max_gain:.2f}dB | beta={beta:.1f}"
        )

# =======================================================
# Plotagem
# =======================================================
plt.figure(figsize=(8, 5))

curvas = {}
for Is_mA, freq_kHz, Av in dados_resultados:
    curvas.setdefault(Av, {"Is": [], "freq": []})
    curvas[Av]["Is"].append(Is_mA)
    curvas[Av]["freq"].append(freq_kHz)

for Av in curvas:
    plt.plot(curvas[Av]["Is"], curvas[Av]["freq"],
             linewidth=2, marker='.', label=f"Av={Av}")

plt.title("Fh vs Is")
plt.xlabel("Is (mA)")
plt.xlim (0,10)
plt.ylabel("Frequência de Corte superior (kHz)")
plt.ylim(100,1600)
#subdivsões
ax = plt.gca()
ax.xaxis.set_minor_locator(AutoMinorLocator(4))  
ax.yaxis.set_minor_locator(AutoMinorLocator(2))
ax.grid(True, which='major', linestyle='-', linewidth=1.0, alpha=1)
ax.grid(True, which='minor', linestyle='--', linewidth=0.5, alpha=0.5)


plt.legend()
plt.tight_layout()

plt.show()
