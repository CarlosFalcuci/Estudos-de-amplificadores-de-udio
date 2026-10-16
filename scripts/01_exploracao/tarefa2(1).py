from PyLTSpice import SimRunner, SpiceEditor, LTSpiceLogReader
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# CAMINHOS
# ============================================================

lts = r"C:\Users\Carlos Eduardo\AppData\Local\Programs\ADI\LTspice\LTspice.exe"
asc = r"C:\Users\Carlos Eduardo\Documents\LTspice\ConfiguracaoCFP.asc"

csv_saida = r"C:\Users\Carlos Eduardo\Documents\Workspace_VSCODE\Pesquisa\thd_vs_av_correntes.csv"
fig_saida = r"C:\Users\Carlos Eduardo\Documents\Workspace_VSCODE\Pesquisa\thd_vs_av_comparacao.png"

runner = SimRunner(
    output_folder="./teste_py_lt",
    simulator=lts
)

# ============================================================
# CONFIGURAÇÕES DA VARREDURA
# ============================================================

correntes_mA = [
    0.4,
    0.6,
    0.8,
    1.0,
    1.2,
    1.5,
    2.0,
    2.5,
    3.0,
    3.5,
    4.0,
    10.0
]

Av_inicio = 7
Av_fim = 17

n_pontos = 50

# folga para garantir que a simulação realmente cubra um pouco além de 7 até 17
folga = 0.10

resultados = []

# ============================================================
# LOOP PRINCIPAL
# ============================================================

plt.figure(figsize=(9, 6))

for I_mA in correntes_mA:

    I = I_mA * 1e-3

    # No seu código original:
    # Rd = 20 / (I/2)
    Rd = 20 / (I / 2)

    # Pela aproximação:
    # Av ≈ Rd/(2*Rs)
    #
    # Rs para Av baixo é maior.
    # Rs para Av alto é menor.

    Rs_Av7 = Rd / (2 * Av_inicio)
    Rs_Av17 = Rd / (2 * Av_fim)

    Rs_max = Rs_Av7 * (1 + folga)
    Rs_min = Rs_Av17 * (1 - folga)

    Rs_values = np.linspace(Rs_max, Rs_min, n_pontos)

    x_av = []
    y_thd = []

    print("\n====================================")
    print(f"I = {I_mA:.3f} mA")
    print(f"Rd = {Rd:.3f} ohm")
    print(f"Rs aproximado para Av=7  -> {Rs_Av7:.3f} ohm")
    print(f"Rs aproximado para Av=17 -> {Rs_Av17:.3f} ohm")
    print(f"Varredura Rs: {Rs_max:.3f} até {Rs_min:.3f} ohm")
    print("====================================")

    for Rs in Rs_values:

        net = SpiceEditor(asc)

        net.set_component_value("I1", f"{I:.12g}")

        net.set_component_value("Rd1e", f"{Rd:.12g}")
        net.set_component_value("Rd1d", f"{Rd:.12g}")

        net.set_component_value("Rs1e", f"{Rs:.12g}")
        net.set_component_value("Rs1d", f"{Rs:.12g}")

        raw, log = runner.run_now(net)
        log = LTSpiceLogReader(log)

        thd = log.fourier["V(vout)"][0].thd

        vpp = float(log.dataset["vpp"][0])
        av = vpp / 2

        x_av.append(av)
        y_thd.append(thd)

        resultados.append({
            "I_mA": I_mA,
            "I_A": I,
            "Rd_ohm": Rd,
            "Rs_ohm": Rs,
            "Av_aproximado_teorico": Rd / (2 * Rs),
            "Av_medido_Vpp_sobre_2": av,
            "THD_percent": thd
        })

        print(
            f"I = {I_mA:6.3f} mA | "
            f"Rs = {Rs:10.3f} ohm | "
            f"Av_teor = {Rd/(2*Rs):8.3f} | "
            f"Av_med = {av:8.3f} | "
            f"THD = {thd:8.5f} %"
        )

    # ordena por ganho medido antes de plotar
    dados_curva = pd.DataFrame({
        "Av": x_av,
        "THD": y_thd
    }).sort_values("Av")

    plt.plot(
        dados_curva["Av"],
        dados_curva["THD"],
        marker="o",
        linestyle="-",
        label=f"I = {I_mA:g} mA"
    )

# ============================================================
# SALVAR CSV
# ============================================================

df_saida = pd.DataFrame(resultados)

df_saida.to_csv(
    csv_saida,
    index=False,
    encoding="utf-8-sig"
)

print(f"\nCSV salvo em: {csv_saida}")

# ============================================================
# PLOT FINAL
# ============================================================

plt.title("THD vs AV para diferentes correntes")
plt.xlabel("AV = Vpp/2")
plt.ylabel("THD (%)")
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.savefig(fig_saida, dpi=600, bbox_inches="tight")
plt.show()

print(f"Figura salva em: {fig_saida}")